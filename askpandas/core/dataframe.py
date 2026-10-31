"""The ``AskDataFrame`` wrapper returned by :func:`askpandas.DataFrame`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from ..exceptions import DataLoadError, LLMNotConfiguredError
from ..utils.helpers import (
    clean_column_names,
    get_dataframe_summary,
    is_numeric_column,
    is_text_column,
    validate_dataframe,
)

if TYPE_CHECKING:
    from .engine import AskPandasEngine


class AskDataFrame:
    """Enhanced DataFrame with AI-powered capabilities."""

    def __init__(self, data: Any) -> None:
        """Wrap ``data``: a DataFrame, dict, list of records, or a ``.csv``/``.json`` path.

        Raises:
            DataLoadError: If ``data`` cannot be converted to a DataFrame.
        """
        try:
            self.df = validate_dataframe(data)
        except DataLoadError:
            raise
        except Exception as e:
            raise DataLoadError(f"Failed to create DataFrame: {e}") from e

        # Store original data source for reference
        self._source = data if isinstance(data, str) else "data"

        # Initialize engine (will be set later)
        self._engine: AskPandasEngine | None = None

    def _get_engine(self) -> AskPandasEngine | None:
        """Get or create the engine, following the LLM currently set with ``set_llm``."""
        # Import here to avoid circular imports
        from .. import get_llm
        from ..core.engine import AskPandasEngine

        llm = get_llm()
        if not llm:
            return None
        if self._engine is None:
            self._engine = AskPandasEngine(llm)
        elif self._engine.llm is not llm:
            # set_llm() was called again: keep the history, switch the model
            self._engine.llm = llm
        return self._engine

    def chat(self, query: str) -> Any:
        """Query the dataframe using natural language."""
        engine = self._get_engine()
        if engine is None:
            raise LLMNotConfiguredError("No LLM configured. Use askpandas.set_llm() to set one.")

        return engine.process_query(query, [self])

    def info(self) -> str:
        """Return a string with dataframe metadata and sample data."""
        summary = get_dataframe_summary(self.df)

        return f"""
DataFrame Info:
- Shape: {summary["shape"]}
- Columns: {summary["columns"]}
- Data types: {summary["dtypes"]}
- Memory usage: {summary["memory_usage"] / 1024 / 1024:.2f} MB
- Null counts: {summary["null_counts"]}
- Unique counts: {summary["unique_counts"]}
- Sample data (first 3 rows):
{self.df.head(3).to_string()}
"""

    def describe(self) -> pd.DataFrame:
        """Get statistical description of the DataFrame."""
        return self.df.describe(include="all")

    def head(self, n: int = 5) -> pd.DataFrame:
        """Get first n rows of the DataFrame."""
        return self.df.head(n)

    def tail(self, n: int = 5) -> pd.DataFrame:
        """Get last n rows of the DataFrame."""
        return self.df.tail(n)

    def shape(self) -> tuple[int, int]:
        """Get the shape of the DataFrame."""
        return self.df.shape

    def columns(self) -> list[str]:
        """Get the column names."""
        return list(self.df.columns)

    def dtypes(self) -> dict[str, Any]:
        """Get the data types of columns."""
        return dict(self.df.dtypes)

    def isnull(self) -> pd.DataFrame:
        """Get boolean mask of null values."""
        return self.df.isnull()

    def notnull(self) -> pd.DataFrame:
        """Get boolean mask of non-null values."""
        return self.df.notnull()

    def dropna(self, **kwargs: Any) -> AskDataFrame:
        """Drop rows with null values."""
        return AskDataFrame(self.df.dropna(**kwargs))

    def fillna(self, value: Any, **kwargs: Any) -> AskDataFrame:
        """Fill null values."""
        return AskDataFrame(self.df.fillna(value, **kwargs))

    def sort_values(self, by: str | list[str], **kwargs: Any) -> AskDataFrame:
        """Sort DataFrame by values."""
        return AskDataFrame(self.df.sort_values(by, **kwargs))

    def groupby(self, by: str | list[str], **kwargs: Any) -> pd.core.groupby.DataFrameGroupBy:
        """Group DataFrame by columns."""
        return self.df.groupby(by, **kwargs)

    def query(self, expr: str) -> AskDataFrame:
        """Query DataFrame using string expression."""
        return AskDataFrame(self.df.query(expr))

    def select_dtypes(self, include: Any = None, exclude: Any = None) -> AskDataFrame:
        """Select columns based on data types."""
        return AskDataFrame(self.df.select_dtypes(include=include, exclude=exclude))

    def clean_columns(self) -> AskDataFrame:
        """Clean column names by removing special characters and standardizing format."""
        return AskDataFrame(clean_column_names(self.df))

    def to_csv(self, path: str, **kwargs: Any) -> str:
        """Save DataFrame to CSV file."""
        try:
            self.df.to_csv(path, **kwargs)
            return f"DataFrame saved to {path}"
        except Exception as e:
            return f"Failed to save DataFrame: {e}"

    def to_json(self, path: str, **kwargs: Any) -> str:
        """Save DataFrame to JSON file."""
        try:
            self.df.to_json(path, **kwargs)
            return f"DataFrame saved to {path}"
        except Exception as e:
            return f"Failed to save DataFrame: {e}"

    def get_summary_stats(self) -> dict[str, Any]:
        """Get comprehensive summary statistics."""
        summary = get_dataframe_summary(self.df)

        # Add additional statistics
        summary.update(
            {
                "numeric_columns": list(self.df.select_dtypes(include=[np.number]).columns),
                "categorical_columns": list(
                    self.df.select_dtypes(include=["object", "string"]).columns
                ),
                "datetime_columns": list(self.df.select_dtypes(include=["datetime"]).columns),
                "total_memory_mb": summary["memory_usage"] / 1024 / 1024,
                "duplicate_rows": self.df.duplicated().sum(),
                "unique_rows": self.df.drop_duplicates().shape[0],
            }
        )

        return summary

    def get_column_info(self, column: str) -> dict[str, Any]:
        """Get detailed information about a specific column."""
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")

        col_data = self.df[column]
        col_type = str(col_data.dtype)

        info = {
            "name": column,
            "dtype": col_type,
            "count": col_data.count(),
            "null_count": col_data.isnull().sum(),
            "unique_count": col_data.nunique(),
            "memory_usage": col_data.memory_usage(deep=True),
        }

        if is_numeric_column(col_data):
            info.update(
                {
                    "min": col_data.min(),
                    "max": col_data.max(),
                    "mean": col_data.mean(),
                    "median": col_data.median(),
                    "std": col_data.std(),
                }
            )
        elif is_text_column(col_data):
            info.update(
                {
                    "top_values": col_data.value_counts().head(5).to_dict(),
                    "most_common": (col_data.mode().iloc[0] if not col_data.mode().empty else None),
                }
            )

        return info

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to the underlying pandas DataFrame."""
        # Guard against infinite recursion when ``df`` is not set yet (copy, pickle)
        if name == "df" or name.startswith("__"):
            raise AttributeError(name)
        return getattr(self.df, name)

    def __getitem__(self, key: Any) -> Any:
        """Allow indexing operations."""
        result = self.df[key]
        if isinstance(result, pd.DataFrame):
            return AskDataFrame(result)
        return result

    def __len__(self) -> int:
        """Return the length of the DataFrame."""
        return len(self.df)

    def __repr__(self) -> str:
        """String representation of the DataFrame."""
        return f"AskDataFrame(shape={self.df.shape}, columns={list(self.df.columns)})"

    def __str__(self) -> str:
        """String representation of the DataFrame."""
        return self.__repr__()
