import pytest
from app.embeddings.embedder import EmbeddingError,OllamaEmbedder
class Fake:
    def __init__(self): self.calls=[]
    def embed(self,*,model,inputs): self.calls.append(list(inputs)); return [[float(i),1.0] for i,_ in enumerate(inputs)]
    def check_ready(self): pass
    def model_available(self,model): return True
def test_batching():
    c=Fake(); e=OllamaEmbedder(batch_size=2,client=c); assert len(e.embed_texts(['a','b','c','d','e']))==5; assert [len(x) for x in c.calls]==[2,2,1]
def test_empty_rejected():
    with pytest.raises(ValueError): OllamaEmbedder(client=Fake()).embed_texts(['ok',''])
def test_empty_input(): assert OllamaEmbedder(client=Fake()).embed_texts([])==[]
def test_bad_dimensions():
    class Broken(Fake):
        def embed(self,*,model,inputs): return [[0.1],[0.2,0.3]]
    with pytest.raises(EmbeddingError): OllamaEmbedder(client=Broken()).embed_texts(['a','b'])
