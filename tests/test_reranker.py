import pytest

from app.retrieval.models import SearchResult
from app.retrieval.reranker import RelevanceReranker


def result(chunk_id, score, text):
    return SearchResult(
        chunk_id=chunk_id,
        document_id="DOC1",
        text=text,
        score=score,
        page=1,
        filename="DOC1.pdf",
        document_type="circular",
        title="Rule",
        issue_date="2026-01-01",
        effective_date="2026-01-15",
        status="active",
        version="1",
    )


def test_reranker_prefers_term_coverage():
    reranker = RelevanceReranker(lexical_weight=0.5)
    results = reranker.rerank(
        "approval transaction",
        [
            result("A", 0.80, "approval"),
            result("B", 0.75, "approval transaction"),
        ],
    )
    assert results[0].chunk_id == "B"


def test_reranker_supports_top_k():
    results = RelevanceReranker().rerank(
        "approval",
        [result("A", 0.8, "approval"), result("B", 0.7, "approval")],
        top_k=1,
    )
    assert len(results) == 1


def test_reranker_rejects_empty_query():
    with pytest.raises(ValueError):
        RelevanceReranker().rerank("", [result("A", 0.8, "approval")])
