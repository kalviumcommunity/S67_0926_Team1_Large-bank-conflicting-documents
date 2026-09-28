from dotenv import load_dotenv

from app.config import load_settings
from app.embeddings.embedder import OpenAIEmbedder
from app.ingestion.pipeline import ingest_document
from app.vectorstore.indexer import DocumentIndexer
from app.vectorstore.qdrant import QdrantVectorStore


def main() -> None:
    load_dotenv()
    settings = load_settings()

    chunks = ingest_document(
        "data/raw/CIRC-2026-001.pdf",
        metadata={
            "document_type": "circular",
            "title": "Transaction Approval Requirements",
            "status": "active",
            "version": "1",
        },
    )

    embedder = OpenAIEmbedder(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
        batch_size=settings.embedding_batch_size,
    )
    store = QdrantVectorStore(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection,
        vector_size=settings.embedding_dimensions,
    )
    indexed = DocumentIndexer(embedder, store).index_chunks(chunks)
    print(f"Indexed {indexed} chunks into '{settings.qdrant_collection}'.")


if __name__ == "__main__":
    main()
