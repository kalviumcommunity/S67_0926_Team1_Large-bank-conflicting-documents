from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import RequestIdMiddleware
from app.api.rag_routes import router as rag_router
from app.api.routes import router
from app.config import load_cors_origins


app = FastAPI(title="Bank Compliance RAG API", version="1.0.0")
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(load_cors_origins()),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(rag_router)


@app.get("/")
def root():
    return {"message": "Bank Compliance RAG API", "version": "1.0.0"}
