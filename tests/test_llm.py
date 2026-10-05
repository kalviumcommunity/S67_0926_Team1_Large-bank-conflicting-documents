import pytest
from app.generation.llm import LLMError,OllamaLLMProvider
class Fake:
    def __init__(self,answer='Grounded [E1].'): self.answer=answer
    def generate(self,**kwargs): return self.answer
    def check_ready(self): pass
    def model_available(self,model): return True
def test_generate(): assert OllamaLLMProvider(client=Fake()).generate('s','p')=='Grounded [E1].'
def test_failure_wrapped():
    class Broken(Fake):
        def generate(self,**kwargs): raise RuntimeError('offline')
    with pytest.raises(LLMError): OllamaLLMProvider(client=Broken()).generate('s','p')
