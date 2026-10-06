from __future__ import annotations

from functools import lru_cache

from app.config import load_settings
from app.embeddings.embedder import OllamaEmbedder
from app.generation.llm import OllamaLLMProvider
from app.generation.service import RagService
from app.ollama.client import OllamaClient
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
        client = OllamaClient(
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout_seconds,
        )
        embedder = OllamaEmbedder(
            model=settings.ollama_embedding_model,
            batch_size=settings.embedding_batch_size,
            client=client,
        )
        store = QdrantVectorStore(
            url=settings.qdrant_url,
            collection_name=settings.qdrant_collection,
            api_key=settings.qdrant_api_key,
        )
        semantic = SemanticRetriever(
            embedder=embedder,
            vector_store=store,
            max_top_k=max(settings.rag_max_top_k, 20),
        )
        hybrid = HybridRetriever(
            semantic_retriever=semantic,
            keyword_retriever=KeywordRetriever(),
            candidate_k=max(settings.rag_max_top_k, 20),
        )
        retrieval = RetrievalPipeline(
            hybrid_retriever=hybrid,
            reranker=RelevanceReranker(),
        )
        llm = OllamaLLMProvider(
            model=settings.ollama_chat_model,
            client=client,
            timeout=settings.ollama_timeout_seconds,
        )
        return RagService(
            retrieval_pipeline=retrieval,
            llm=llm,
            default_top_k=settings.rag_default_top_k,
            max_top_k=settings.rag_max_top_k,
        )
    except Exception as exc:
        raise RagServiceConfigurationError(
            "RAG service is not configured correctly"
        ) from exc


def check_rag_ready() -> None:
    service = get_rag_service()
    embedder = (
        service.retrieval_pipeline
        .hybrid_retriever
        .semantic_retriever
        .embedder
    )
    embedder.check_ready()
    service.llm.check_ready()
