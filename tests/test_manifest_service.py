import json
from datetime import datetime, timedelta, timezone

from app.services.manifest_service import ManifestStore, is_stale, manifest_key


def test_manifest_claim_is_atomic_for_same_document(tmp_path):
    store = ManifestStore(str(tmp_path / "manifest.db"))

    key = manifest_key("hash-1", "DOC-1")

    claimed, existing = store.claim(
        document_key=key,
        document_id="DOC-1",
        file_hash="hash-1",
        filename="rule.pdf",
        version="1",
        processing_ttl_seconds=1800,
    )

    assert claimed is True
    assert existing is None

    claimed_again, existing_again = store.claim(
        document_key=key,
        document_id="DOC-1",
        file_hash="hash-1",
        filename="rule.pdf",
        version="1",
        processing_ttl_seconds=1800,
    )

    assert claimed_again is False
    assert existing_again["status"] == "processing"


def test_failed_document_can_be_reclaimed(tmp_path):
    store = ManifestStore(str(tmp_path / "manifest.db"))
    key = manifest_key("hash-2", "DOC-2")

    store.claim(
        document_key=key,
        document_id="DOC-2",
        file_hash="hash-2",
        filename="rule.pdf",
        version="1",
        processing_ttl_seconds=1800,
    )

    store.mark_failed(
        document_key=key,
        stored_path="/tmp/rule.pdf",
        error_code="EmbeddingError",
        error_message="temporary provider failure",
    )

    claimed, existing = store.claim(
        document_key=key,
        document_id="DOC-2",
        file_hash="hash-2",
        filename="rule.pdf",
        version="1",
        processing_ttl_seconds=1800,
    )

    assert claimed is True
    assert existing is None


def test_indexed_document_cannot_be_reclaimed(tmp_path):
    store = ManifestStore(str(tmp_path / "manifest.db"))
    key = manifest_key("hash-3", "DOC-3")

    store.claim(
        document_key=key,
        document_id="DOC-3",
        file_hash="hash-3",
        filename="rule.pdf",
        version="1",
        processing_ttl_seconds=1800,
    )

    store.mark_indexed(
        document_key=key,
        stored_path="/tmp/rule.pdf",
        chunk_count=3,
        indexed_count=3,
    )

    claimed, existing = store.claim(
        document_key=key,
        document_id="DOC-3",
        file_hash="hash-3",
        filename="rule.pdf",
        version="1",
        processing_ttl_seconds=1800,
    )

    assert claimed is False
    assert existing["status"] == "indexed"


def test_stale_processing_claim_can_be_recovered():
    old = (
        datetime.now(timezone.utc) - timedelta(hours=2)
    ).isoformat()

    assert is_stale(old, ttl_seconds=60)
