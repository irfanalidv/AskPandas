"""Plug in your own model by implementing two methods, and inspect what AskPandas does.

Use case: you serve a model behind an internal API (or want to log every prompt). Any
object with ``generate(prompt) -> str`` and ``is_available() -> bool`` works; subclassing
``askpandas.BaseLLM`` is optional. The example also shows the sandbox rejecting unsafe
code and the execution history.

Needs: nothing for the default offline run. Pass ``--openai`` to use OpenAI instead
(requires network and ``OPENAI_API_KEY``; makes two short API calls with gpt-4o-mini).

Run: python examples/custom_llm_backend.py [--openai]
"""

from __future__ import annotations

import sys

import askpandas as ap


class LoggingLLM(ap.BaseLLM):
    """Wraps another backend (or a fixed reply) and records every prompt."""

    def __init__(self, inner: ap.BaseLLM | None = None) -> None:
        self.inner = inner
        self.prompts: list[str] = []
        self.model_name = getattr(inner, "model_name", "logging-offline")

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if self.inner is not None:
            return self.inner.generate(prompt)
        if "internals" in prompt.rsplit("USER QUERY:", 1)[-1].lower():
            # A misbehaving model trying a classic sandbox escape via dunder attributes
            return "```python\nprint(().__class__.__base__.__subclasses__())\n```"
        return "```python\nprint(df0.groupby('team')['tickets'].sum().idxmax())\n```"

    def is_available(self) -> bool:
        return True if self.inner is None else self.inner.is_available()


inner = ap.OpenAICompatibleLLM.openai("gpt-4o-mini") if "--openai" in sys.argv else None
llm = LoggingLLM(inner)
ap.set_llm(llm)

tickets = ap.DataFrame(
    {
        "team": ["billing", "billing", "shipping", "returns", "shipping", "shipping"],
        "tickets": [12, 7, 30, 4, 11, 9],
    }
)

print("Q: Which team handled the most tickets?")
print(tickets.chat("Which team handled the most tickets?"))

if inner is None:
    print("Q: Show me the Python internals")
    print(tickets.chat("Show me the Python internals"))

print(f"\nPrompt sent to the model starts with:\n{llm.prompts[0][:200]}...")
for entry in tickets._engine.get_execution_history() if tickets._engine else []:
    status = "ok" if entry["success"] else f"failed ({entry['error']})"
    print(f"- {entry['query']!r}: {status}")
