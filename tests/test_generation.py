from dataclasses import dataclass

import pytest

from app.generation.service import RagGenerationError, RagService
from app.retrieval.models import SearchResult


def result(chunk_id="C1", text="Approval is required."):
    return SearchResult(
        chunk_id=chunk_id,
        document_id="DOC1",
        text=text,
        score=0.91,
        page=3,
        filename="DOC1.pdf",
        document_type="circular",
        title="Approval Rule",
        issue_date="2026-01-01",
        effective_date="2026-01-15",
        status="active",
        version="1",
    )


class FakeRetriever:
    def __init__(self, results=None):
        self.results = list(results or [])
        self.calls = []

    def search(self, query, *, top_k, filters=None):
        self.calls.append((query, top_k, filters))
        return self.results[:top_k]


class FakeLLM:
    def __init__(self, answer="Approval is required [E1]."):
        self.answer = answer
        self.calls = []

    def generate(self, instructions, user_input):
        self.calls.append((instructions, user_input))
        return self.answer


def test_rag_service_builds_grounded_response():
    retriever = FakeRetriever([result()])
    llm = FakeLLM()

    service = RagService(retriever, llm)
    response = service.answer("What is required?")

    assert response.query == "What is required?"
    assert response.answer == "Approval is required [E1]."
    assert response.used_chunk_ids == ["C1"]
    assert response.evidence[0].evidence_id == "E1"
    assert "Approval is required." in llm.calls[0][1]


def test_empty_results_return_explicit_insufficient_evidence():
    retriever = FakeRetriever([])
    llm = FakeLLM()

    response = RagService(retriever, llm).answer("What is required?")

    assert response.evidence == []
    assert "insufficient compliance evidence" in response.answer


def test_empty_query_is_rejected():
    with pytest.raises(ValueError):
        RagService(FakeRetriever(), FakeLLM()).answer("   ")


def test_top_k_is_bounded():
    service = RagService(
        FakeRetriever([result()]),
        FakeLLM(),
        default_top_k=2,
        max_top_k=3,
    )

    with pytest.raises(ValueError):
        service.answer("question", top_k=4)


def test_retrieval_failure_is_wrapped():
    class BrokenRetriever:
        def search(self, *args, **kwargs):
            raise RuntimeError("qdrant failed")

    with pytest.raises(RagGenerationError):
        RagService(BrokenRetriever(), FakeLLM()).answer("question")


def test_llm_failure_is_wrapped():
    class BrokenLLM:
        def generate(self, *args, **kwargs):
            raise RuntimeError("provider unavailable")

    with pytest.raises(RagGenerationError):
        RagService(FakeRetriever([result()]), BrokenLLM()).answer("question")
