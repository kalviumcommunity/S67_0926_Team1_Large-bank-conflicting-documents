from __future__ import annotations

import os
from dataclasses import dataclass


def _int_env(name: str, default: int, minimum: int = 0) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if value < minimum:
        raise RuntimeError(f"{name} must be >= {minimum}")
    return value


@dataclass(frozen=True)
class IngestionSettings:
    max_upload_bytes: int
    manifest_db_path: str
    processing_ttl_seconds: int


def load_ingestion_settings() -> IngestionSettings:
    return IngestionSettings(
        max_upload_bytes=_int_env(
            "MAX_UPLOAD_BYTES",
            25 * 1024 * 1024,
            minimum=1,
        ),
        manifest_db_path=os.getenv(
            "INGESTION_MANIFEST_DB",
            "data/ingestion_manifest.db",
        ).strip(),
        processing_ttl_seconds=_int_env(
            "INGESTION_PROCESSING_TTL_SECONDS",
            30 * 60,
            minimum=30,
        ),
    )
