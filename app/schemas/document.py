from datetime import date
from typing import Optional

from pydantic import BaseModel, validator


ALLOWED_DOCUMENT_TYPES = {
    "circular",
    "audit_report",
    "regulatory_update",
    "policy",
}
ALLOWED_STATUSES = {
    "active",
    "superseded",
    "draft",
    "archived",
    "unknown",
}


class DocumentMeta(BaseModel):
    document_type: Optional[str] = None
    title: Optional[str] = None
    issue_date: Optional[date] = None
    effective_date: Optional[date] = None
    status: str = "unknown"
    version: Optional[str] = None
    document_id: Optional[str] = None

    @validator("document_type")
    def validate_document_type(cls, value):
        if value is not None and value not in ALLOWED_DOCUMENT_TYPES:
            raise ValueError(
                f"document_type must be one of {sorted(ALLOWED_DOCUMENT_TYPES)}"
            )
        return value

    @validator("status")
    def validate_status(cls, value):
        if value not in ALLOWED_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(ALLOWED_STATUSES)}"
            )
        return value

    @validator("title", "version", "document_id")
    def validate_non_blank_strings(cls, value):
        if value is not None and not value.strip():
            raise ValueError("value cannot be blank")
        return value

    @validator("effective_date")
    def validate_effective_date(cls, value, values):
        issue_date = values.get("issue_date")
        if value is not None and issue_date is not None and value < issue_date:
            raise ValueError("effective_date cannot be before issue_date")
        return value

    class Config:
        anystr_strip_whitespace = True
