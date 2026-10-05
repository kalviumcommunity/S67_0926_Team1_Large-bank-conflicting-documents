import pytest

from app.config import load_settings


def test_load_settings_rejects_missing_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("QDRANT_URL", "http://qdrant")
    with pytest.raises(RuntimeError):
        load_settings()


def test_load_settings_rejects_invalid_top_k(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("QDRANT_URL", "http://qdrant")
    monkeypatch.setenv("RAG_DEFAULT_TOP_K", "0")
    with pytest.raises(RuntimeError):
        load_settings()


def test_load_settings_uses_production_defaults(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("QDRANT_URL", "http://qdrant")
    monkeypatch.delenv("RAG_MODEL", raising=False)
    monkeypatch.delenv("RAG_DEFAULT_TOP_K", raising=False)
    monkeypatch.delenv("RAG_MAX_TOP_K", raising=False)
    settings = load_settings()
    assert settings.rag_model == "gpt-6-luna"
    assert settings.rag_default_top_k == 5
    assert settings.rag_max_top_k == 10
