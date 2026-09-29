import shutil
from fastapi import UploadFile


def save_file(file: UploadFile, path: str):
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)