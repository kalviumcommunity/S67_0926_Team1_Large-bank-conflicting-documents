import sqlite3
from datetime import datetime, timedelta, timezone

from app.services.manifest_service import ManifestStore, is_stale, manifest_key


def test_manifest_persists_compliance_metadata(tmp_path):
    store = ManifestStore(str(tmp_path / "manifest.db"))
    metadata = {
        "document_type": "circular",
        "title": "Approval Rule",
        "status": "active",
        "version": "2",
        "document_id": "DOC-1",
    }
    key = manifest_key("hash-1", "DOC-1")

    claimed, _ = store.claim(
        document_key=key,
        document_id="DOC-1",
        file_hash="hash-1",
        filename="rule.pdf",
        version="2",
        metadata=metadata,
        processing_ttl_seconds=1800,
    )

    assert claimed
    assert store.get(key)["metadata"] == metadata


def test_manifest_migrates_existing_database_without_metadata_column(tmp_path):
    path = tmp_path / "legacy.db"
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE ingestion_manifest (
            document_key TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            filename TEXT,
            version TEXT,
            status TEXT NOT NULL,
            stored_path TEXT,
            chunk_count INTEGER,
            indexed_count INTEGER,
            error_code TEXT,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()

    store = ManifestStore(str(path))
    columns = {
        row[1]
        for row in sqlite3.connect(path).execute(
            "PRAGMA table_info(ingestion_manifest)"
        ).fetchall()
    }
    assert "metadata_json" in columns
    assert store.load() == {}


def test_failed_document_can_be_reclaimed(tmp_path):
    store = ManifestStore(str(tmp_path / "manifest.db"))
    key = manifest_key("hash-2", "DOC-2")

    store.claim(
        document_key=key,
        document_id="DOC-2",
        file_hash="hash-2",
        filename="rule.pdf",
        version="1",
        metadata={"document_type": "circular", "document_id": "DOC-2"},
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
        metadata={"document_type": "circular", "document_id": "DOC-2"},
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
        metadata={"document_type": "circular", "document_id": "DOC-3"},
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
        metadata={"document_type": "circular", "document_id": "DOC-3"},
        processing_ttl_seconds=1800,
    )

    assert claimed is False
    assert existing["status"] == "indexed"


def test_stale_processing_claim_can_be_recovered():
    old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    assert is_stale(old, ttl_seconds=60)


def test_claim_allows_legacy_call_without_metadata(tmp_path):
    store = ManifestStore(str(tmp_path / "manifest.db"))
    key = manifest_key("hash-legacy", "DOC-LEGACY")

    claimed, existing = store.claim(
        document_key=key,
        document_id="DOC-LEGACY",
        file_hash="hash-legacy",
        filename="rule.pdf",
        version="1",
        processing_ttl_seconds=1800,
    )

    assert claimed is True
    assert existing is None
    assert store.get(key)["metadata"] == {}
