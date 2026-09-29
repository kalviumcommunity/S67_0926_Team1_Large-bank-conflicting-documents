from typing import Any, List, Optional, Protocol

from app.retrieval.filters import build_qdrant_filter
from app.retrieval.models import SearchFilters, SearchResult


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        ...


class VectorStoreProvider(Protocol):
    collection_name: str
    client: Any


class RetrievalError(RuntimeError):
    """Raised when semantic retrieval cannot be completed."""


class SemanticRetriever:
    """Semantic retrieval over the existing Qdrant vector index."""

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStoreProvider,
        max_top_k: int = 20,
    ):
        if max_top_k <= 0:
            raise ValueError("max_top_k must be positive")

        self.embedder = embedder
        self.vector_store = vector_store
        self.max_top_k = max_top_k

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: Optional[SearchFilters] = None,
    ) -> List[SearchResult]:
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("query cannot be empty")

        if top_k <= 0 or top_k > self.max_top_k:
            raise ValueError(
                f"top_k must be between 1 and {self.max_top_k}"
            )

        try:
            vectors = self.embedder.embed_texts([normalized_query])
            if len(vectors) != 1:
                raise RetrievalError(
                    "embedding provider returned an unexpected number of vectors"
                )

            query_vector = vectors[0]
            query_filter = build_qdrant_filter(filters)

            points = self._query_qdrant(
                query_vector=query_vector,
                query_filter=query_filter,
                top_k=top_k,
            )

            return [self._to_result(point) for point in points]

        except (ValueError, RetrievalError):
            raise
        except Exception as exc:
            raise RetrievalError("semantic retrieval failed") from exc

    def _query_qdrant(self, query_vector, query_filter, top_k):
        client = self.vector_store.client

        # qdrant-client versions expose either query_points or search.
        if hasattr(client, "query_points"):
            response = client.query_points(
                collection_name=self.vector_store.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            )
            return list(getattr(response, "points", response))

        if hasattr(client, "search"):
            return list(
                client.search(
                    collection_name=self.vector_store.collection_name,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=top_k,
                    with_payload=True,
                )
            )

        raise RetrievalError(
            "Qdrant client does not expose a supported search method"
        )

    @staticmethod
    def _to_result(point: Any) -> SearchResult:
        payload = getattr(point, "payload", None) or {}

        return SearchResult(
            chunk_id=str(payload.get("chunk_id", getattr(point, "id", ""))),
            document_id=str(payload.get("document_id", "")),
            text=str(payload.get("text", "")),
            score=float(getattr(point, "score", 0.0)),
            page=payload.get("page"),
            filename=payload.get("filename"),
            document_type=payload.get("document_type"),
            title=payload.get("title"),
            issue_date=payload.get("issue_date"),
            effective_date=payload.get("effective_date"),
            status=payload.get("status"),
            version=payload.get("version"),
        )
