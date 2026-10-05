from datetime import date

from fastapi.testclient import TestClient

from app.api import rag_routes
from app.generation.models import EvidenceItem, RagResponse
from app.main import app


class FakeRagService:
    def __init__(self):
        self.calls = []

    def answer(self, query, *, top_k, filters, as_of_date):
        self.calls.append((query, top_k, filters, as_of_date))
        from app.retrieval.models import SearchResult
        result = SearchResult(
            chunk_id="C1", document_id="DOC1", text="Approval is required.", score=0.92,
            page=4, filename="DOC1.pdf", document_type="circular", title="Approval Rule",
            issue_date="2026-01-01", effective_date="2026-01-15", status="active", version="2",
        )
        return RagResponse(query=query, answer="Approval is required [E1].", evidence=[EvidenceItem("E1", result)])


client = TestClient(app)


def test_query_endpoint_returns_grounded_response(monkeypatch):
    service = FakeRagService()
    monkeypatch.setattr(rag_routes, "get_rag_service", lambda: service)
    response = client.post(
        "/api/query",
        json={"question": "What approval is required?", "top_k": 3, "as_of_date": "2026-06-01", "document_type": "circular", "status": "active", "version": "2"},
        headers={"X-Request-ID": "test-request"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Approval is required [E1]."
    assert payload["used_chunk_ids"] == ["C1"]
    assert payload["evidence"][0]["evidence_id"] == "E1"
    assert response.headers["X-Request-ID"] == "test-request"
    assert service.calls[0][0] == "What approval is required?"
    assert service.calls[0][1] == 3
    assert service.calls[0][3] == date(2026, 6, 1)


def test_query_validation_rejects_empty_question():
    assert client.post("/api/query", json={"question": ""}).status_code == 422


def test_query_validation_rejects_large_top_k():
    assert client.post("/api/query", json={"question": "What?", "top_k": 11}).status_code == 422


def test_query_maps_configuration_failure_to_503(monkeypatch):
    from app.services.rag_application import RagServiceConfigurationError
    def broken_service():
        raise RagServiceConfigurationError("missing")
    monkeypatch.setattr(rag_routes, "get_rag_service", broken_service)
    response = client.post("/api/query", json={"question": "What is required?"})
    assert response.status_code == 503


def test_query_does_not_expose_internal_exception(monkeypatch):
    class BrokenService:
        def answer(self, **kwargs):
            raise RuntimeError("secret qdrant endpoint")
    monkeypatch.setattr(rag_routes, "get_rag_service", lambda: BrokenService())
    response = client.post("/api/query", json={"question": "What is required?"})
    assert response.status_code == 500
    assert "secret qdrant endpoint" not in response.text
