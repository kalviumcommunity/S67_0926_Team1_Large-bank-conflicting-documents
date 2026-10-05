from app.config import load_settings
def test_defaults(monkeypatch):
    monkeypatch.setenv('QDRANT_URL','http://localhost:6333'); monkeypatch.delenv('OLLAMA_CHAT_MODEL',raising=False); monkeypatch.delenv('OLLAMA_EMBEDDING_MODEL',raising=False); s=load_settings(); assert s.ollama_chat_model=='gemma3:4b'; assert s.ollama_embedding_model=='nomic-embed-text'; assert s.qdrant_collection=='compliance_chunks_ollama'
