"""AskPandas: query pandas DataFrames and CSV files in natural language with an LLM."""

from __future__ import annotations

import logging
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Any

from .core.dataframe import AskDataFrame
from .core.engine import AskPandasEngine
from .core.query_processor import QueryProcessor
from .exceptions import (
    AskPandasError,
    CodeGenerationError,
    DataLoadError,
    LLMError,
    LLMNotConfiguredError,
    QueryProcessingError,
)
from .llm.base import BaseLLM
from .llm.huggingface_client import HuggingFaceLLM
from .llm.ollama_client import OllamaLLM
from .llm.openai_compatible import OpenAICompatibleLLM
from .utils.helpers import (
    clean_column_names,
    detect_data_types,
    format_number,
    get_dataframe_summary,
    get_memory_usage_mb,
    validate_dataframe,
)
from .visualization.charts import (
    create_bar_chart,
    create_box_plot,
    create_correlation_heatmap,
    create_histogram,
    create_line_chart,
    create_scatter_plot,
    get_plot_colors,
    save_plot,
    set_plot_style,
)

try:
    __version__ = _pkg_version("askpandas")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0.0.0+unknown"
__author__ = "Md Irfan Ali"
__email__ = "irfanali29@hotmail.com"

__all__ = [
    "AskDataFrame",
    "AskPandasEngine",
    "AskPandasError",
    "BaseLLM",
    "CodeGenerationError",
    "DataFrame",
    "DataLoadError",
    "HuggingFaceLLM",
    "LLMError",
    "LLMNotConfiguredError",
    "OllamaLLM",
    "OpenAICompatibleLLM",
    "QueryProcessingError",
    "QueryProcessor",
    "__version__",
    "analyze_query",
    "chat",
    "clean_column_names",
    "create_bar_chart",
    "create_box_plot",
    "create_correlation_heatmap",
    "create_histogram",
    "create_line_chart",
    "create_scatter_plot",
    "detect_data_types",
    "format_number",
    "get_available_models",
    "get_config",
    "get_dataframe_summary",
    "get_llm",
    "get_memory_usage_mb",
    "get_plot_colors",
    "get_query_examples",
    "save_plot",
    "set_config",
    "set_llm",
    "set_plot_style",
    "validate_dataframe",
    "validate_query",
]


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Config:
    """Global settings, read and changed with :func:`get_config` / :func:`set_config`.

    Settings that take effect: ``output_dir`` (where :func:`save_plot` writes),
    ``plot_style`` (applied when changed via :func:`set_config`) and ``verbose``
    (logs configuration changes at INFO level). The remaining keys are stored for
    forward compatibility and are not enforced yet.
    """

    def __init__(self) -> None:
        self.llm: Any = None
        self.model_name = "mistral"
        self.temperature = 0.1
        self.max_tokens = 1000
        self.enable_plotting = True
        self.safe_mode = True
        self.output_dir = "askpandas_plots"
        self.plot_style = "seaborn"
        self.max_execution_time = 30  # seconds
        self.enable_history = True
        self.verbose = False

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enable_plotting": self.enable_plotting,
            "safe_mode": self.safe_mode,
            "output_dir": self.output_dir,
            "plot_style": self.plot_style,
            "max_execution_time": self.max_execution_time,
            "enable_history": self.enable_history,
            "verbose": self.verbose,
        }

    def update(self, **kwargs: Any) -> None:
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(
                    f"Unknown configuration key: {key!r}. Valid keys: {sorted(self.to_dict())}"
                )


# Global configuration instance
config = Config()


def set_llm(llm: Any) -> None:
    """Set the LLM used by :meth:`AskDataFrame.chat` and :func:`chat`.

    Any object with ``generate(prompt) -> str`` and ``is_available() -> bool`` works;
    subclassing :class:`BaseLLM` is optional.
    """
    if not hasattr(llm, "generate") or not hasattr(llm, "is_available"):
        raise ValueError("LLM must implement 'generate' and 'is_available' methods")

    config.llm = llm
    if config.verbose:
        logger.info("LLM set to: %s", type(llm).__name__)


def get_llm() -> Any:
    """Get the currently configured LLM."""
    return config.llm


def get_config() -> dict[str, Any]:
    """Get current configuration."""
    return config.to_dict()


def set_config(**kwargs: Any) -> None:
    """Update configuration."""
    config.update(**kwargs)
    if "plot_style" in kwargs:
        set_plot_style(config.plot_style)
    if config.verbose:
        logger.info("Configuration updated: %s", kwargs)


def chat(query: str, *dataframes: Any) -> Any:
    """Ask ``query`` across one or more DataFrames (exposed as ``df0``, ``df1``, ...).

    Each argument may be an :class:`AskDataFrame` or anything :func:`DataFrame` accepts.

    Raises:
        LLMNotConfiguredError: If :func:`set_llm` has not been called.
        ValueError: If no DataFrame is given.
        QueryProcessingError: If the query fails.
    """
    if not config.llm:
        raise LLMNotConfiguredError("No LLM configured. Use askpandas.set_llm() to set one.")

    if not dataframes:
        raise ValueError("At least one dataframe must be provided.")

    # Validate dataframes
    validated_dfs = []
    for df in dataframes:
        if isinstance(df, AskDataFrame):
            validated_dfs.append(df)
        else:
            validated_dfs.append(AskDataFrame(df))

    engine = AskPandasEngine(config.llm)
    return engine.process_query(query, validated_dfs)


def DataFrame(data: Any) -> AskDataFrame:
    """Create an AskPandas DataFrame."""
    return AskDataFrame(data)


def get_available_models() -> dict[str, list[str]]:
    """Get list of available models for different LLM providers."""
    return {
        "ollama": [
            "mistral",
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "codellama",
            "gemma",
            "neural-chat",
            "vicuna",
        ],
        "huggingface": [
            "Qwen/Qwen2.5-Coder-7B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "meta-llama/Llama-3.1-8B-Instruct",
        ],
        "openai": ["gpt-4o-mini", "gpt-4o"],
        "mistral": ["mistral-small-latest", "codestral-latest", "mistral-large-latest"],
    }


def get_query_examples(category: str | None = None) -> list[str]:
    """Get example queries for different categories."""
    processor = QueryProcessor()
    return processor.get_query_examples(category)


def analyze_query(query: str) -> dict[str, Any]:
    """Analyze a query and provide insights."""
    processor = QueryProcessor()
    return processor.categorize_query(query)


def validate_query(query: str, columns: list[str]) -> dict[str, Any]:
    """Validate if a query can be executed with given columns."""
    processor = QueryProcessor()
    return processor.validate_query(query, columns)
