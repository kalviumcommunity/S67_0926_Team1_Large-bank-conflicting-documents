from dataclasses import dataclass
from typing import List

from app.retrieval.models import SearchResult


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    result: SearchResult


@dataclass(frozen=True)
class RagResponse:
    query: str
    answer: str
    evidence: List[EvidenceItem]

    @property
    def used_chunk_ids(self) -> List[str]:
        return [item.result.chunk_id for item in self.evidence]

    def as_dict(self):
        return {
            "query": self.query,
            "answer": self.answer,
            "used_chunk_ids": self.used_chunk_ids,
            "evidence": [
                {
                    "evidence_id": item.evidence_id,
                    **item.result.as_dict(),
                }
                for item in self.evidence
            ],
        }
