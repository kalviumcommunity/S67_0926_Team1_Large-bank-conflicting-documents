from __future__ import annotations
from typing import Dict, Iterable, Protocol
from app.vectorstore.qdrant import QdrantVectorStore
class EmbeddingProvider(Protocol):
    def embed_chunks(self,chunks:Iterable[Dict])->list[list[float]]: ...
    def check_ready(self)->None: ...
class DocumentIndexer:
    def __init__(self,embedder:EmbeddingProvider,vector_store:QdrantVectorStore): self.embedder=embedder; self.vector_store=vector_store
    def index_chunks(self,chunks:Iterable[Dict])->int:
        chunk_list=list(chunks)
        if not chunk_list: return 0
        embeddings=self.embedder.embed_chunks(chunk_list)
        if not embeddings: raise ValueError('embedding provider returned no vectors')
        self.vector_store.ensure_collection(vector_size=len(embeddings[0]))
        self.vector_store.upsert_chunks(chunk_list,embeddings)
        return len(chunk_list)
    def check_ready(self): self.vector_store.check_connection(); self.embedder.check_ready()
