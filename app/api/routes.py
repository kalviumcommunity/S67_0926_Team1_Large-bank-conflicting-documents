from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion_service import process_document

router = APIRouter(prefix="/api", tags=["Documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        result = await process_document(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    return {"status": "ok"}