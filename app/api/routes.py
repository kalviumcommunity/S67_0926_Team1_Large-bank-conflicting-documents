from datetime import date
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.ingestion_service import (
    DocumentIngestionService,
    DocumentProcessingInProgressError,
    DuplicateDocumentError,
    IngestionServiceError,
    InvalidDocumentMetadataError,
    UnsupportedDocumentError,
    build_default_ingestion_service,
)

router = APIRouter(prefix="/api", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    issue_date: Optional[date] = Form(None),
    effective_date: Optional[date] = Form(None),
    status: str = Form("unknown"),
    version: Optional[str] = Form(None),
    document_id: Optional[str] = Form(None),
):
    metadata = {
        "document_type": document_type,
        "title": title,
        "issue_date": issue_date.isoformat() if issue_date else None,
        "effective_date": (
            effective_date.isoformat()
            if effective_date
            else None
        ),
        "status": status,
        "version": version,
        "document_id": document_id,
    }
    metadata = {
        key: value
        for key, value in metadata.items()
        if value is not None
    }

    try:
        service = build_default_ingestion_service()
        return await service.process_document(
            file,
            metadata=metadata,
        )

    except InvalidDocumentMetadataError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except UnsupportedDocumentError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except DuplicateDocumentError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "document has already been ingested",
                "document_id": exc.record.get("document_id"),
                "status": exc.record.get("status"),
            },
        ) from exc

    except DocumentProcessingInProgressError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "document ingestion is already in progress",
                "document_id": exc.record.get("document_id"),
            },
        ) from exc

    except IngestionServiceError as exc:
        raise HTTPException(
            status_code=500,
            detail="document ingestion failed",
        ) from exc


@router.get("/documents/{document_id}/status")
def document_status(document_id: str):
    try:
        service = build_default_ingestion_service()
        record = service.get_status(document_id)

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="document not found",
            )

        # Do not expose stored paths or raw processing errors.
        return {
            "document_id": record["document_id"],
            "filename": record["filename"],
            "status": record["status"],
            "chunk_count": record["chunk_count"],
            "indexed_count": record["indexed_count"],
            "version": record["version"],
            "updated_at": record["updated_at"],
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="document status lookup failed",
        ) from exc


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/ready")
def readiness_check():
    try:
        service = build_default_ingestion_service()
        service.check_ready()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="ingestion dependencies are not ready",
        ) from exc

    return {"status": "ready"}
