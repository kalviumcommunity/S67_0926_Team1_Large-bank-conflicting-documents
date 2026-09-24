from typing import Dict, List, Optional

from app.ingestion.chunker import TokenAwareChunker
from app.ingestion.cleaner import clean_text
from app.ingestion.loaders import load_document
from app.ingestion.metadata import build_chunk_records


def ingest_document(
    file_path: str,
    *,
    chunk_size: int = 700,
    overlap: int = 100,
    metadata: Optional[Dict] = None,
) -> List[Dict]:
    document = load_document(file_path)
    chunker = TokenAwareChunker(chunk_size=chunk_size, overlap=overlap)
    all_chunks = []
    next_index = 0

    for page in document["pages"]:
        cleaned = clean_text(page["text"])
        if not cleaned:
            continue
        chunks = chunker.chunk_page(
            document_id=document["document_id"],
            text=cleaned,
            page=page["page"],
            start_index=next_index,
        )
        all_chunks.extend(chunks)
        next_index += len(chunks)

    metadata = metadata or {}
    return build_chunk_records(
        document,
        all_chunks,
        document_type=metadata.get("document_type"),
        title=metadata.get("title"),
        issue_date=metadata.get("issue_date"),
        effective_date=metadata.get("effective_date"),
        status=metadata.get("status", "unknown"),
        version=metadata.get("version"),
    )
