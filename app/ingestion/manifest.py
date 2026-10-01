from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()

    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def build_manifest(records: Iterable[Dict], report) -> Dict:
    records = list(records)

    document_ids = sorted(
        {
            record["document_id"]
            for record in records
            if record.get("document_id")
        }
    )

    return {
        "schema_version": "1",
        "total_chunks": len(records),
        "document_ids": document_ids,
        "batch": report.as_dict(),
    }


def write_manifest(manifest: Dict, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(
            manifest,
            handle,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")
