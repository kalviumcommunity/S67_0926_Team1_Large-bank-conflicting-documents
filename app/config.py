import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    embedding_model: str
    embedding_batch_size: int
    qdrant_url: str
    qdrant_api_key: str | None
    qdrant_collection: str
    embedding_dimensions: int


def load_settings() -> Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    qdrant_url = os.getenv("QDRANT_URL", "").strip()
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    if not qdrant_url:
        raise RuntimeError("QDRANT_URL is not configured")

    return Settings(
        openai_api_key=openai_api_key,
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "64")),
        qdrant_url=qdrant_url,
        qdrant_api_key=os.getenv("QDRANT_API_KEY") or None,
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "compliance_chunks"),
        embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
    )
