from pydantic import BaseModel
from typing import Optional


class DocumentMeta(BaseModel):
    document_type: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = "unknown"
    version: Optional[str] = None