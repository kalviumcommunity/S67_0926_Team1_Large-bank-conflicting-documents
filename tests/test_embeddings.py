from types import SimpleNamespace
import pytest

from app.embeddings.embedder import EmbeddingError, OpenAIEmbedder


class FakeEmbeddingsAPI:
    def __init__(self):
        self.calls = []

    def create(self, *, model, input):
        self.calls.append((model, list(input)))
        return SimpleNamespace(
            data=[
                SimpleNamespace(index=i, embedding=[float(i), 1.0])
                for i in range(len(input))
            ]
        )


class FakeClient:
    def __init__(self):
        self.embeddings = FakeEmbeddingsAPI()


def test_embed_texts_batches_requests():
    client = FakeClient()
    embedder = OpenAIEmbedder(api_key="test", batch_size=2, client=client)
    vectors = embedder.embed_texts(["one", "two", "three", "four", "five"])
    assert len(vectors) == 5
    assert [len(batch) for _, batch in client.embeddings.calls] == [2, 2, 1]


def test_embed_texts_rejects_empty_text():
    embedder = OpenAIEmbedder(api_key="test", client=FakeClient())
    with pytest.raises(ValueError):
        embedder.embed_texts(["valid", ""])


def test_embed_texts_wraps_api_failure():
    class BrokenAPI:
        def create(self, **kwargs):
            raise RuntimeError("network failure")
    client = SimpleNamespace(embeddings=BrokenAPI())
    embedder = OpenAIEmbedder(api_key="test", client=client)
    with pytest.raises(EmbeddingError):
        embedder.embed_texts(["hello"])


def test_embed_texts_empty_input():
    embedder = OpenAIEmbedder(api_key="test", client=FakeClient())
    assert embedder.embed_texts([]) == []
