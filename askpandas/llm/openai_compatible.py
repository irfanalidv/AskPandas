"""Client for any OpenAI-compatible Chat Completions API.

Works with OpenAI, Mistral, the Hugging Face Inference Providers router, Groq,
Together, vLLM, LM Studio, Ollama's ``/v1`` endpoint and other servers that
implement ``POST {base_url}/chat/completions``. Only ``requests`` is required.
"""

from __future__ import annotations

import os
from typing import Any

import requests

from ..exceptions import LLMError
from .base import BaseLLM

DEFAULT_SYSTEM_PROMPT = (
    "You are an expert Python data analyst. Reply with Python code only, "
    "inside a single ```python code block."
)


class OpenAICompatibleLLM(BaseLLM):
    """LLM client for OpenAI-compatible ``/chat/completions`` endpoints.

    Args:
        model_name: Model identifier understood by the server.
        base_url: API root, e.g. ``https://api.openai.com/v1``.
        api_key: API key. If omitted, read from ``api_key_env``.
        api_key_env: Environment variable(s) to read the key from (first match wins).
        temperature: Sampling temperature.
        max_tokens: Maximum tokens in the reply.
        timeout: HTTP timeout in seconds.
        system_prompt: System message sent before the prompt (``None`` to omit).
    """

    def __init__(
        self,
        model_name: str,
        base_url: str = "https://api.openai.com/v1",
        api_key: str | None = None,
        api_key_env: str | tuple[str, ...] | None = "OPENAI_API_KEY",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        timeout: float = 60,
        system_prompt: str | None = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.system_prompt = system_prompt
        env_names = (api_key_env,) if isinstance(api_key_env, str) else (api_key_env or ())
        self.api_key = api_key or next(
            (os.environ[name] for name in env_names if os.environ.get(name)), None
        )

    # ------------------------------------------------------------------ presets
    @classmethod
    def openai(cls, model_name: str = "gpt-4o-mini", **kwargs: Any) -> OpenAICompatibleLLM:
        """OpenAI (reads ``OPENAI_API_KEY``)."""
        return cls(model_name, base_url="https://api.openai.com/v1", **kwargs)

    @classmethod
    def mistral(
        cls, model_name: str = "mistral-small-latest", **kwargs: Any
    ) -> OpenAICompatibleLLM:
        """Mistral AI (reads ``MISTRAL_API_KEY``)."""
        kwargs.setdefault("api_key_env", "MISTRAL_API_KEY")
        return cls(model_name, base_url="https://api.mistral.ai/v1", **kwargs)

    # --------------------------------------------------------------------- API
    @property
    def headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _messages(self, prompt: str) -> list[dict[str, str]]:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(self, prompt: str) -> str:
        """Send ``prompt`` as a chat message and return the reply text."""
        payload = {
            "model": self.model_name,
            "messages": self._messages(prompt),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"] or ""
        except requests.HTTPError as e:
            body = e.response.text[:500] if e.response is not None else ""
            raise LLMError(f"{type(self).__name__} request failed ({e}). Response: {body}") from e
        except Exception as e:
            raise LLMError(f"{type(self).__name__} failed to generate a response: {e}") from e

    def is_available(self) -> bool:
        """Return True if ``GET {base_url}/models`` succeeds with the configured key."""
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def __repr__(self) -> str:
        return f"{type(self).__name__}(model_name={self.model_name!r}, base_url={self.base_url!r})"
