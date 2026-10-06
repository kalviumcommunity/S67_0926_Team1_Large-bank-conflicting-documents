from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import UploadFile

from app.config import load_settings
from app.embeddings.embedder import OllamaEmbedder
from app.ingestion.pipeline import ingest_document
from app.services.ingestion_config import load_ingestion_settings
from app.services.manifest_service import (
    ManifestStore,
    file_sha256,
    is_stale,
    manifest_key,
)
from app.vectorstore.indexer import DocumentIndexer
from app.vectorstore.qdrant import QdrantVectorStore

UPLOAD_DIR = "data/uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class IngestionServiceError(RuntimeError):
    pass


class UnsupportedDocumentError(IngestionServiceError):
    pass


class InvalidDocumentMetadataError(IngestionServiceError):
    pass


class DocumentNotFoundError(IngestionServiceError):
    pass


class DocumentRetryUnavailableError(IngestionServiceError):
    pass


class DuplicateDocumentError(IngestionServiceError):
    def __init__(self, record):
        super().__init__("document has already been ingested")
        self.record = record


class DocumentProcessingInProgressError(IngestionServiceError):
    def __init__(self, record):
        super().__init__("document is already being processed")
        self.record = record


class DocumentIngestionService:
    def __init__(
        self,
        indexer,
        *,
        manifest=None,
        upload_dir=UPLOAD_DIR,
        max_upload_bytes=None,
        processing_ttl_seconds=None,
    ):
        cfg = load_ingestion_settings()
        self.indexer = indexer
        self.manifest = manifest or ManifestStore(cfg.manifest_db_path)
        self.upload_dir = Path(upload_dir)
        self.max_upload_bytes = (
            max_upload_bytes
            if max_upload_bytes is not None
            else cfg.max_upload_bytes
        )
        self.processing_ttl_seconds = (
            processing_ttl_seconds
            if processing_ttl_seconds is not None
            else cfg.processing_ttl_seconds
        )

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
        temporary_path, digest = self._write_upload(file, filename)
        document_id = str(metadata.get("document_id") or digest[:24])
        metadata["document_id"] = document_id

        key = manifest_key(digest, document_id)
        claimed, existing = self.manifest.claim(
            document_key=key,
            document_id=document_id,
            file_hash=digest,
            filename=filename,
            version=metadata.get("version"),
            metadata=metadata,
            processing_ttl_seconds=self.processing_ttl_seconds,
        )

        if not claimed:
            self._cleanup(temporary_path)
            if existing and existing.get("status") == "indexed":
                raise DuplicateDocumentError(existing)
            raise DocumentProcessingInProgressError(existing or {})

        final = self.upload_dir / f"{digest[:16]}-{filename}"
        try:
            os.replace(temporary_path, final)
            chunks = ingest_document(str(final), metadata=metadata)
            indexed = self.indexer.index_chunks(chunks)
            record = self.manifest.mark_indexed(
                document_key=key,
                stored_path=str(final),
                chunk_count=len(chunks),
                indexed_count=indexed,
            )
            return self._result(record)
        except Exception as exc:
            self.manifest.mark_failed(
                document_key=key,
                stored_path=str(final) if final.exists() else None,
                error_code=exc.__class__.__name__[:80],
                error_message=str(exc)[:500],
            )
            if isinstance(exc, IngestionServiceError):
                raise
            raise IngestionServiceError("document ingestion failed") from exc
        finally:
            self._cleanup(temporary_path)

    async def retry_document(self, document_id: str) -> Dict[str, Any]:
        record = self.manifest.find_latest_by_document_id(document_id)
        if record is None:
            raise DocumentNotFoundError("document was not found")

        status = record.get("status")
        if status == "indexed":
            raise DuplicateDocumentError(record)
        if status == "processing" and not is_stale(
            record.get("updated_at"),
            self.processing_ttl_seconds,
        ):
            raise DocumentProcessingInProgressError(record)
        if status not in {"failed", "processing"}:
            raise DocumentRetryUnavailableError("document is not retryable")

        metadata = dict(record.get("metadata") or {})
        metadata["document_id"] = record.get("document_id")
        if not metadata.get("document_type"):
            raise DocumentRetryUnavailableError(
                "stored compliance metadata is incomplete; upload the document again"
            )

        stored_path = record.get("stored_path")
        if not stored_path:
            raise DocumentRetryUnavailableError(
                "original uploaded file is unavailable; upload the document again"
            )

        source_path = Path(stored_path).resolve()
        upload_root = self.upload_dir.resolve()
        if source_path != upload_root and upload_root not in source_path.parents:
            raise DocumentRetryUnavailableError("stored document location is invalid")
        if not source_path.is_file():
            raise DocumentRetryUnavailableError(
                "original uploaded file is unavailable; upload the document again"
            )

        try:
            digest = file_sha256(str(source_path))
        except OSError as exc:
            raise DocumentRetryUnavailableError(
                "stored document could not be read"
            ) from exc

        if digest != record.get("file_hash"):
            raise DocumentRetryUnavailableError(
                "stored document integrity check failed; upload the document again"
            )

        key = manifest_key(digest, document_id)
        claimed, existing = self.manifest.claim(
            document_key=key,
            document_id=document_id,
            file_hash=digest,
            filename=str(record.get("filename") or source_path.name),
            version=metadata.get("version"),
            metadata=metadata,
            processing_ttl_seconds=self.processing_ttl_seconds,
        )

        if not claimed:
            if existing and existing.get("status") == "indexed":
                raise DuplicateDocumentError(existing)
            raise DocumentProcessingInProgressError(existing or {})

        try:
            chunks = ingest_document(str(source_path), metadata=metadata)
            indexed = self.indexer.index_chunks(chunks)
            finalized = self.manifest.mark_indexed(
                document_key=key,
                stored_path=str(source_path),
                chunk_count=len(chunks),
                indexed_count=indexed,
            )
            return self._result(finalized)
        except Exception as exc:
            self.manifest.mark_failed(
                document_key=key,
                stored_path=str(source_path),
                error_code=exc.__class__.__name__[:80],
                error_message=str(exc)[:500],
            )
            if isinstance(exc, IngestionServiceError):
                raise
            raise IngestionServiceError("document retry failed") from exc

    def list_documents(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Dict[str, Any]]:
        return self.manifest.list_records(
            status=status,
            limit=limit,
            offset=offset,
        )

    def get_status(self, document_id):
        return self.manifest.find_latest_by_document_id(document_id)

    def check_ready(self):
        self.indexer.check_ready()

    @staticmethod
    def _result(record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "document_id": record["document_id"],
            "filename": record["filename"],
            "status": record["status"],
            "chunk_count": record["chunk_count"],
            "indexed_count": record["indexed_count"],
            "sha256": record["file_hash"],
            "ingested_at": record["updated_at"],
        }

    @staticmethod
    def _validate_metadata(metadata):
        from app.validation.document_validator import validate_document_metadata

        normalized = dict(metadata)
        if not normalized.get("document_type"):
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

    def _write_upload(self, file, filename):
        fd, temp_name = tempfile.mkstemp(
            prefix=".uploading-",
            suffix=Path(filename).suffix.lower(),
            dir=self.upload_dir,
        )
        digest = hashlib.sha256()
        total = 0
        try:
            with os.fdopen(fd, "wb") as buffer:
                while True:
                    block = file.file.read(1024 * 1024)
                    if not block:
                        break
                    total += len(block)
                    if total > self.max_upload_bytes:
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
    def _cleanup(path):
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass


def build_default_ingestion_service():
    settings = load_settings()
    embedder = OllamaEmbedder(
        model=settings.ollama_embedding_model,
        base_url=settings.ollama_base_url,
        batch_size=settings.embedding_batch_size,
        timeout=settings.ollama_timeout_seconds,
    )
    store = QdrantVectorStore(
        url=settings.qdrant_url,
        collection_name=settings.qdrant_collection,
        api_key=settings.qdrant_api_key,
    )
    return DocumentIngestionService(DocumentIndexer(embedder, store))
