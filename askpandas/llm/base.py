"""Abstract interface every AskPandas LLM client implements."""

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Minimal LLM interface used by :class:`~askpandas.core.engine.AskPandasEngine`.

    Subclass it (or duck-type the two methods) to plug in any model or provider.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Return the model's reply to ``prompt`` (ideally a fenced Python code block)."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the backend can be reached."""
