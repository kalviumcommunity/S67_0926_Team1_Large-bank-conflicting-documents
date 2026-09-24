import os
import shutil
from fastapi import UploadFile

from app.services.storage_service import save_file

UPLOAD_DIR = "data/uploads"


async def process_document(file: UploadFile):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    save_file(file, file_path)

    # Placeholder response (future: call ingestion pipeline)
    return {
        "filename": file.filename,
        "status": "uploaded",
        "message": "Document stored successfully. Processing will be added in next PR.",
    }