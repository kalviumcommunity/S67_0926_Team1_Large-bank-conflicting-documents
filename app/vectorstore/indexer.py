from typing import Dict, Iterable

from app.embeddings.embedder import OpenAIEmbedder
from app.vectorstore.qdrant import QdrantVectorStore


class DocumentIndexer:
    """Coordinates chunk embedding and Qdrant indexing."""

    def __init__(
        self,
        embedder: OpenAIEmbedder,
        vector_store: QdrantVectorStore,
    ):
        self.embedder = embedder
        self.vector_store = vector_store

    def index_chunks(self, chunks: Iterable[Dict]) -> int:
        chunk_list = list(chunks)
        if not chunk_list:
            return 0

        embeddings = self.embedder.embed_chunks(chunk_list)

        self.vector_store.ensure_collection()
        self.vector_store.upsert_chunks(chunk_list, embeddings)

        return len(chunk_list)

    def check_ready(self) -> None:
        self.vector_store.check_connection()
