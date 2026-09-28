import pytest
from app.vectorstore.qdrant import QdrantVectorStore


class FakeQdrant:
    def __init__(self):
        self.collections = set()
        self.upserts = []

    def collection_exists(self, name):
        return name in self.collections

    def create_collection(self, **kwargs):
        self.collections.add(kwargs["collection_name"])

    def upsert(self, **kwargs):
        self.upserts.append(kwargs)


def make_store(fake):
    return QdrantVectorStore(
        url="http://test", collection_name="compliance_chunks",
        vector_size=3, client=fake
    )


def test_ensure_collection_creates_missing_collection():
    fake = FakeQdrant()
    make_store(fake).ensure_collection()
    assert "compliance_chunks" in fake.collections


def test_ensure_collection_does_not_recreate_existing_collection():
    fake = FakeQdrant()
    fake.collections.add("compliance_chunks")
    make_store(fake).ensure_collection()
    assert len(fake.collections) == 1


def test_upsert_preserves_chunk_metadata():
    fake = FakeQdrant()
    store = make_store(fake)
    chunks = [{
        "chunk_id": "CIRC-1-p1-c000",
        "document_id": "CIRC-1",
        "text": "Approval is required.",
        "page": 1,
        "status": "active",
    }]
    store.upsert_chunks(chunks, [[0.1, 0.2, 0.3]])
    point = fake.upserts[0]["points"][0]
    assert point.payload["chunk_id"] == "CIRC-1-p1-c000"
    assert point.payload["document_id"] == "CIRC-1"


def test_upsert_rejects_wrong_vector_dimension():
    fake = FakeQdrant()
    with pytest.raises(ValueError):
        make_store(fake).upsert_chunks(
            [{"chunk_id": "C1", "text": "hello"}], [[0.1, 0.2]]
        )


def test_upsert_rejects_mismatched_lengths():
    fake = FakeQdrant()
    with pytest.raises(ValueError):
        make_store(fake).upsert_chunks(
            [{"chunk_id": "C1", "text": "hello"}], []
        )
