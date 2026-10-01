from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.ingestion.pipeline import ingest_document


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


@dataclass(frozen=True)
class DocumentRunResult:
    filename: str
    status: str
    chunk_count: int = 0
    error: Optional[str] = None

    def as_dict(self) -> Dict:
        return asdict(self)


@dataclass(frozen=True)
class BatchIngestionReport:
    total_files: int
    processed_files: int
    failed_files: int
    skipped_files: int
    results: List[DocumentRunResult]

    def as_dict(self) -> Dict:
        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "skipped_files": self.skipped_files,
            "results": [result.as_dict() for result in self.results],
        }


def discover_documents(input_dir: str) -> List[Path]:
    directory = Path(input_dir)

    if not directory.exists():
        raise FileNotFoundError(f"input directory does not exist: {input_dir}")

    if not directory.is_dir():
        raise NotADirectoryError(f"input path is not a directory: {input_dir}")

    return sorted(
        [
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ],
        key=lambda path: path.name.lower(),
    )


def ingest_batch(
    input_dir: str,
    *,
    chunk_size: int = 700,
    overlap: int = 100,
    metadata_by_filename: Optional[Dict[str, Dict]] = None,
) -> Tuple[List[Dict], BatchIngestionReport]:
    metadata_by_filename = metadata_by_filename or {}
    documents = discover_documents(input_dir)

    records: List[Dict] = []
    results: List[DocumentRunResult] = []

    for path in documents:
        filename = path.name

        try:
            chunks = ingest_document(
                str(path),
                chunk_size=chunk_size,
                overlap=overlap,
                metadata=metadata_by_filename.get(filename),
            )

            records.extend(chunks)
            results.append(
                DocumentRunResult(
                    filename=filename,
                    status="processed",
                    chunk_count=len(chunks),
                )
            )
        except Exception as exc:
            results.append(
                DocumentRunResult(
                    filename=filename,
                    status="failed",
                    error=str(exc),
                )
            )

    report = BatchIngestionReport(
        total_files=len(documents),
        processed_files=sum(r.status == "processed" for r in results),
        failed_files=sum(r.status == "failed" for r in results),
        skipped_files=sum(r.status == "skipped" for r in results),
        results=results,
    )

    return records, report
