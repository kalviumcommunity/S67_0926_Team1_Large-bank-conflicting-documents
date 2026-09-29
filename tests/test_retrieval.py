from types import SimpleNamespace

import pytest

from app.retrieval.models import SearchFilters
from app.retrieval.service import RetrievalError, SemanticRetriever


class FakeEmbedder:
    def embed_texts(self, texts):
        assert len(texts) == 1
        return [[0.1, 0.2, 0.3]]


class FakeVectorStore:
    collection_name = "compliance_chunks"

    def __init__(self):
        self.calls = []

        class Client:
            def __init__(inner_self, outer):
                inner_self.outer = outer

            def query_points(inner_self, **kwargs):
                inner_self.outer.calls.append(kwargs)
                return SimpleNamespace(
                    points=[
                        SimpleNamespace(
                            id=101,
                            score=0.94,
                            payload={
                                "chunk_id": "CIRC-001-p2-c001",
                                "document_id": "CIRC-001",
                                "text": "Approval is required for this transaction.",
                                "page": 2,
                                "filename": "CIRC-001.pdf",
                                "document_type": "circular",
                                "title": "Transaction Approval",
                                "issue_date": "2026-04-01",
                                "effective_date": "2026-04-15",
                                "status": "active",
                                "version": "2",
                            },
                        )
                    ]
                )

        self.client = Client(self)


def test_semantic_search_returns_traceable_results():
    store = FakeVectorStore()
    retriever = SemanticRetriever(FakeEmbedder(), store)

    results = retriever.search("approval requirement", top_k=5)

    assert len(results) == 1
    result = results[0]

    assert result.chunk_id == "CIRC-001-p2-c001"
    assert result.document_id == "CIRC-001"
    assert result.score == 0.94
    assert result.page == 2
    assert result.status == "active"


def test_metadata_filters_are_sent_to_qdrant():
    store = FakeVectorStore()
    retriever = SemanticRetriever(FakeEmbedder(), store)

    retriever.search(
        "approval requirement",
        filters=SearchFilters(
            document_type="circular",
            status="active",
            version="2",
        ),
    )

    qdrant_filter = store.calls[0]["query_filter"]

    assert qdrant_filter is not None
    assert len(qdrant_filter.must) == 3


def test_empty_query_is_rejected():
    retriever = SemanticRetriever(FakeEmbedder(), FakeVectorStore())

    with pytest.raises(ValueError):
        retriever.search("   ")


def test_invalid_top_k_is_rejected():
    retriever = SemanticRetriever(FakeEmbedder(), FakeVectorStore())

    with pytest.raises(ValueError):
        retriever.search("approval", top_k=0)

    with pytest.raises(ValueError):
        retriever.search("approval", top_k=21)


def test_empty_result_set_is_supported():
    class EmptyClient:
        def query_points(self, **kwargs):
            return SimpleNamespace(points=[])

    store = SimpleNamespace(
        collection_name="compliance_chunks",
        client=EmptyClient(),
    )

    retriever = SemanticRetriever(FakeEmbedder(), store)

    assert retriever.search("approval") == []


def test_qdrant_failure_is_wrapped():
    class BrokenClient:
        def query_points(self, **kwargs):
            raise RuntimeError("connection failed")

    store = SimpleNamespace(
        collection_name="compliance_chunks",
        client=BrokenClient(),
    )

    retriever = SemanticRetriever(FakeEmbedder(), store)

    with pytest.raises(RetrievalError):
        retriever.search("approval")
