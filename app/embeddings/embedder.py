from typing import Iterable, List, Sequence
from openai import OpenAI


class EmbeddingError(RuntimeError):
    """Raised when embedding generation fails."""


class OpenAIEmbedder:
    """Batched, validated wrapper around the OpenAI embeddings API."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small",
                 batch_size: int = 64, client: OpenAI | None = None):
        if not api_key:
            raise ValueError("api_key is required")
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.client = client or OpenAI(api_key=api_key)
        self.model = model
        self.batch_size = batch_size

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        cleaned = [text.strip() for text in texts]
        if not cleaned:
            return []
        if any(not text for text in cleaned):
            raise ValueError("Embedding input cannot contain empty text")

        vectors: List[List[float]] = []
        try:
            for start in range(0, len(cleaned), self.batch_size):
                batch = cleaned[start:start + self.batch_size]
                response = self.client.embeddings.create(
                    model=self.model, input=batch
                )
                data = sorted(response.data, key=lambda item: item.index)
                if len(data) != len(batch):
                    raise EmbeddingError(
                        "Embedding API returned an unexpected number of vectors"
                    )
                vectors.extend(item.embedding for item in data)
        except EmbeddingError:
            raise
        except Exception as exc:
            raise EmbeddingError("Embedding generation failed") from exc
        return vectors

    def embed_chunks(self, chunks: Iterable[dict]) -> List[List[float]]:
        chunk_list = list(chunks)
        return self.embed_texts([chunk["text"] for chunk in chunk_list])
