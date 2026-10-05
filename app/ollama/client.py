from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

class OllamaConnectionError(RuntimeError):
    pass

@dataclass(frozen=True)
class OllamaResponse:
    payload: Dict[str, Any]

class OllamaClient:
    def __init__(self, base_url='http://localhost:11434', *, timeout=120.0, opener:Callable[...,Any]=urlopen):
        base_url=base_url.strip().rstrip('/')
        if not base_url: raise ValueError('OLLAMA_BASE_URL is required')
        if timeout<=0: raise ValueError('timeout must be positive')
        self.base_url=base_url; self.timeout=timeout; self._opener=opener
    def generate(self, *, model, system, prompt, temperature=0.0):
        p=self._post('/api/chat', {'model':model,'stream':False,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}],'options':{'temperature':temperature}}).payload
        content=str((p.get('message') or {}).get('content') or '').strip()
        if not content: raise OllamaConnectionError('Ollama returned an empty generation')
        return content
    def embed(self, *, model, inputs):
        p=self._post('/api/embed', {'model':model,'input':inputs}).payload
        embeddings=p.get('embeddings')
        if not isinstance(embeddings,list): raise OllamaConnectionError('Ollama returned an invalid embedding response')
        return [[float(v) for v in vec] for vec in embeddings]
    def model_available(self, model):
        p=self._get('/api/tags').payload
        requested=model.split(':',1)[0]
        for item in p.get('models') or []:
            name=str(item.get('name') or '')
            if name==model or name.split(':',1)[0]==requested: return True
        return False
    def check_ready(self): self._get('/api/tags')
    def _get(self,path):
        return self._request(Request(self.base_url+path,method='GET',headers={'Accept':'application/json'}))
    def _post(self,path,payload):
        return self._request(Request(self.base_url+path,method='POST',data=json.dumps(payload).encode(),headers={'Accept':'application/json','Content-Type':'application/json'}))
    def _request(self,request):
        try:
            with self._opener(request,timeout=self.timeout) as response: raw=response.read().decode('utf-8')
        except (HTTPError,URLError,OSError) as exc:
            raise OllamaConnectionError('Ollama service is unavailable') from exc
        try: payload=json.loads(raw)
        except json.JSONDecodeError as exc: raise OllamaConnectionError('Ollama returned invalid JSON') from exc
        if not isinstance(payload,dict): raise OllamaConnectionError('Ollama returned an invalid response object')
        return OllamaResponse(payload)
