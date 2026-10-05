import app.services.rag_application as rag_application


def test_rag_service_factory_is_cached(monkeypatch):
    class Settings:
        openai_api_key = "test"
        embedding_model = "text-embedding-3-small"
        embedding_batch_size = 2
        qdrant_url = "http://qdrant"
        qdrant_api_key = None
        qdrant_collection = "compliance_chunks"
        embedding_dimensions = 1536
        rag_model = "gpt-6-luna"
        rag_default_top_k = 5
        rag_max_top_k = 10
        openai_timeout_seconds = 60.0
        openai_max_retries = 2
    monkeypatch.setattr(rag_application, "load_settings", lambda: Settings())
    monkeypatch.setattr(rag_application, "OpenAIEmbedder", lambda **kwargs: object())
    monkeypatch.setattr(rag_application, "QdrantVectorStore", lambda **kwargs: object())
    monkeypatch.setattr(rag_application, "OpenAIResponsesProvider", lambda **kwargs: object())
    rag_application.get_rag_service.cache_clear()
    first = rag_application.get_rag_service()
    second = rag_application.get_rag_service()
    assert first is second
    rag_application.get_rag_service.cache_clear()
