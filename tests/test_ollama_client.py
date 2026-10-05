import json
from app.ollama.client import OllamaClient
class Resp:
    def __init__(self,p): self.p=json.dumps(p).encode()
    def read(self): return self.p
    def __enter__(self): return self
    def __exit__(self,*args): pass
def make(payloads):
    calls=[]
    def opener(req,timeout): calls.append((req,timeout)); return Resp(payloads[len(calls)-1])
    return opener,calls
def test_embed_batch():
    opener,calls=make([{'embeddings':[[0.1,0.2],[0.3,0.4]]}]); c=OllamaClient(opener=opener); assert c.embed(model='nomic-embed-text',inputs=['a','b'])==[[0.1,0.2],[0.3,0.4]]; assert '/api/embed' in calls[0][0].full_url
def test_generate():
    opener,calls=make([{'message':{'content':'Answer [E1].'}}]); c=OllamaClient(opener=opener); assert c.generate(model='gemma3:4b',system='s',prompt='p')=='Answer [E1].'; assert '/api/chat' in calls[0][0].full_url
def test_model_available():
    opener,calls=make([{'models':[{'name':'gemma3:4b'},{'name':'nomic-embed-text:latest'}]},{'models':[{'name':'gemma3:4b'},{'name':'nomic-embed-text:latest'}]}]); c=OllamaClient(opener=opener); assert c.model_available('gemma3:4b'); assert c.model_available('nomic-embed-text')
