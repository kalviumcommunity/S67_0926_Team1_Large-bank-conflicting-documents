from app.ingestion.batch import (
    BatchIngestionReport,
    DocumentRunResult,
    discover_documents,
    ingest_batch,
)
from app.ingestion.manifest import build_manifest, write_manifest


def test_discover_documents_is_deterministic(tmp_path):
    (tmp_path / "b.pdf").write_bytes(b"pdf")
    (tmp_path / "A.docx").write_bytes(b"docx")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    discovered = discover_documents(str(tmp_path))

    assert [path.name for path in discovered] == ["A.docx", "b.pdf"]


def test_discover_missing_directory_fails(tmp_path):
    missing = tmp_path / "does-not-exist"

    try:
        discover_documents(str(missing))
    except FileNotFoundError:
        return

    assert False, "Expected FileNotFoundError"


def test_ingest_batch_isolates_document_failure(tmp_path, monkeypatch):
    first = tmp_path / "good.pdf"
    second = tmp_path / "bad.pdf"
    first.write_bytes(b"good")
    second.write_bytes(b"bad")

    def fake_ingest(path, **kwargs):
        if path.endswith("bad.pdf"):
            raise ValueError("invalid source")
        return [
            {
                "document_id": "DOC1",
                "chunk_id": "DOC1-p1-c000",
                "text": "rule",
            }
        ]

    monkeypatch.setattr("app.ingestion.batch.ingest_document", fake_ingest)

    records, report = ingest_batch(str(tmp_path))

    assert len(records) == 1
    assert report.processed_files == 1
    assert report.failed_files == 1
    failed_result = next(result for result in report.results if result.status == "failed")
    assert failed_result.filename == "bad.pdf"
    assert failed_result.error == "invalid source"


def test_manifest_is_deterministic():
    records = [
        {"document_id": "DOC2", "chunk_id": "C2", "text": "b"},
        {"document_id": "DOC1", "chunk_id": "C1", "text": "a"},
        {"document_id": "DOC2", "chunk_id": "C3", "text": "c"},
    ]

    report = BatchIngestionReport(
        total_files=2,
        processed_files=2,
        failed_files=0,
        skipped_files=0,
        results=[
            DocumentRunResult(filename="a.pdf", status="processed", chunk_count=1),
            DocumentRunResult(filename="b.pdf", status="processed", chunk_count=2),
        ],
    )

    manifest = build_manifest(records, report)

    assert manifest["document_ids"] == ["DOC1", "DOC2"]
    assert manifest["total_chunks"] == 3


def test_manifest_can_be_written(tmp_path):
    report = BatchIngestionReport(
        total_files=1,
        processed_files=1,
        failed_files=0,
        skipped_files=0,
        results=[
            DocumentRunResult(
                filename="a.pdf",
                status="processed",
                chunk_count=1,
            )
        ],
    )

    output = tmp_path / "manifest.json"

    write_manifest(
        build_manifest(
            [{"document_id": "DOC1", "chunk_id": "C1"}],
            report,
        ),
        str(output),
    )

    assert output.exists()
    assert '"schema_version": "1"' in output.read_text(encoding="utf-8")
