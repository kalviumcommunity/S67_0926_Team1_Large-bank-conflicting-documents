import os


def ensure_directory(path: str):
    os.makedirs(path, exist_ok=True)