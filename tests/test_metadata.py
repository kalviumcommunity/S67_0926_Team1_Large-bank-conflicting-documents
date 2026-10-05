from app.ingestion.chunker import Chunk
from app.ingestion.metadata import build_chunk_records


def test_file_format_is_not_used_as_compliance_document_type():
    chunk = Chunk(
        chunk_id="DOC-p1-c000",
        document_id="DOC",
        text="Approval required.",
        page=1,
        chunk_index=0,
        token_count=3,
    )

    records = build_chunk_records(
        {
            "filename": "DOC.pdf",
            "document_type": "pdf",
        },
        [chunk],
        document_type="circular",
        status="active",
    )

    assert records[0]["document_type"] == "circular"


def test_missing_compliance_document_type_does_not_become_pdf():
    chunk = Chunk(
        chunk_id="DOC-p1-c000",
        document_id="DOC",
        text="Approval required.",
        page=1,
        chunk_index=0,
        token_count=3,
    )

    records = build_chunk_records(
        {
            "filename": "DOC.pdf",
            "document_type": "pdf",
        },
        [chunk],
        status="unknown",
    )

    assert records[0]["document_type"] is None
