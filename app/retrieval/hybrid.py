from dataclasses import replace
from typing import List, Optional, Sequence, Tuple

from app.retrieval.models import SearchFilters, SearchResult
from app.retrieval.service import SemanticRetriever


class KeywordRetriever:
    """Simple lexical retriever over an explicitly supplied corpus."""

    def __init__(self, records: Optional[Sequence[SearchResult]] = None):
        self._records: List[SearchResult] = list(records or [])

    def replace_records(self, records: Sequence[SearchResult]) -> None:
        self._records = list(records)

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: Optional[SearchFilters] = None,
    ) -> List[SearchResult]:
        terms = _tokens(query)
        if not terms:
            raise ValueError("query cannot be empty")
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        candidates = [
            result for result in self._records
            if _matches_filters(result, filters)
        ]

        scored: List[Tuple[float, SearchResult]] = []
        for result in candidates:
            doc_terms = _tokens(result.text)
            overlap = len(terms.intersection(doc_terms))
            if overlap == 0:
                continue

            score = overlap / max(len(terms), 1)
            scored.append((score, replace(result, score=score)))

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].document_id,
                item[1].page or 0,
                item[1].chunk_id,
            )
        )
        return [result for _, result in scored[:top_k]]


def reciprocal_rank_fusion(
    semantic_results: Sequence[SearchResult],
    keyword_results: Sequence[SearchResult],
    *,
    k: int = 60,
    semantic_weight: float = 1.0,
    keyword_weight: float = 1.0,
) -> List[SearchResult]:
    if k <= 0:
        raise ValueError("fusion k must be positive")
    if semantic_weight < 0 or keyword_weight < 0:
        raise ValueError("fusion weights cannot be negative")
    if semantic_weight == 0 and keyword_weight == 0:
        raise ValueError("at least one fusion weight must be positive")

    merged = {}

    for rank, result in enumerate(semantic_results, start=1):
        merged.setdefault(result.chunk_id, {"result": result, "score": 0.0})
        merged[result.chunk_id]["score"] += semantic_weight / (k + rank)

    for rank, result in enumerate(keyword_results, start=1):
        merged.setdefault(result.chunk_id, {"result": result, "score": 0.0})
        merged[result.chunk_id]["score"] += keyword_weight / (k + rank)

    ranked = sorted(
        merged.values(),
        key=lambda item: (
            -item["score"],
            item["result"].document_id,
            item["result"].page or 0,
            item["result"].chunk_id,
        ),
    )

    return [
        replace(item["result"], score=float(item["score"]))
        for item in ranked
    ]


class HybridRetriever:
    """Combines semantic and lexical retrieval using rank fusion."""

    def __init__(
        self,
        semantic_retriever: SemanticRetriever,
        keyword_retriever: KeywordRetriever,
        *,
        candidate_k: int = 20,
        semantic_weight: float = 1.0,
        keyword_weight: float = 1.0,
        fusion_k: int = 60,
    ):
        if candidate_k <= 0:
            raise ValueError("candidate_k must be positive")

        self.semantic_retriever = semantic_retriever
        self.keyword_retriever = keyword_retriever
        self.candidate_k = candidate_k
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.fusion_k = fusion_k

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: Optional[SearchFilters] = None,
    ) -> List[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        semantic = self.semantic_retriever.search(
            query,
            top_k=self.candidate_k,
            filters=filters,
        )
        keyword = self.keyword_retriever.search(
            query,
            top_k=self.candidate_k,
            filters=filters,
        )

        fused = reciprocal_rank_fusion(
            semantic,
            keyword,
            k=self.fusion_k,
            semantic_weight=self.semantic_weight,
            keyword_weight=self.keyword_weight,
        )
        return fused[:top_k]


def _tokens(text: str) -> set[str]:
    return {
        token.strip(".,:;!?()[]{}\"'").lower()
        for token in text.split()
        if token.strip(".,:;!?()[]{}\"'")
    }


def _matches_filters(
    result: SearchResult,
    filters: Optional[SearchFilters],
) -> bool:
    if not filters:
        return True

    for field_name in (
        "document_type",
        "status",
        "document_id",
        "version",
        "effective_date",
    ):
        expected = getattr(filters, field_name)
        if expected is not None and getattr(result, field_name) != expected:
            return False

    return True
