from pathlib import Path

import pytest

from app.ingestion.chunker import TokenAwareChunker
from app.ingestion.cleaner import clean_text


def test_clean_text_normalizes_whitespace():
    text = "Rule   applies\r\n\r\n\r\nPage 4\n\nApproval"
    cleaned = clean_text(text)
    assert "Rule applies" in cleaned
    assert "Page 4" not in cleaned
    assert "\n\n\n" not in cleaned


def test_chunker_validates_overlap():
    with pytest.raises(ValueError):
        TokenAwareChunker(chunk_size=100, overlap=100)


def test_chunker_creates_token_limited_chunks():
    chunker = TokenAwareChunker(chunk_size=20, overlap=5)
    chunks = chunker.chunk_page("TEST-001", "approval requirement " * 100, 2)
    assert len(chunks) > 1
    assert all(c.document_id == "TEST-001" for c in chunks)
    assert all(c.page == 2 for c in chunks)
    assert all(c.token_count <= 20 for c in chunks)


def test_sample_corpus_exists():
    assert Path("data/raw/CIRC-2026-001.txt").exists()
