import app.services.rag_application as app


def test_factory_uses_ollama(monkeypatch):
    class Settings:
        ollama_base_url = "http://ollama"
        ollama_chat_model = "gemma3:4b"
        ollama_embedding_model = "nomic-embed-text"
        ollama_timeout_seconds = 120.0
        embedding_batch_size = 32
        qdrant_url = "http://q"
        qdrant_api_key = None
        qdrant_collection = "compliance_chunks_ollama"
        rag_default_top_k = 5
        rag_max_top_k = 10

    class X:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(app, "load_settings", lambda: Settings())
    monkeypatch.setattr(app, "OllamaClient", X)
    monkeypatch.setattr(app, "OllamaEmbedder", X)
    monkeypatch.setattr(app, "QdrantVectorStore", X)
    monkeypatch.setattr(app, "OllamaLLMProvider", X)

    app.get_rag_service.cache_clear()
    assert app.get_rag_service() is not None
    app.get_rag_service.cache_clear()
