from typing import List, Optional, Protocol

from app.retrieval.hybrid import HybridRetriever
from app.retrieval.models import SearchFilters, SearchResult


class Reranker(Protocol):
    def rerank(
        self,
        query: str,
        results: List[SearchResult],
        *,
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        ...


class RetrievalPipeline:
    """Hybrid retrieval followed by result reranking."""

    def __init__(
        self,
        hybrid_retriever: HybridRetriever,
        reranker: Reranker,
    ):
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: Optional[SearchFilters] = None,
    ) -> List[SearchResult]:
        candidates = self.hybrid_retriever.search(
            query,
            top_k=self.hybrid_retriever.candidate_k,
            filters=filters,
        )
        return self.reranker.rerank(query, candidates, top_k=top_k)
