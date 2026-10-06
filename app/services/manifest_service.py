from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional


class ManifestStore:
    """
    Durable, concurrency-safe ingestion state.

    SQLite is used instead of a JSON read/modify/write file so concurrent
    uploads cannot lose state or both claim the same document.
    """

    def __init__(
        self,
        path: str = "data/ingestion_manifest.db",
        *,
        legacy_json_path: str = "data/ingestion_manifest.json",
    ):
        self.path = Path(path)
        self.legacy_json_path = Path(legacy_json_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()
        self._migrate_legacy_json()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=30,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 30000")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ingestion_manifest (
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
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            columns = {
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(ingestion_manifest)"
                ).fetchall()
            }
            if "metadata_json" not in columns:
                connection.execute(
                    """
                    ALTER TABLE ingestion_manifest
                    ADD COLUMN metadata_json TEXT NOT NULL DEFAULT '{}'
                    """
                )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_ingestion_document_id
                ON ingestion_manifest(document_id)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_ingestion_status_updated
                ON ingestion_manifest(status, updated_at DESC)
                """
            )

    def _migrate_legacy_json(self) -> None:
        if not self.legacy_json_path.exists():
            return

        with self._connect() as connection:
            count = connection.execute(
                "SELECT COUNT(*) AS count FROM ingestion_manifest"
            ).fetchone()["count"]

        if count:
            return

        try:
            with self.legacy_json_path.open("r", encoding="utf-8") as handle:
                legacy = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return

        if not isinstance(legacy, dict):
            return

        for key, record in legacy.items():
            if not isinstance(record, dict):
                continue

            file_hash = str(record.get("sha256") or "")
            document_id = str(record.get("document_id") or "")
            if not file_hash or not document_id:
                continue

            self.save(
                document_key=str(key),
                record={
                    **record,
                    "status": record.get("status", "failed"),
                },
            )

    @staticmethod
    def _decode_row(row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        record = dict(row)
        raw_metadata = record.pop("metadata_json", "{}")
        try:
            metadata = json.loads(raw_metadata) if raw_metadata else {}
        except (TypeError, json.JSONDecodeError):
            metadata = {}
        record["metadata"] = metadata if isinstance(metadata, dict) else {}
        return record

    def load(self) -> Dict[str, Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM ingestion_manifest
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return {
            row["document_key"]: self._decode_row(row)
            for row in rows
        }

    def get(self, document_key: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM ingestion_manifest
                WHERE document_key = ?
                """,
                (document_key,),
            ).fetchone()

        return self._decode_row(row) if row else None

    def find_latest_by_document_id(
        self,
        document_id: str,
    ) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM ingestion_manifest
                WHERE document_id = ?
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (document_id,),
            ).fetchone()

        return self._decode_row(row) if row else None

    def list_records(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Dict[str, Any]]:
        if limit <= 0 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        if offset < 0:
            raise ValueError("offset must be non-negative")

        query = "SELECT * FROM ingestion_manifest"
        params: list[Any] = []

        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._decode_row(row) for row in rows]

    def claim(
        self,
        *,
        document_key: str,
        document_id: str,
        file_hash: str,
        filename: str,
        version: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
        processing_ttl_seconds: int = 1800,
    ) -> tuple[bool, Optional[Dict[str, Any]]]:
        """Atomically claim a document for processing."""
        now = utc_now()
        metadata_json = _serialize_metadata(metadata)

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")

            by_key = connection.execute(
                """
                SELECT *
                FROM ingestion_manifest
                WHERE document_key = ?
                """,
                (document_key,),
            ).fetchone()

            by_hash = connection.execute(
                """
                SELECT *
                FROM ingestion_manifest
                WHERE file_hash = ?
                """,
                (file_hash,),
            ).fetchone()

            existing = by_key or by_hash

            if existing:
                record = self._decode_row(existing)
                status = record["status"]

                if status == "indexed":
                    connection.execute("COMMIT")
                    return False, record

                if status == "processing" and not is_stale(
                    record.get("updated_at"),
                    processing_ttl_seconds,
                ):
                    connection.execute("COMMIT")
                    return False, record

                connection.execute(
                    """
                    UPDATE ingestion_manifest
                    SET document_key = ?,
                        document_id = ?,
                        file_hash = ?,
                        filename = ?,
                        version = ?,
                        status = 'processing',
                        stored_path = NULL,
                        chunk_count = NULL,
                        indexed_count = NULL,
                        error_code = NULL,
                        error_message = NULL,
                        metadata_json = ?,
                        updated_at = ?
                    WHERE document_key = ?
                    """,
                    (
                        document_key,
                        document_id,
                        file_hash,
                        filename,
                        version,
                        metadata_json,
                        now,
                        record["document_key"],
                    ),
                )
                connection.execute("COMMIT")
                return True, None

            connection.execute(
                """
                INSERT INTO ingestion_manifest (
                    document_key,
                    document_id,
                    file_hash,
                    filename,
                    version,
                    status,
                    metadata_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, 'processing', ?, ?, ?)
                """,
                (
                    document_key,
                    document_id,
                    file_hash,
                    filename,
                    version,
                    metadata_json,
                    now,
                    now,
                ),
            )
            connection.execute("COMMIT")

        return True, None

    def mark_indexed(
        self,
        *,
        document_key: str,
        stored_path: str,
        chunk_count: int,
        indexed_count: int,
    ) -> Dict[str, Any]:
        now = utc_now()

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE ingestion_manifest
                SET status = 'indexed',
                    stored_path = ?,
                    chunk_count = ?,
                    indexed_count = ?,
                    error_code = NULL,
                    error_message = NULL,
                    updated_at = ?
                WHERE document_key = ?
                """,
                (
                    stored_path,
                    chunk_count,
                    indexed_count,
                    now,
                    document_key,
                ),
            )

        record = self.get(document_key)
        if record is None:
            raise RuntimeError("ingestion manifest disappeared during finalization")
        return record

    def mark_failed(
        self,
        *,
        document_key: str,
        stored_path: Optional[str],
        error_code: str,
        error_message: str,
    ) -> Dict[str, Any]:
        now = utc_now()

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE ingestion_manifest
                SET status = 'failed',
                    stored_path = ?,
                    error_code = ?,
                    error_message = ?,
                    updated_at = ?
                WHERE document_key = ?
                """,
                (
                    stored_path,
                    error_code,
                    error_message,
                    now,
                    document_key,
                ),
            )

        record = self.get(document_key)
        if record is None:
            raise RuntimeError("ingestion manifest disappeared during failure recording")
        return record

    def save(self, document_key: str, record: Dict[str, Any]) -> None:
        now = record.get("updated_at") or utc_now()
        metadata_json = _serialize_metadata(record.get("metadata"))

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO ingestion_manifest (
                    document_key,
                    document_id,
                    file_hash,
                    filename,
                    version,
                    status,
                    stored_path,
                    chunk_count,
                    indexed_count,
                    error_code,
                    error_message,
                    metadata_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_key) DO UPDATE SET
                    document_id = excluded.document_id,
                    file_hash = excluded.file_hash,
                    filename = excluded.filename,
                    version = excluded.version,
                    status = excluded.status,
                    stored_path = excluded.stored_path,
                    chunk_count = excluded.chunk_count,
                    indexed_count = excluded.indexed_count,
                    error_code = excluded.error_code,
                    error_message = excluded.error_message,
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at
                """,
                (
                    document_key,
                    str(record.get("document_id") or ""),
                    str(record.get("sha256") or ""),
                    record.get("filename"),
                    record.get("version"),
                    record.get("status", "failed"),
                    record.get("stored_path"),
                    record.get("chunk_count"),
                    record.get("indexed_count"),
                    record.get("error_code"),
                    record.get("error_message"),
                    metadata_json,
                    record.get("created_at") or now,
                    now,
                ),
            )


def _serialize_metadata(metadata: Optional[Dict[str, Any]]) -> str:
    if not metadata:
        return "{}"
    try:
        value = json.dumps(
            dict(metadata),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("ingestion metadata must be JSON serializable") from exc
    return value


def file_sha256(path: str) -> str:
    digest = sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def manifest_key(
    file_hash: str,
    document_id: Optional[str] = None,
) -> str:
    return f"{document_id or '-'}:{file_hash}"


def is_stale(
    updated_at: Optional[str],
    ttl_seconds: int,
) -> bool:
    if not updated_at:
        return True

    try:
        timestamp = datetime.fromisoformat(updated_at)
    except ValueError:
        return True

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    age = datetime.now(timezone.utc) - timestamp
    return age.total_seconds() >= ttl_seconds
