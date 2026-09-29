from app.retrieval.models import SearchFilters, SearchResult


def test_search_result_serialization():
    result = SearchResult(
        chunk_id="C1",
        document_id="DOC1",
        text="Approval is required.",
        score=0.91,
        page=3,
        filename="DOC1.pdf",
        document_type="circular",
        title="Approval Rule",
        issue_date="2026-01-01",
        effective_date="2026-01-15",
        status="active",
        version="1",
    )

    data = result.as_dict()

    assert data["chunk_id"] == "C1"
    assert data["score"] == 0.91
    assert data["effective_date"] == "2026-01-15"


def test_search_filters_are_optional():
    filters = SearchFilters()
    assert filters.document_type is None
    assert filters.status is None
