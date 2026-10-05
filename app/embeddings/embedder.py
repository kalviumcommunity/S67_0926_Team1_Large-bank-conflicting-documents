from __future__ import annotations
from typing import Iterable, List, Sequence
from app.ollama.client import OllamaClient, OllamaConnectionError

class EmbeddingError(RuntimeError): pass

class OllamaEmbedder:
    def __init__(self, model='nomic-embed-text', *, base_url='http://localhost:11434', batch_size=32, timeout=120.0, client=None):
        if not model.strip(): raise ValueError('model is required')
        if batch_size<=0: raise ValueError('batch_size must be positive')
        self.model=model; self.batch_size=batch_size; self.client=client or OllamaClient(base_url=base_url,timeout=timeout)
    def embed_texts(self,texts:Sequence[str])->List[List[float]]:
        cleaned=[t.strip() for t in texts]
        if not cleaned: return []
        if any(not t for t in cleaned): raise ValueError('Embedding input cannot contain empty text')
        vectors=[]
        try:
            for start in range(0,len(cleaned),self.batch_size):
                batch=cleaned[start:start+self.batch_size]
                got=self.client.embed(model=self.model,inputs=batch)
                if len(got)!=len(batch): raise EmbeddingError('Ollama returned an unexpected number of vectors')
                dims={len(v) for v in got}
                if len(dims)!=1 or not dims: raise EmbeddingError('Ollama returned inconsistent embedding dimensions')
                if any(not v for v in got): raise EmbeddingError('Ollama returned malformed embeddings')
                vectors.extend(got)
            return vectors
        except EmbeddingError: raise
        except (OllamaConnectionError,Exception) as exc: raise EmbeddingError('local embedding generation failed') from exc
    def embed_chunks(self,chunks:Iterable[dict])->List[List[float]]: return self.embed_texts([c['text'] for c in list(chunks)])
    def check_ready(self):
        try:
            self.client.check_ready()
            if not self.client.model_available(self.model): raise EmbeddingError(f'embedding model is not installed: {self.model}')
        except EmbeddingError: raise
        except Exception as exc: raise EmbeddingError('local embedding service is not ready') from exc
