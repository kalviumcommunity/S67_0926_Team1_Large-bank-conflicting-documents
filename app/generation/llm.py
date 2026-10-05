from typing import Protocol

from openai import OpenAI


class LLMError(RuntimeError):
    """Raised when grounded answer generation fails."""


class LLMProvider(Protocol):
    def generate(self, instructions: str, user_input: str) -> str:
        ...


class OpenAIResponsesProvider:
    """OpenAI Responses API adapter for grounded answer generation."""

    def __init__(self, api_key: str, model: str = "gpt-6-luna", *, timeout: float = 60.0, max_retries: int = 2, client: OpenAI | None = None):
        if not api_key:
            raise ValueError("api_key is required")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        self.client = client or OpenAI(api_key=api_key, timeout=timeout, max_retries=max_retries)
        self.model = model

    def generate(self, instructions: str, user_input: str) -> str:
        try:
            response = self.client.responses.create(model=self.model, instructions=instructions, input=user_input)
            answer = (response.output_text or "").strip()
            if not answer:
                raise LLMError("LLM returned an empty answer")
            return answer
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError("LLM generation failed") from exc
