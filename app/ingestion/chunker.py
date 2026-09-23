from dataclasses import dataclass
from typing import List, Optional

import tiktoken


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    page: Optional[int]
    chunk_index: int
    token_count: int


class TokenAwareChunker:
    def __init__(self, model_name: str = "gpt-4o-mini", chunk_size: int = 700, overlap: int = 100):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be >= 0 and smaller than chunk_size")
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_page(self, document_id: str, text: str, page: Optional[int], start_index: int = 0) -> List[Chunk]:
        tokens = self.encoding.encode(text)
        if not tokens:
            return []
        chunks: List[Chunk] = []
        start = 0
        index = start_index
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunks.append(
                Chunk(
                    chunk_id=f"{document_id}-p{page or 0}-c{index:03d}",
                    document_id=document_id,
                    text=self.encoding.decode(chunk_tokens).strip(),
                    page=page,
                    chunk_index=index,
                    token_count=len(chunk_tokens),
                )
            )
            if end == len(tokens):
                break
            start = end - self.overlap
            index += 1
        return chunks
