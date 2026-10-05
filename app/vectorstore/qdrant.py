from typing import Dict, Iterable, List
import hashlib

from qdrant_client import QdrantClient
from qdrant_client.http import models


class QdrantVectorStore:
    """Qdrant collection management and vector upsert operations."""

    def __init__(
        self,
        url: str,
        collection_name: str,
        api_key: str | None = None,
        vector_size: int = 1536,
        client: QdrantClient | None = None,
    ):
        if not url:
            raise ValueError("QDRANT_URL is required")
        if not collection_name:
            raise ValueError("collection_name is required")
        if vector_size <= 0:
            raise ValueError("vector_size must be positive")

        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = client or QdrantClient(url=url, api_key=api_key)

    def check_connection(self) -> None:
        try:
            if hasattr(self.client, "get_collections"):
                self.client.get_collections()
                return

            # Compatibility fallback for minimal/fake clients.
            self.client.collection_exists(self.collection_name)
        except Exception as exc:
            raise RuntimeError("Qdrant is not reachable") from exc

    def ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def upsert_chunks(
        self,
        chunks: Iterable[Dict],
        embeddings: List[List[float]],
    ) -> None:
        chunk_list = list(chunks)

        if len(chunk_list) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        points = []

        for chunk, vector in zip(chunk_list, embeddings):
            if len(vector) != self.vector_size:
                raise ValueError(
                    f"Expected vector size {self.vector_size}, "
                    f"received {len(vector)}"
                )

            points.append(
                models.PointStruct(
                    id=_stable_point_id(chunk["chunk_id"]),
                    vector=vector,
                    payload={
                        key: value
                        for key, value in chunk.items()
                        if key != "embedding"
                    },
                )
            )

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )


def _stable_point_id(chunk_id: str) -> int:
    digest = hashlib.sha256(chunk_id.encode("utf-8")).digest()
    return int.from_bytes(
        digest[:8],
        byteorder="big",
    ) & ((1 << 63) - 1)
