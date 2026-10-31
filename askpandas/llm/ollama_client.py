"""Client for a local Ollama server (https://ollama.com)."""

from __future__ import annotations

import requests

from .base import BaseLLM


class OllamaLLM(BaseLLM):
    """LLM client for a locally running Ollama server.

    Args:
        model_name: Ollama model tag, e.g. ``"mistral"`` or ``"llama3.1"``.
        host: Ollama server URL.
        temperature: Sampling temperature.
        timeout: HTTP timeout in seconds (local models can be slow on first load).
    """

    def __init__(
        self,
        model_name: str = "mistral",
        host: str = "http://localhost:11434",
        temperature: float = 0.1,
        timeout: float = 120,
    ) -> None:
        self.model_name = model_name
        self.host = host.rstrip("/")
        self.endpoint = f"{self.host}/api/generate"
        self.temperature = temperature
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        """Generate response using Ollama."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature, "top_p": 0.9},
        }
        try:
            response = requests.post(self.endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            raise RuntimeError(f"Ollama failed to generate response: {e}") from e

    def is_available(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def __repr__(self) -> str:
        return f"OllamaLLM(model_name={self.model_name!r}, host={self.host!r})"
