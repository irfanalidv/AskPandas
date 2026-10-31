"""A tiny scripted LLM so the examples run offline, without an API key or Ollama.

``ScriptedLLM`` implements the same two-method interface as the real clients
(``generate`` and ``is_available``). It reads the user question out of the prompt that
AskPandas builds and replies with the pandas code a real model would be expected to write.
Everything after that (code extraction, validation, sandboxed execution, history) is the
real AskPandas pipeline.

To use a real model instead, replace ``ScriptedLLM(...)`` with for example
``askpandas.OllamaLLM("llama3.1")`` or ``askpandas.OpenAICompatibleLLM.openai("gpt-4o-mini")``.
"""

from __future__ import annotations

import askpandas as ap


class ScriptedLLM(ap.BaseLLM):
    """Answers each question with canned code, chosen by a keyword in the question."""

    def __init__(self, answers: dict[str, str]) -> None:
        self.answers = answers
        self.model_name = "scripted-offline"

    def generate(self, prompt: str) -> str:
        question = prompt.rsplit("USER QUERY:", 1)[-1].lower()
        for keyword, code in self.answers.items():
            if keyword in question:
                return f"```python\n{code.strip()}\n```"
        return "```python\nprint('No scripted answer for this question.')\n```"

    def is_available(self) -> bool:
        return True
