from types import SimpleNamespace
import pytest
from app.vectorstore.qdrant import QdrantVectorStore
class Client:
    def __init__(self,exists=False,size=1536): self.exists=exists; self.size=size; self.created=None
    def collection_exists(self,name): return self.exists
    def create_collection(self,**kwargs): self.created=kwargs
    def get_collection(self,name): return SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(vectors=SimpleNamespace(size=self.size))))
def test_create_uses_embedding_dimension():
    c=Client(); QdrantVectorStore('http://q','local',client=c).ensure_collection(vector_size=768); assert c.created['vectors_config'].size==768
def test_existing_mismatch_fails():
    with pytest.raises(ValueError): QdrantVectorStore('http://q','local',client=Client(True,1536)).ensure_collection(vector_size=768)
