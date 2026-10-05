import io

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.services.ingestion_service import (
    DocumentIngestionService,
    DuplicateDocumentError,
    InvalidDocumentMetadataError,
    UnsupportedDocumentError,
)
from app.services.manifest_service import ManifestStore


class FakeIndexer:
    def __init__(self):
        self.chunks = []

    def index_chunks(self, chunks):
        chunks = list(chunks)
        self.chunks.extend(chunks)
        return len(chunks)

    def check_ready(self):
        return None


def upload(name, content):
    return UploadFile(
        file=io.BytesIO(content),
        filename=name,
        headers=Headers(
            {"content-type": "application/octet-stream"}
        ),
    )


def make_service(tmp_path):
    return DocumentIngestionService(
        FakeIndexer(),
        manifest=ManifestStore(
            str(tmp_path / "manifest.db")
        ),
        upload_dir=str(tmp_path / "uploads"),
        max_upload_bytes=1024,
        processing_ttl_seconds=1800,
    )


@pytest.mark.anyio
async def test_upload_creates_indexed_manifest(
    tmp_path,
    monkeypatch,
):
    service = make_service(tmp_path)

    monkeypatch.setattr(
        "app.services.ingestion_service.ingest_document",
        lambda path, metadata=None: [
            {
                "chunk_id": "DOC1-p1-c000",
                "document_id": metadata["document_id"],
                "text": "Approval is required.",
                "page": 1,
                "token_count": 4,
            }
        ],
    )

    response = await service.process_document(
        upload("rule.pdf", b"pdf bytes"),
        metadata={
            "document_type": "circular",
            "status": "active",
            "version": "1",
        },
    )

    assert response["status"] == "indexed"
    assert response["chunk_count"] == 1
    assert response["indexed_count"] == 1
    assert len(response["sha256"]) == 64


@pytest.mark.anyio
async def test_same_content_is_not_indexed_twice(
    tmp_path,
    monkeypatch,
):
    service = make_service(tmp_path)

    monkeypatch.setattr(
        "app.services.ingestion_service.ingest_document",
        lambda path, metadata=None: [
            {
                "chunk_id": "DOC1-p1-c000",
                "document_id": metadata["document_id"],
                "text": "Approval is required.",
                "page": 1,
                "token_count": 4,
            }
        ],
    )

    metadata = {
        "document_type": "circular",
        "status": "active",
        "version": "1",
    }

    await service.process_document(
        upload("rule.pdf", b"same content"),
        metadata=metadata,
    )

    with pytest.raises(DuplicateDocumentError):
        await service.process_document(
            upload("different-name.pdf", b"same content"),
            metadata=metadata,
        )


@pytest.mark.anyio
async def test_missing_document_type_is_rejected(tmp_path):
    service = make_service(tmp_path)

    with pytest.raises(InvalidDocumentMetadataError):
        await service.process_document(
            upload("rule.pdf", b"content"),
            metadata={"status": "active"},
        )


@pytest.mark.anyio
async def test_unsupported_extension_is_rejected(tmp_path):
    service = make_service(tmp_path)

    with pytest.raises(UnsupportedDocumentError):
        await service.process_document(
            upload("rule.txt", b"not supported"),
            metadata={"document_type": "circular"},
        )


@pytest.mark.anyio
async def test_failed_ingestion_is_recorded(
    tmp_path,
    monkeypatch,
):
    service = make_service(tmp_path)

    def broken_ingestion(*args, **kwargs):
        raise RuntimeError("bad document")

    monkeypatch.setattr(
        "app.services.ingestion_service.ingest_document",
        broken_ingestion,
    )

    with pytest.raises(Exception):
        await service.process_document(
            upload("rule.pdf", b"content"),
            metadata={"document_type": "circular"},
        )

    records = service.manifest.load()

    assert len(records) == 1
    record = next(iter(records.values()))
    assert record["status"] == "failed"
    assert record["error_code"]
