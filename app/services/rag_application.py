from __future__ import annotations

from functools import lru_cache

from app.config import load_settings
from app.embeddings.embedder import OpenAIEmbedder
from app.generation.llm import OpenAIResponsesProvider
from app.generation.service import RagService
from app.retrieval.hybrid import HybridRetriever, KeywordRetriever
from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.reranker import RelevanceReranker
from app.retrieval.service import SemanticRetriever
from app.vectorstore.qdrant import QdrantVectorStore


class RagServiceConfigurationError(RuntimeError):
    """Raised when the production RAG stack cannot be configured."""


@lru_cache(maxsize=1)
def get_rag_service() -> RagService:
    try:
        settings = load_settings()
        embedder = OpenAIEmbedder(api_key=settings.openai_api_key, model=settings.embedding_model, batch_size=settings.embedding_batch_size)
        vector_store = QdrantVectorStore(url=settings.qdrant_url, collection_name=settings.qdrant_collection, api_key=settings.qdrant_api_key, vector_size=settings.embedding_dimensions)
        semantic = SemanticRetriever(embedder=embedder, vector_store=vector_store, max_top_k=max(settings.rag_max_top_k, 20))
        keyword = KeywordRetriever()
        hybrid = HybridRetriever(semantic_retriever=semantic, keyword_retriever=keyword, candidate_k=max(settings.rag_max_top_k, 20))
        retrieval = RetrievalPipeline(hybrid_retriever=hybrid, reranker=RelevanceReranker())
        llm = OpenAIResponsesProvider(api_key=settings.openai_api_key, model=settings.rag_model, timeout=settings.openai_timeout_seconds, max_retries=settings.openai_max_retries)
        return RagService(retrieval_pipeline=retrieval, llm=llm, default_top_k=settings.rag_default_top_k, max_top_k=settings.rag_max_top_k)
    except Exception as exc:
        raise RagServiceConfigurationError("RAG service is not configured correctly") from exc
