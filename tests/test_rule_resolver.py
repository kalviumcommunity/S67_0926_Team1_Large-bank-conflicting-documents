from datetime import date

from app.retrieval.models import SearchResult
from app.retrieval.rule_resolver import CurrentRuleResolver

def result(*, chunk_id, document_id="RULE-1", version="1", effective_date="2026-01-01", status="active", score=0.8):
    return SearchResult(chunk_id=chunk_id, document_id=document_id, text=f"Rule text {chunk_id}", score=score, page=1, filename="rule.pdf", document_type="circular", title="Transaction Approval", issue_date="2025-01-01", effective_date=effective_date, status=status, version=version)

def test_latest_active_version_wins():
    old=result(chunk_id="OLD",version="1",effective_date="2026-01-01"); current=result(chunk_id="CURRENT",version="2",effective_date="2026-05-01")
    resolution=CurrentRuleResolver().resolve([old,current],as_of_date=date(2026,6,1))
    assert [item.chunk_id for item in resolution.selected]==["CURRENT"]; assert old in resolution.excluded

def test_future_effective_version_is_not_selected():
    current=result(chunk_id="CURRENT",version="2",effective_date="2026-05-01"); future=result(chunk_id="FUTURE",version="3",effective_date="2026-10-01")
    resolution=CurrentRuleResolver().resolve([current,future],as_of_date=date(2026,7,1))
    assert [item.chunk_id for item in resolution.selected]==["CURRENT"]; assert future in resolution.excluded

def test_superseded_versions_are_excluded():
    old=result(chunk_id="OLD",version="1",effective_date="2026-01-01",status="superseded"); active=result(chunk_id="NEW",version="2",effective_date="2026-04-01")
    resolution=CurrentRuleResolver().resolve([old,active],as_of_date=date(2026,6,1))
    assert [item.chunk_id for item in resolution.selected]==["NEW"]; assert old in resolution.excluded

def test_multiple_chunks_from_selected_version_are_retained():
    a=result(chunk_id="C1",version="2",effective_date="2026-05-01",score=0.9); b=result(chunk_id="C2",version="2",effective_date="2026-05-01",score=0.7); old=result(chunk_id="OLD",version="1",effective_date="2026-01-01",score=0.95)
    resolution=CurrentRuleResolver().resolve([a,b,old],as_of_date=date(2026,6,1))
    assert {item.chunk_id for item in resolution.selected}=={"C1","C2"}

def test_no_active_version_means_no_current_rule():
    old=result(chunk_id="OLD",version="1",effective_date="2026-01-01",status="superseded")
    resolution=CurrentRuleResolver().resolve([old],as_of_date=date(2026,6,1))
    assert resolution.selected==[]; assert resolution.has_current_rule is False
