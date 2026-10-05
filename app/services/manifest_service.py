from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional


class ManifestStore:
    """Small atomic JSON manifest for idempotent document ingestion."""

    def __init__(self, path: str = "data/ingestion_manifest.json"):
        self.path = Path(path)

    def load(self) -> Dict[str, Dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise RuntimeError("ingestion manifest is corrupted") from exc

        if not isinstance(data, dict):
            raise RuntimeError("ingestion manifest must contain an object")

        return data

    def get(self, document_key: str) -> Optional[Dict[str, Any]]:
        return self.load().get(document_key)

    def save(self, document_key: str, record: Dict[str, Any]) -> None:
        data = self.load()
        data[document_key] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)

        fd, temp_name = tempfile.mkstemp(
            prefix="ingestion_manifest_",
            suffix=".tmp",
            dir=str(self.path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)


def file_sha256(path: str) -> str:
    digest = sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def manifest_key(file_hash: str, document_id: Optional[str] = None) -> str:
    return f"{document_id or '-'}:{file_hash}"
