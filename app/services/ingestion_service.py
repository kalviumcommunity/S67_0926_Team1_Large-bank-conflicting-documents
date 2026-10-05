from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import UploadFile

from app.config import load_settings
from app.embeddings.embedder import OpenAIEmbedder
from app.ingestion.pipeline import ingest_document
from app.services.ingestion_config import load_ingestion_settings
from app.services.manifest_service import (
    ManifestStore,
    manifest_key,
)
from app.vectorstore.indexer import DocumentIndexer
from app.vectorstore.qdrant import QdrantVectorStore


UPLOAD_DIR = "data/uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class IngestionServiceError(RuntimeError):
    """Base error for production document ingestion."""


class UnsupportedDocumentError(IngestionServiceError):
    pass


class InvalidDocumentMetadataError(IngestionServiceError):
    pass


class DuplicateDocumentError(IngestionServiceError):
    def __init__(self, record: Dict[str, Any]):
        super().__init__("document has already been ingested")
        self.record = record


class DocumentProcessingInProgressError(IngestionServiceError):
    def __init__(self, record: Dict[str, Any]):
        super().__init__("document is already being processed")
        self.record = record


class DocumentIngestionService:
    """Coordinates validation, durable claim state, ingestion, and indexing."""

    def __init__(
        self,
        indexer: DocumentIndexer,
        *,
        manifest: Optional[ManifestStore] = None,
        upload_dir: str = UPLOAD_DIR,
        max_upload_bytes: Optional[int] = None,
        processing_ttl_seconds: Optional[int] = None,
    ):
        ingestion_settings = load_ingestion_settings()

        self.indexer = indexer
        self.manifest = manifest or ManifestStore(
            ingestion_settings.manifest_db_path
        )
        self.upload_dir = Path(upload_dir)
        self.max_upload_bytes = (
            max_upload_bytes
            if max_upload_bytes is not None
            else ingestion_settings.max_upload_bytes
        )
        self.processing_ttl_seconds = (
            processing_ttl_seconds
            if processing_ttl_seconds is not None
            else ingestion_settings.processing_ttl_seconds
        )

        if self.max_upload_bytes <= 0:
            raise ValueError("max_upload_bytes must be positive")
        if self.processing_ttl_seconds <= 0:
            raise ValueError("processing_ttl_seconds must be positive")

    async def process_document(
        self,
        file: UploadFile,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        filename = Path(file.filename or "").name
        extension = Path(filename).suffix.lower()

        if not filename:
            raise UnsupportedDocumentError("a filename is required")

        if extension not in ALLOWED_EXTENSIONS:
            raise UnsupportedDocumentError(
                f"unsupported file type: {extension or '<none>'}"
            )

        metadata = self._validate_metadata(metadata or {})

        self.upload_dir.mkdir(parents=True, exist_ok=True)

        temporary_path, digest = self._write_upload(
            file=file,
            filename=filename,
        )

        document_id = str(
            metadata.get("document_id")
            or digest[:24]
        )
        metadata["document_id"] = document_id

        document_key = manifest_key(
            file_hash=digest,
            document_id=document_id,
        )

        claimed, existing = self.manifest.claim(
            document_key=document_key,
            document_id=document_id,
            file_hash=digest,
            filename=filename,
            version=metadata.get("version"),
            processing_ttl_seconds=self.processing_ttl_seconds,
        )

        if not claimed:
            self._cleanup(temporary_path)

            if existing and existing.get("status") == "indexed":
                raise DuplicateDocumentError(existing)

            raise DocumentProcessingInProgressError(existing or {})

        final_path = self.upload_dir / f"{digest[:16]}-{filename}"

        try:
            os.replace(temporary_path, final_path)

            chunks = ingest_document(
                str(final_path),
                metadata=metadata,
            )

            indexed_count = self.indexer.index_chunks(chunks)

            record = self.manifest.mark_indexed(
                document_key=document_key,
                stored_path=str(final_path),
                chunk_count=len(chunks),
                indexed_count=indexed_count,
            )

            return {
                "document_id": document_id,
                "filename": filename,
                "status": "indexed",
                "chunk_count": len(chunks),
                "indexed_count": indexed_count,
                "sha256": digest,
                "ingested_at": record["updated_at"],
            }

        except Exception as exc:
            error_code = _error_code(exc)

            self.manifest.mark_failed(
                document_key=document_key,
                stored_path=str(final_path) if final_path.exists() else None,
                error_code=error_code,
                error_message=str(exc)[:500],
            )

            if isinstance(exc, IngestionServiceError):
                raise

            raise IngestionServiceError(
                "document ingestion failed"
            ) from exc

        finally:
            self._cleanup(temporary_path)

    def get_status(self, document_id: str) -> Optional[Dict[str, Any]]:
        return self.manifest.find_latest_by_document_id(document_id)

    def check_ready(self) -> None:
        self.indexer.check_ready()

    @staticmethod
    def _validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        from app.validation.document_validator import validate_document_metadata

        normalized = dict(metadata)

        document_type = normalized.get("document_type")
        if not document_type:
            raise InvalidDocumentMetadataError(
                "document_type is required for compliance ingestion"
            )

        try:
            validate_document_metadata(normalized)
        except Exception as exc:
            raise InvalidDocumentMetadataError(
                "document metadata failed validation"
            ) from exc

        return normalized

    def _write_upload(
        self,
        *,
        file: UploadFile,
        filename: str,
    ):
        fd, temp_name = tempfile.mkstemp(
            prefix=".uploading-",
            suffix=Path(filename).suffix.lower(),
            dir=self.upload_dir,
        )

        digest = hashlib.sha256()
        total_bytes = 0

        try:
            with os.fdopen(fd, "wb") as buffer:
                while True:
                    block = file.file.read(1024 * 1024)
                    if not block:
                        break

                    total_bytes += len(block)
                    if total_bytes > self.max_upload_bytes:
                        raise UnsupportedDocumentError(
                            "file exceeds the maximum configured upload size"
                        )

                    digest.update(block)
                    buffer.write(block)

                buffer.flush()
                os.fsync(buffer.fileno())

            return Path(temp_name), digest.hexdigest()

        except Exception:
            self._cleanup(Path(temp_name))
            raise

    @staticmethod
    def _cleanup(path: Path) -> None:
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass


def _error_code(error: Exception) -> str:
    name = error.__class__.__name__
    return name[:80]


def build_default_ingestion_service() -> DocumentIngestionService:
    settings = load_settings()

    embedder = OpenAIEmbedder(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
        batch_size=settings.embedding_batch_size,
    )

    vector_store = QdrantVectorStore(
        url=settings.qdrant_url,
        collection_name=settings.qdrant_collection,
        api_key=settings.qdrant_api_key,
        vector_size=settings.embedding_dimensions,
    )

    indexer = DocumentIndexer(
        embedder,
        vector_store,
    )

    return DocumentIngestionService(indexer)
