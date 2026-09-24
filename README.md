# Backend

FastAPI backend for document ingestion.

## Run locally

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```powershell
pytest
```

Add ingestion implementation under `app/ingestion/`.
