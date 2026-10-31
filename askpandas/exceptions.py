"""Exception hierarchy for AskPandas.

Every exception derives from :class:`AskPandasError`, so callers can catch all library
errors in one place. Each class also subclasses the built-in exception that earlier
releases raised (``ValueError`` or ``RuntimeError``), so existing ``except`` clauses keep
working.
"""

from __future__ import annotations


class AskPandasError(Exception):
    """Base class for all AskPandas errors."""


class DataLoadError(AskPandasError, ValueError):
    """Input could not be turned into a pandas DataFrame (bad path, format or data)."""


class LLMNotConfiguredError(AskPandasError, ValueError):
    """A natural-language query was made before an LLM was set with ``set_llm``."""


class LLMError(AskPandasError, RuntimeError):
    """The LLM backend failed (HTTP error, timeout, malformed response)."""


class CodeGenerationError(AskPandasError, RuntimeError):
    """The LLM kept failing to return code after all retries."""


class QueryProcessingError(AskPandasError, RuntimeError):
    """A query failed somewhere between prompt building and code execution."""


__all__ = [
    "AskPandasError",
    "CodeGenerationError",
    "DataLoadError",
    "LLMError",
    "LLMNotConfiguredError",
    "QueryProcessingError",
]
