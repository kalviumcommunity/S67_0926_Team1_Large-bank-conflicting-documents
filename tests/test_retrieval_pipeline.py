from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.reranker import RelevanceReranker
from app.retrieval.models import SearchResult


def test_pipeline_connects_hybrid_and_reranking():
    class FakeHybrid:
        candidate_k = 3

        def search(self, query, *, top_k, filters=None):
            return [
                SearchResult(
                    chunk_id="A",
                    document_id="DOC1",
                    text="approval transaction",
                    score=0.5,
                    page=1,
                    filename="DOC1.pdf",
                    document_type="circular",
                    title="Rule",
                    issue_date=None,
                    effective_date=None,
                    status="active",
                    version="1",
                )
            ]

    pipeline = RetrievalPipeline(FakeHybrid(), RelevanceReranker())
    results = pipeline.search("approval", top_k=1)
    assert len(results) == 1
    assert results[0].chunk_id == "A"
