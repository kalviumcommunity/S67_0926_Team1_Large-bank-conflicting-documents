from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class SearchFilters:
    document_type: Optional[str] = None
    status: Optional[str] = None
    document_id: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[str] = None


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    document_id: str
    text: str
    score: float
    page: Optional[int]
    filename: Optional[str]
    document_type: Optional[str]
    title: Optional[str]
    issue_date: Optional[str]
    effective_date: Optional[str]
    status: Optional[str]
    version: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "score": self.score,
            "page": self.page,
            "filename": self.filename,
            "document_type": self.document_type,
            "title": self.title,
            "issue_date": self.issue_date,
            "effective_date": self.effective_date,
            "status": self.status,
            "version": self.version,
        }
