from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import UploadFile

from app.config import load_settings
from app.embeddings.embedder import OpenAIEmbedder
from app.ingestion.pipeline import ingest_document
from app.services.manifest_service import ManifestStore, file_sha256, manifest_key, utc_now
from app.services.storage_service import save_file
from app.vectorstore.indexer import DocumentIndexer
from app.vectorstore.qdrant import QdrantVectorStore


UPLOAD_DIR = "data/uploads"
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class IngestionServiceError(RuntimeError):
    """Base error for production document ingestion."""


class UnsupportedDocumentError(IngestionServiceError):
    pass


class DuplicateDocumentError(IngestionServiceError):
    def __init__(self, record: Dict[str, Any]):
        super().__init__("document has already been ingested")
        self.record = record


class DocumentIngestionService:
    """Coordinates storage, validation, chunking, embeddings, and Qdrant indexing."""

    def __init__(
        self,
        indexer: DocumentIndexer,
        *,
        manifest: Optional[ManifestStore] = None,
        upload_dir: str = UPLOAD_DIR,
        max_upload_bytes: int = MAX_UPLOAD_BYTES,
    ):
        self.indexer = indexer
        self.manifest = manifest or ManifestStore()
        self.upload_dir = Path(upload_dir)
        self.max_upload_bytes = max_upload_bytes

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
                f"unsupported file type: {extension or '<none>'}; "
                f"supported types: {sorted(ALLOWED_EXTENSIONS)}"
            )

        metadata = dict(metadata or {})
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        temporary_path = self.upload_dir / f".uploading-{filename}"

        try:
            total_bytes = 0
            with temporary_path.open("wb") as buffer:
                while True:
                    block = await file.read(1024 * 1024)
                    if not block:
                        break
                    total_bytes += len(block)
                    if total_bytes > self.max_upload_bytes:
                        raise UnsupportedDocumentError(
                            f"file exceeds maximum size of {self.max_upload_bytes} bytes"
                        )
                    buffer.write(block)

            digest = file_sha256(str(temporary_path))
            document_id = str(metadata.get("document_id") or digest[:24])
            metadata["document_id"] = document_id

            key = manifest_key(digest, document_id)
            existing = self.manifest.get(key)
            if existing and existing.get("status") == "indexed":
                raise DuplicateDocumentError(existing)

            final_path = self.upload_dir / f"{digest[:16]}-{filename}"
            os.replace(temporary_path, final_path)

            chunks = ingest_document(
                str(final_path),
                metadata=metadata,
            )
            indexed_count = self.indexer.index_chunks(chunks)

            record = {
                "document_id": document_id,
                "filename": filename,
                "stored_path": str(final_path),
                "sha256": digest,
                "status": "indexed",
                "chunk_count": len(chunks),
                "indexed_count": indexed_count,
                "ingested_at": utc_now(),
            }
            self.manifest.save(key, record)

            return {
                "document_id": document_id,
                "filename": filename,
                "status": "indexed",
                "chunk_count": len(chunks),
                "indexed_count": indexed_count,
                "sha256": digest,
            }

        except DuplicateDocumentError:
            raise
        except Exception as exc:
            if isinstance(exc, IngestionServiceError):
                raise
            raise IngestionServiceError("document ingestion failed") from exc
        finally:
            if temporary_path.exists():
                temporary_path.unlink()


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
    indexer = DocumentIndexer(embedder, vector_store)

    return DocumentIngestionService(indexer)
