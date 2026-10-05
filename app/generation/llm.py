from typing import Protocol
from app.ollama.client import OllamaClient, OllamaConnectionError

class LLMError(RuntimeError): pass
class LLMProvider(Protocol):
    def generate(self,instructions:str,user_input:str)->str: ...

class OllamaLLMProvider:
    def __init__(self,model='gemma3:4b',*,base_url='http://localhost:11434',timeout=120.0,temperature=0.0,client=None):
        if not model.strip(): raise ValueError('model is required')
        if timeout<=0: raise ValueError('timeout must be positive')
        if temperature<0: raise ValueError('temperature cannot be negative')
        self.model=model; self.temperature=temperature; self.client=client or OllamaClient(base_url=base_url,timeout=timeout)
    def generate(self,instructions,user_input):
        try: return self.client.generate(model=self.model,system=instructions,prompt=user_input,temperature=self.temperature).strip()
        except Exception as exc:
            if isinstance(exc,LLMError): raise
            raise LLMError('local LLM generation failed') from exc
    def check_ready(self):
        try:
            self.client.check_ready()
            if not self.client.model_available(self.model): raise LLMError(f'chat model is not installed: {self.model}')
        except LLMError: raise
        except Exception as exc: raise LLMError('local LLM service is not ready') from exc
