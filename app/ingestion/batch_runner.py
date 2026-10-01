from typing import Dict, Optional

from app.ingestion.batch import ingest_batch
from app.ingestion.manifest import build_manifest, write_manifest


def run_batch(
    input_dir: str,
    *,
    manifest_path: Optional[str] = None,
    chunk_size: int = 700,
    overlap: int = 100,
    metadata_by_filename: Optional[Dict[str, Dict]] = None,
):
    records, report = ingest_batch(
        input_dir,
        chunk_size=chunk_size,
        overlap=overlap,
        metadata_by_filename=metadata_by_filename,
    )

    manifest = build_manifest(records, report)

    if manifest_path:
        write_manifest(manifest, manifest_path)

    return records, report, manifest


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch-ingest a compliance document corpus."
    )
    parser.add_argument("input_dir")
    parser.add_argument(
        "--manifest",
        default="data/processed/ingestion_manifest.json",
    )

    args = parser.parse_args()

    _, report, manifest = run_batch(
        args.input_dir,
        manifest_path=args.manifest,
    )

    print(
        f"Processed={report.processed_files} "
        f"Failed={report.failed_files} "
        f"Skipped={report.skipped_files}"
    )
    print(f"Chunks={manifest['total_chunks']}")
