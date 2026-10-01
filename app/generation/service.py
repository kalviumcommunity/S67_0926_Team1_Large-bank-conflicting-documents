from typing import Optional

from app.generation.llm import LLMProvider
from app.generation.models import EvidenceItem, RagResponse
from app.generation.prompt import SYSTEM_INSTRUCTIONS, build_rag_input
from app.retrieval.models import SearchFilters, SearchResult


class RagGenerationError(RuntimeError):
    """Raised when a grounded RAG response cannot be produced."""


class RagService:
    """Retrieves evidence and generates an answer grounded in that evidence."""

    def __init__(
        self,
        retrieval_pipeline,
        llm: LLMProvider,
        *,
        default_top_k: int = 5,
        max_top_k: int = 10,
    ):
        if default_top_k <= 0:
            raise ValueError("default_top_k must be positive")
        if max_top_k < default_top_k:
            raise ValueError("max_top_k must be >= default_top_k")

        self.retrieval_pipeline = retrieval_pipeline
        self.llm = llm
        self.default_top_k = default_top_k
        self.max_top_k = max_top_k

    def answer(
        self,
        query: str,
        *,
        top_k: Optional[int] = None,
        filters: Optional[SearchFilters] = None,
    ) -> RagResponse:
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("query cannot be empty")

        requested_top_k = self.default_top_k if top_k is None else top_k
        if requested_top_k <= 0 or requested_top_k > self.max_top_k:
            raise ValueError(
                f"top_k must be between 1 and {self.max_top_k}"
            )

        try:
            results = self.retrieval_pipeline.search(
                normalized_query,
                top_k=requested_top_k,
                filters=filters,
            )
        except Exception as exc:
            raise RagGenerationError(
                "retrieval failed before answer generation"
            ) from exc

        if not results:
            return RagResponse(
                query=normalized_query,
                answer="I have insufficient compliance evidence to answer that question.",
                evidence=[],
            )

        evidence = [
            EvidenceItem(
                evidence_id=f"E{index}",
                result=result,
            )
            for index, result in enumerate(results, start=1)
        ]

        prompt = build_rag_input(normalized_query, evidence)

        try:
            answer = self.llm.generate(
                SYSTEM_INSTRUCTIONS,
                prompt,
            )
        except Exception as exc:
            raise RagGenerationError(
                "grounded answer generation failed"
            ) from exc

        return RagResponse(
            query=normalized_query,
            answer=answer,
            evidence=evidence,
        )
