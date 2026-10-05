from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Tuple

def _int_env(name,default,minimum=0):
    try: value=int(os.getenv(name,str(default)).strip())
    except ValueError as exc: raise RuntimeError(f'{name} must be an integer') from exc
    if value<minimum: raise RuntimeError(f'{name} must be >= {minimum}')
    return value
def _float_env(name,default,minimum=0.0):
    try: value=float(os.getenv(name,str(default)).strip())
    except ValueError as exc: raise RuntimeError(f'{name} must be a number') from exc
    if value<minimum: raise RuntimeError(f'{name} must be >= {minimum}')
    return value
def _list_env(name,default)->Tuple[str,...]:
    values=tuple(x.strip() for x in os.getenv(name,default).split(',') if x.strip())
    if not values: raise RuntimeError(f'{name} must contain at least one value')
    return values
@dataclass(frozen=True)
class Settings:
    ollama_base_url:str; ollama_chat_model:str; ollama_embedding_model:str; ollama_timeout_seconds:float; embedding_batch_size:int
    qdrant_url:str; qdrant_api_key:str|None; qdrant_collection:str; rag_default_top_k:int; rag_max_top_k:int
def load_settings()->Settings:
    default_k=_int_env('RAG_DEFAULT_TOP_K',5,1); max_k=_int_env('RAG_MAX_TOP_K',10,1)
    if max_k<default_k: raise RuntimeError('RAG_MAX_TOP_K must be >= RAG_DEFAULT_TOP_K')
    return Settings(ollama_base_url=os.getenv('OLLAMA_BASE_URL','http://localhost:11434').strip(),ollama_chat_model=os.getenv('OLLAMA_CHAT_MODEL','gemma3:4b').strip(),ollama_embedding_model=os.getenv('OLLAMA_EMBEDDING_MODEL','nomic-embed-text').strip(),ollama_timeout_seconds=_float_env('OLLAMA_TIMEOUT_SECONDS',120,1.0),embedding_batch_size=_int_env('EMBEDDING_BATCH_SIZE',32,1),qdrant_url=os.getenv('QDRANT_URL','http://localhost:6333').strip(),qdrant_api_key=os.getenv('QDRANT_API_KEY') or None,qdrant_collection=os.getenv('QDRANT_COLLECTION','compliance_chunks_ollama').strip(),rag_default_top_k=default_k,rag_max_top_k=max_k)
def load_cors_origins()->Tuple[str,...]: return _list_env('CORS_ORIGINS','http://localhost:5173')
