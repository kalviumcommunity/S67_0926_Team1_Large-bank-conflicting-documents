from datetime import date
import pytest
from app.generation.service import RagGenerationError, RagService
from app.retrieval.models import SearchResult

def result(chunk_id,version,effective_date,status="active"):
    return SearchResult(chunk_id=chunk_id,document_id="RULE-1",text=f"Approval requirement for version {version}.",score=0.9,page=4,filename="rule.pdf",document_type="circular",title="Approval Rule",issue_date="2026-01-01",effective_date=effective_date,status=status,version=version)

class FakeRetriever:
    def __init__(self,results): self.results=results
    def search(self,query,*,top_k,filters=None): return self.results[:top_k]

class FakeLLM:
    def __init__(self,answer="Approval is required [E1]."): self.answer=answer; self.calls=[]
    def generate(self,instructions,user_input): self.calls.append((instructions,user_input)); return self.answer

def test_rag_service_generates_from_current_version_only():
    retriever=FakeRetriever([result("OLD","1","2026-01-01"),result("CURRENT","2","2026-05-01")]); llm=FakeLLM()
    response=RagService(retriever,llm).answer("What is required?",as_of_date=date(2026,6,1))
    assert response.used_chunk_ids==["CURRENT"]; assert "[E1]" in response.answer; assert "CURRENT" in llm.calls[0][1]; assert "OLD" not in llm.calls[0][1]

def test_rag_service_rejects_uncited_llm_output():
    retriever=FakeRetriever([result("CURRENT","2","2026-05-01")]); llm=FakeLLM(answer="Approval is required.")
    with pytest.raises(RagGenerationError): RagService(retriever,llm).answer("What is required?",as_of_date=date(2026,6,1))

def test_rag_service_reports_no_current_rule():
    retriever=FakeRetriever([result("OLD","1","2026-01-01",status="superseded")]); llm=FakeLLM()
    response=RagService(retriever,llm).answer("What is required?",as_of_date=date(2026,6,1))
    assert response.evidence==[]; assert "current applicable rule" in response.answer; assert llm.calls==[]
