from __future__ import annotations
import hashlib
from typing import Dict, Iterable, List
from qdrant_client import QdrantClient
from qdrant_client.http import models
class QdrantVectorStore:
    def __init__(self,url,collection_name,api_key=None,vector_size=None,client=None):
        if not url: raise ValueError('QDRANT_URL is required')
        if not collection_name: raise ValueError('collection_name is required')
        if vector_size is not None and vector_size<=0: raise ValueError('vector_size must be positive')
        self.collection_name=collection_name; self.vector_size=vector_size; self.client=client or QdrantClient(url=url,api_key=api_key)
    def check_connection(self):
        try:
            if hasattr(self.client,'get_collections'): self.client.get_collections()
            else: self.client.collection_exists(self.collection_name)
        except Exception as exc: raise RuntimeError('Qdrant is not reachable') from exc
    def ensure_collection(self,*,vector_size=None):
        requested=vector_size or self.vector_size
        if self.client.collection_exists(self.collection_name):
            info=self.client.get_collection(self.collection_name); actual=_collection_vector_size(info)
            if requested is not None and actual!=requested: raise ValueError(f'Qdrant collection vector dimension does not match the active embedding model: expected {requested}, found {actual}')
            self.vector_size=actual; return
        if requested is None: raise ValueError('vector_size must be known before creating the collection')
        self.vector_size=requested
        self.client.create_collection(collection_name=self.collection_name,vectors_config=models.VectorParams(size=requested,distance=models.Distance.COSINE))
    def upsert_chunks(self,chunks:Iterable[Dict],embeddings:List[List[float]]):
        chunk_list=list(chunks)
        if len(chunk_list)!=len(embeddings): raise ValueError('Number of chunks must match number of embeddings')
        if not chunk_list: return
        if self.vector_size is None: raise ValueError('vector size has not been initialized')
        points=[]
        for chunk,vector in zip(chunk_list,embeddings):
            if len(vector)!=self.vector_size: raise ValueError(f'Expected vector size {self.vector_size}, received {len(vector)}')
            points.append(models.PointStruct(id=_stable_point_id(chunk['chunk_id']),vector=vector,payload={k:v for k,v in chunk.items() if k!='embedding'}))
        self.client.upsert(collection_name=self.collection_name,points=points,wait=True)
def _collection_vector_size(info):
    vectors=getattr(info.config.params,'vectors',None)
    if isinstance(vectors,dict):
        values=list(vectors.values())
        if len(values)!=1: raise ValueError('named Qdrant vectors are not supported by this RAG pipeline')
        return int(values[0].size)
    size=getattr(vectors,'size',None)
    if size is None: raise ValueError('unable to determine Qdrant vector dimension')
    return int(size)
def _stable_point_id(chunk_id):
    digest=hashlib.sha256(chunk_id.encode()).digest(); return int.from_bytes(digest[:8],'big') & ((1<<63)-1)
