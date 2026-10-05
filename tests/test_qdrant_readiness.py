import pytest

from app.vectorstore.qdrant import QdrantVectorStore


class FakeQdrant:
    def get_collections(self):
        return {"collections": []}


class BrokenQdrant:
    def get_collections(self):
        raise RuntimeError("connection refused")


def test_qdrant_connection_check():
    store = QdrantVectorStore(
        url="http://qdrant",
        collection_name="compliance_chunks",
        vector_size=3,
        client=FakeQdrant(),
    )

    store.check_connection()


def test_qdrant_connection_failure_is_reported():
    store = QdrantVectorStore(
        url="http://qdrant",
        collection_name="compliance_chunks",
        vector_size=3,
        client=BrokenQdrant(),
    )

    with pytest.raises(RuntimeError):
        store.check_connection()
