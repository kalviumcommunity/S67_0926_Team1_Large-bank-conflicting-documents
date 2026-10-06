import hashlib
import io

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.services.ingestion_service import (
    DocumentIngestionService,
    DocumentRetryUnavailableError,
)
from app.services.manifest_service import ManifestStore


class FakeIndexer:
    def __init__(self):
        self.calls = 0

    def index_chunks(self, chunks):
        self.calls += 1
        return len(list(chunks))

    def check_ready(self):
        return None


def upload(name, content):
    return UploadFile(
        file=io.BytesIO(content),
        filename=name,
        headers=Headers({"content-type": "application/octet-stream"}),
    )


def make_service(tmp_path):
    return DocumentIngestionService(
        FakeIndexer(),
        manifest=ManifestStore(str(tmp_path / "manifest.db")),
        upload_dir=str(tmp_path / "uploads"),
        max_upload_bytes=1024,
        processing_ttl_seconds=1800,
    )


@pytest.mark.anyio
async def test_failed_ingestion_can_be_retried_from_stored_source(tmp_path, monkeypatch):
    service = make_service(tmp_path)
    calls = {"count": 0}

    def flaky_ingestion(path, metadata=None):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("transient failure")
        return [
            {
                "chunk_id": "DOC1-p1-c000",
                "document_id": metadata["document_id"],
                "text": "Approval is required.",
                "page": 1,
                "token_count": 4,
            }
        ]

    monkeypatch.setattr(
        "app.services.ingestion_service.ingest_document",
        flaky_ingestion,
    )

    metadata = {
        "document_type": "circular",
        "status": "active",
        "version": "1",
    }

    with pytest.raises(Exception):
        await service.process_document(upload("rule.pdf", b"same content"), metadata=metadata)

    first = service.manifest.load()
    record = next(iter(first.values()))
    assert record["status"] == "failed"
    assert record["metadata"]["document_type"] == "circular"

    retried = await service.retry_document(record["document_id"])

    assert retried["status"] == "indexed"
    assert service.manifest.find_latest_by_document_id(record["document_id"])["status"] == "indexed"
    assert service.indexer.calls == 1


@pytest.mark.anyio
async def test_retry_rejects_tampered_source(tmp_path, monkeypatch):
    service = make_service(tmp_path)
    monkeypatch.setattr(
        "app.services.ingestion_service.ingest_document",
        lambda path, metadata=None: (_ for _ in ()).throw(RuntimeError("failure")),
    )

    with pytest.raises(Exception):
        await service.process_document(
            upload("rule.pdf", b"original content"),
            metadata={"document_type": "circular", "status": "active", "version": "1"},
        )

    record = next(iter(service.manifest.load().values()))
    source = record["stored_path"]
    with open(source, "wb") as handle:
        handle.write(b"tampered")

    with pytest.raises(DocumentRetryUnavailableError, match="integrity check"):
        await service.retry_document(record["document_id"])


@pytest.mark.anyio
async def test_retry_rejects_missing_source(tmp_path):
    service = make_service(tmp_path)
    content = b"stored content"
    digest = hashlib.sha256(content).hexdigest()
    key = f"DOC-1:{digest}"
    service.manifest.claim(
        document_key=key,
        document_id="DOC-1",
        file_hash=digest,
        filename="rule.pdf",
        version="1",
        metadata={
            "document_id": "DOC-1",
            "document_type": "circular",
            "status": "active",
            "version": "1",
        },
        processing_ttl_seconds=1800,
    )
    service.manifest.mark_failed(
        document_key=key,
        stored_path=str(tmp_path / "uploads" / "missing.pdf"),
        error_code="RuntimeError",
        error_message="failure",
    )

    with pytest.raises(DocumentRetryUnavailableError, match="unavailable"):
        await service.retry_document("DOC-1")
