from pathlib import Path
from typing import Dict

import fitz
from docx import Document

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def load_document(file_path: str) -> Dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {path.suffix}. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )
    if path.suffix.lower() == ".pdf":
        return _load_pdf(path)
    return _load_docx(path)


def _load_pdf(path: Path) -> Dict:
    pages = []
    with fitz.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            pages.append({"page": page_number, "text": page.get_text("text")})
    return {
        "document_id": path.stem,
        "filename": path.name,
        "document_type": "pdf",
        "pages": pages,
    }


def _load_docx(path: Path) -> Dict:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return {
        "document_id": path.stem,
        "filename": path.name,
        "document_type": "docx",
        "pages": [{"page": None, "text": "\n".join(paragraphs)}],
    }
