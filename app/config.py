from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple


def _env_int(name: str, default: int, *, minimum: int = 0) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if value < minimum:
        raise RuntimeError(f"{name} must be >= {minimum}")
    return value


def _env_float(name: str, default: float, *, minimum: float = 0.0) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number") from exc
    if value < minimum:
        raise RuntimeError(f"{name} must be >= {minimum}")
    return value


def _env_list(name: str, default: str) -> Tuple[str, ...]:
    values = tuple(item.strip() for item in os.getenv(name, default).split(",") if item.strip())
    if not values:
        raise RuntimeError(f"{name} must contain at least one value")
    return values


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    embedding_model: str
    embedding_batch_size: int
    qdrant_url: str
    qdrant_api_key: str | None
    qdrant_collection: str
    embedding_dimensions: int
    rag_model: str
    rag_default_top_k: int
    rag_max_top_k: int
    openai_timeout_seconds: float
    openai_max_retries: int


def load_settings() -> Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    qdrant_url = os.getenv("QDRANT_URL", "").strip()
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    if not qdrant_url:
        raise RuntimeError("QDRANT_URL is not configured")

    default_top_k = _env_int("RAG_DEFAULT_TOP_K", 5, minimum=1)
    max_top_k = _env_int("RAG_MAX_TOP_K", 10, minimum=1)
    if max_top_k < default_top_k:
        raise RuntimeError("RAG_MAX_TOP_K must be >= RAG_DEFAULT_TOP_K")

    return Settings(
        openai_api_key=openai_api_key,
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small").strip(),
        embedding_batch_size=_env_int("EMBEDDING_BATCH_SIZE", 64, minimum=1),
        qdrant_url=qdrant_url,
        qdrant_api_key=os.getenv("QDRANT_API_KEY") or None,
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "compliance_chunks").strip(),
        embedding_dimensions=_env_int("EMBEDDING_DIMENSIONS", 1536, minimum=1),
        rag_model=os.getenv("RAG_MODEL", "gpt-6-luna").strip(),
        rag_default_top_k=default_top_k,
        rag_max_top_k=max_top_k,
        openai_timeout_seconds=_env_float("OPENAI_TIMEOUT_SECONDS", 60.0, minimum=1.0),
        openai_max_retries=_env_int("OPENAI_MAX_RETRIES", 2, minimum=0),
    )


def load_cors_origins() -> Tuple[str, ...]:
    return _env_list("CORS_ORIGINS", "http://localhost:5173")
