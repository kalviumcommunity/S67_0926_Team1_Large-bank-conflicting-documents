from app.config import load_settings
from app.embeddings.embedder import OllamaEmbedder
from app.ingestion.pipeline import ingest_document
from app.vectorstore.indexer import DocumentIndexer
from app.vectorstore.qdrant import QdrantVectorStore

def main():
    settings=load_settings()
    embedder=OllamaEmbedder(model=settings.ollama_embedding_model,base_url=settings.ollama_base_url,batch_size=settings.embedding_batch_size,timeout=settings.ollama_timeout_seconds)
    store=QdrantVectorStore(url=settings.qdrant_url,collection_name=settings.qdrant_collection,api_key=settings.qdrant_api_key)
    records=ingest_document('data/raw/CIRC-2026-001.pdf',metadata={'document_type':'circular','status':'active','version':'1'})
    count=DocumentIndexer(embedder,store).index_chunks(records)
    print(f'Indexed {count} chunks into {settings.qdrant_collection}')
if __name__=='__main__': main()
