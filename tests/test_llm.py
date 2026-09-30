from types import SimpleNamespace

import pytest

from app.generation.llm import LLMError, OpenAIResponsesProvider


class FakeResponses:
    def __init__(self, text="Grounded answer [E1]."):
        self.text = text
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.text)


class FakeClient:
    def __init__(self, text="Grounded answer [E1]."):
        self.responses = FakeResponses(text)


def test_openai_provider_uses_responses_api():
    client = FakeClient()
    provider = OpenAIResponsesProvider(
        api_key="test",
        model="gpt-5.6-luna",
        client=client,
    )

    answer = provider.generate("system", "evidence")

    assert answer == "Grounded answer [E1]."
    assert client.responses.calls[0]["model"] == "gpt-5.6-luna"
    assert client.responses.calls[0]["instructions"] == "system"


def test_openai_provider_rejects_empty_output():
    provider = OpenAIResponsesProvider(
        api_key="test",
        client=FakeClient(""),
    )

    with pytest.raises(LLMError):
        provider.generate("system", "evidence")


def test_openai_provider_wraps_api_failure():
    class BrokenResponses:
        def create(self, **kwargs):
            raise RuntimeError("network failure")

    client = SimpleNamespace(responses=BrokenResponses())

    provider = OpenAIResponsesProvider(
        api_key="test",
        client=client,
    )

    with pytest.raises(LLMError):
        provider.generate("system", "evidence")
