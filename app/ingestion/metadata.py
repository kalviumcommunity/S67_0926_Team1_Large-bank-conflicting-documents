from dataclasses import asdict
from typing import Dict, List, Optional

from app.ingestion.chunker import Chunk


def build_chunk_records(
    document: Dict,
    chunks: List[Chunk],
    *,
    document_type: Optional[str] = None,
    title: Optional[str] = None,
    issue_date: Optional[str] = None,
    effective_date: Optional[str] = None,
    status: str = "unknown",
    version: Optional[str] = None,
) -> List[Dict]:
    records = []
    for chunk in chunks:
        record = asdict(chunk)
        record.update(
            {
                "filename": document["filename"],
                "document_type": document_type or document["document_type"],
                "title": title or document["filename"],
                "issue_date": issue_date,
                "effective_date": effective_date,
                "status": status,
                "version": version,
            }
        )
        records.append(record)
    return records
