from app.vectorstore.indexer import DocumentIndexer


class FakeEmbedder:
    def embed_chunks(self, chunks):
        return [[0.1, 0.2, 0.3] for _ in chunks]


class FakeVectorStore:
    def __init__(self):
        self.ensure_called = False
        self.received = None

    def ensure_collection(self):
        self.ensure_called = True

    def upsert_chunks(self, chunks, embeddings):
        self.received = (chunks, embeddings)


def test_index_chunks_returns_count_and_indexes():
    store = FakeVectorStore()
    indexer = DocumentIndexer(FakeEmbedder(), store)
    chunks = [{"chunk_id": "C1", "text": "one"}, {"chunk_id": "C2", "text": "two"}]
    assert indexer.index_chunks(chunks) == 2
    assert store.ensure_called
    assert len(store.received[0]) == 2
    assert len(store.received[1]) == 2


def test_index_empty_chunks():
    store = FakeVectorStore()
    assert DocumentIndexer(FakeEmbedder(), store).index_chunks([]) == 0
    assert not store.ensure_called
