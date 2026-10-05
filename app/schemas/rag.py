from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)
    as_of_date: Optional[date] = None
    document_type: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default=None, max_length=50)
    document_id: Optional[str] = Field(default=None, max_length=200)
    version: Optional[str] = Field(default=None, max_length=100)
    effective_date: Optional[date] = None


class RagEvidenceResponse(BaseModel):
    evidence_id: str
    chunk_id: str
    document_id: str
    text: str
    score: float
    page: Optional[int] = None
    filename: Optional[str] = None
    document_type: Optional[str] = None
    title: Optional[str] = None
    issue_date: Optional[str] = None
    effective_date: Optional[str] = None
    status: Optional[str] = None
    version: Optional[str] = None


class RagQueryResponse(BaseModel):
    query: str
    answer: str
    used_chunk_ids: List[str]
    evidence: List[RagEvidenceResponse]
