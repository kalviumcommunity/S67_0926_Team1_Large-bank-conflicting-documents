import pytest
from app.generation.citations import CitationValidationError, validate_answer_citations
from app.generation.models import EvidenceItem
from app.retrieval.models import SearchResult

def evidence_item(evidence_id):
    result=SearchResult(chunk_id=f"C-{evidence_id}",document_id="DOC-1",text="Approval is required.",score=0.9,page=2,filename="doc.pdf",document_type="circular",title="Approval Rule",issue_date="2026-01-01",effective_date="2026-01-15",status="active",version="1")
    return EvidenceItem(evidence_id=evidence_id,result=result)

def test_valid_citation_is_accepted():
    result=validate_answer_citations("Approval is required [E1].",[evidence_item("E1")]); assert result.valid; assert result.cited_ids==frozenset({"E1"})

def test_unknown_citation_is_rejected():
    with pytest.raises(CitationValidationError): validate_answer_citations("Approval is required [E99].",[evidence_item("E1")])

def test_missing_citation_is_rejected():
    with pytest.raises(CitationValidationError): validate_answer_citations("Approval is required.",[evidence_item("E1")])

def test_multiple_valid_citations_are_supported():
    result=validate_answer_citations("Approval is required [E1], subject to the document [E2].",[evidence_item("E1"),evidence_item("E2")]); assert result.valid; assert result.cited_ids==frozenset({"E1","E2"})
