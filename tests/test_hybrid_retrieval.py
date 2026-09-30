import pytest

from app.retrieval.hybrid import HybridRetriever, KeywordRetriever, reciprocal_rank_fusion
from app.retrieval.models import SearchFilters, SearchResult


def result(chunk_id, score=0.9, status="active", text="approval transaction rule"):
    return SearchResult(
        chunk_id=chunk_id,
        document_id="DOC1",
        text=text,
        score=score,
        page=1,
        filename="DOC1.pdf",
        document_type="circular",
        title="Approval Rule",
        issue_date="2026-01-01",
        effective_date="2026-01-15",
        status=status,
        version="1",
    )


def test_keyword_retriever_scores_matching_terms():
    retriever = KeywordRetriever([
        result("A", text="approval is required for transaction"),
        result("B", text="unrelated account information"),
    ])
    results = retriever.search("approval transaction")
    assert [item.chunk_id for item in results] == ["A"]
    assert results[0].score > 0


def test_keyword_retriever_applies_filters():
    retriever = KeywordRetriever([result("ACTIVE"), result("OLD", status="superseded")])
    results = retriever.search("approval transaction", filters=SearchFilters(status="active"))
    assert [item.chunk_id for item in results] == ["ACTIVE"]


def test_rrf_merges_and_deduplicates():
    semantic = [result("A"), result("B", score=0.8)]
    keyword = [result("A", score=0.7), result("C", score=0.6)]
    fused = reciprocal_rank_fusion(semantic, keyword)
    assert {item.chunk_id for item in fused} == {"A", "B", "C"}
    assert fused[0].chunk_id == "A"


def test_rrf_rejects_zero_weights():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([], [], semantic_weight=0, keyword_weight=0)


def test_hybrid_retriever_respects_top_k():
    class FakeSemantic:
        def search(self, query, *, top_k, filters=None):
            return [result("A"), result("B", score=0.8)]

    class FakeKeyword:
        def search(self, query, *, top_k=5, filters=None):
            return [result("B", score=0.9), result("C", score=0.7)]

    retriever = HybridRetriever(FakeSemantic(), FakeKeyword(), candidate_k=3)
    results = retriever.search("approval", top_k=2)
    assert len(results) == 2
