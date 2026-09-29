from typing import Dict, Iterable, Set

from app.schemas.document import DocumentMeta


class DocumentValidationError(ValueError):
    """Raised when a document fails the production quality gate."""


def validate_document_metadata(metadata: Dict) -> DocumentMeta:
    try:
        return DocumentMeta(**metadata)
    except Exception as exc:
        raise DocumentValidationError(str(exc)) from exc


def validate_document_content(document: Dict) -> None:
    document_id = document.get("document_id")
    filename = document.get("filename")
    pages = document.get("pages")

    if not document_id:
        raise DocumentValidationError("document_id is required")
    if not filename:
        raise DocumentValidationError("filename is required")
    if not isinstance(pages, list) or not pages:
        raise DocumentValidationError("document must contain at least one page")

    usable_text = [
        page.get("text", "").strip()
        for page in pages
        if isinstance(page, dict)
    ]

    if not any(usable_text):
        raise DocumentValidationError("document contains no usable text")


def validate_chunk_records(chunks: Iterable[Dict]) -> None:
    chunks = list(chunks)

    if not chunks:
        raise DocumentValidationError("no chunks were produced")

    seen_chunk_ids: Set[str] = set()

    for chunk in chunks:
        chunk_id = chunk.get("chunk_id")
        text = chunk.get("text", "")
        token_count = chunk.get("token_count")

        if not chunk_id:
            raise DocumentValidationError("chunk_id is required")
        if chunk_id in seen_chunk_ids:
            raise DocumentValidationError(
                f"duplicate chunk_id detected: {chunk_id}"
            )
        if not isinstance(text, str) or not text.strip():
            raise DocumentValidationError(
                f"chunk {chunk_id} contains empty text"
            )
        if not isinstance(token_count, int) or token_count <= 0:
            raise DocumentValidationError(
                f"chunk {chunk_id} has invalid token_count"
            )

        seen_chunk_ids.add(chunk_id)


def quality_check_document(document: Dict, metadata: Dict, chunks: Iterable[Dict]):
    validate_document_content(document)
    normalized_metadata = validate_document_metadata(metadata)
    validate_chunk_records(chunks)

    if normalized_metadata.document_id:
        if normalized_metadata.document_id != document["document_id"]:
            raise DocumentValidationError(
                "metadata document_id does not match document document_id"
            )

    return normalized_metadata
