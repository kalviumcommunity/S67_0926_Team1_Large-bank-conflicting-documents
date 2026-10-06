from fastapi.testclient import TestClient

from app.main import app


class FakeService:
    def __init__(self):
        self.records = [
            {
                "document_id": "DOC-1",
                "filename": "rule.pdf",
                "status": "failed",
                "chunk_count": 4,
                "indexed_count": 0,
                "version": "2",
                "updated_at": "2026-10-05T00:00:00+00:00",
            }
        ]

    def list_documents(self, *, status=None, limit=100, offset=0):
        return [r for r in self.records if status is None or r["status"] == status]

    async def retry_document(self, document_id):
        return {
            "document_id": document_id,
            "filename": "rule.pdf",
            "status": "indexed",
            "chunk_count": 4,
            "indexed_count": 4,
            "sha256": "a" * 64,
            "ingested_at": "2026-10-05T01:00:00+00:00",
        }

    def get_status(self, document_id):
        return None

    def check_ready(self):
        return None


def test_document_inventory_hides_internal_fields(monkeypatch):
    service = FakeService()
    monkeypatch.setattr("app.api.routes.build_default_ingestion_service", lambda: service)

    response = TestClient(app).get("/api/documents?status=failed")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["items"][0]["document_id"] == "DOC-1"
    assert "stored_path" not in body["items"][0]
    assert "error_message" not in body["items"][0]


def test_document_inventory_rejects_unknown_status():
    response = TestClient(app).get("/api/documents?status=unknown")
    assert response.status_code == 422


def test_document_retry_endpoint(monkeypatch):
    service = FakeService()
    monkeypatch.setattr("app.api.routes.build_default_ingestion_service", lambda: service)

    response = TestClient(app).post("/api/documents/DOC-1/retry")

    assert response.status_code == 200
    assert response.json()["status"] == "indexed"
