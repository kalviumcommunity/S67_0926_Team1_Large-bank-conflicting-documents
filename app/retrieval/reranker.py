from dataclasses import replace
from typing import List, Optional, Protocol

from app.retrieval.models import SearchResult


class Reranker(Protocol):
    def rerank(
        self,
        query: str,
        results: List[SearchResult],
        *,
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        ...


class ReRankingError(RuntimeError):
    pass


class RelevanceReranker:
    """Deterministic baseline reranker using query-term coverage."""

    def __init__(self, lexical_weight: float = 0.35):
        if lexical_weight < 0:
            raise ValueError("lexical_weight cannot be negative")
        self.lexical_weight = lexical_weight

    def rerank(
        self,
        query: str,
        results: List[SearchResult],
        *,
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        query_terms = {
            token.strip(".,:;!?()[]{}\"'").lower()
            for token in query.split()
            if token.strip(".,:;!?()[]{}\"'")
        }

        if not query_terms:
            raise ValueError("query cannot be empty")

        ranked = []
        for result in results:
            text_terms = {
                token.strip(".,:;!?()[]{}\"'").lower()
                for token in result.text.split()
                if token.strip(".,:;!?()[]{}\"'")
            }
            coverage = len(query_terms.intersection(text_terms)) / len(query_terms)
            final_score = result.score + self.lexical_weight * coverage
            ranked.append((final_score, result))

        ranked.sort(
            key=lambda item: (
                -item[0],
                item[1].document_id,
                item[1].page or 0,
                item[1].chunk_id,
            )
        )

        output = [replace(result, score=float(score)) for score, result in ranked]

        if top_k is not None:
            if top_k <= 0:
                raise ValueError("top_k must be positive")
            output = output[:top_k]

        return output
