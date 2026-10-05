from __future__ import annotations

import re
from dataclasses import dataclass
from typing import FrozenSet, Iterable, Set

from app.generation.models import EvidenceItem

_CITATION_PATTERN = re.compile(r"\[E(\d+)\]")

class CitationValidationError(ValueError):
    """Raised when generated output cannot be traced to supplied evidence."""

@dataclass(frozen=True)
class CitationValidation:
    cited_ids: FrozenSet[str]
    unknown_ids: FrozenSet[str]
    missing_citation: bool
    @property
    def valid(self) -> bool:
        return not self.unknown_ids and not self.missing_citation


def validate_answer_citations(answer: str, evidence: Iterable[EvidenceItem], *, require_citation: bool = True) -> CitationValidation:
    allowed_ids: Set[str]={item.evidence_id for item in evidence}
    cited_ids={f"E{match.group(1)}" for match in _CITATION_PATTERN.finditer(answer or "")}
    unknown_ids=cited_ids-allowed_ids
    missing_citation=require_citation and bool(allowed_ids) and not cited_ids
    result=CitationValidation(frozenset(cited_ids), frozenset(unknown_ids), missing_citation)
    if result.unknown_ids:
        unknown=", ".join(sorted(result.unknown_ids))
        raise CitationValidationError(f"answer contains citations not present in retrieved evidence: {unknown}")
    if result.missing_citation:
        raise CitationValidationError("answer contains no evidence citation markers")
    return result
