import pytest

from app.validation.document_validator import (
    DocumentValidationError,
    quality_check_document,
    validate_chunk_records,
)


def _document():
    return {
        "document_id": "CIRC-2026-001",
        "filename": "CIRC-2026-001.pdf",
        "pages": [{"page": 1, "text": "Approval is required."}],
    }


def _chunks():
    return [
        {
            "chunk_id": "CIRC-2026-001-p1-c000",
            "text": "Approval is required.",
            "token_count": 5,
        }
    ]


def test_valid_document_metadata_passes():
    metadata = {
        "document_type": "circular",
        "title": "Transaction Approval Requirements",
        "issue_date": "2026-04-01",
        "effective_date": "2026-04-15",
        "status": "active",
        "version": "1",
    }

    normalized = quality_check_document(_document(), metadata, _chunks())

    assert normalized.status == "active"
    assert normalized.document_type == "circular"


def test_invalid_status_fails():
    with pytest.raises(DocumentValidationError):
        quality_check_document(_document(), {"status": "invalid"}, _chunks())


def test_effective_date_before_issue_date_fails():
    with pytest.raises(DocumentValidationError):
        quality_check_document(
            _document(),
            {"issue_date": "2026-04-15", "effective_date": "2026-04-01"},
            _chunks(),
        )


def test_empty_document_fails():
    document = _document()
    document["pages"] = [{"page": 1, "text": "   "}]

    with pytest.raises(DocumentValidationError):
        quality_check_document(document, {}, _chunks())


def test_empty_chunks_fail():
    with pytest.raises(DocumentValidationError):
        validate_chunk_records([])


def test_duplicate_chunk_ids_fail():
    with pytest.raises(DocumentValidationError):
        validate_chunk_records(_chunks() * 2)


def test_document_id_mismatch_fails():
    with pytest.raises(DocumentValidationError):
        quality_check_document(
            _document(),
            {"document_id": "OTHER-DOC"},
            _chunks(),
        )
