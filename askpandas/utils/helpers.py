import os
import warnings
from typing import Any

import pandas as pd

from ..exceptions import DataLoadError


def is_text_column(series: pd.Series) -> bool:
    """True for text columns: ``object`` dtype (pandas < 3) or ``str``/``string`` dtype (pandas 3)."""
    return pd.api.types.is_object_dtype(series) or isinstance(series.dtype, pd.StringDtype)


def is_numeric_column(series: pd.Series) -> bool:
    """True for integer/float columns (booleans excluded)."""
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)


def validate_dataframe(df: Any) -> pd.DataFrame:
    """Convert ``df`` to a pandas DataFrame.

    Accepts a DataFrame (returned as-is), a dict or list of records, or a path
    (``str`` or :class:`os.PathLike`) to a ``.csv`` or ``.json`` file.

    Raises:
        DataLoadError: If the input cannot be converted or the file cannot be read.
    """
    if isinstance(df, pd.DataFrame):
        return df
    if isinstance(df, (dict, list)):
        return pd.DataFrame(df)
    if isinstance(df, (str, os.PathLike)):
        path = os.fspath(df)
        lowered = str(path).lower()
        try:
            if lowered.endswith(".csv"):
                return pd.read_csv(path, encoding="utf-8", low_memory=False)
            if lowered.endswith(".json"):
                return pd.read_json(path, encoding="utf-8")
        except (OSError, ValueError) as e:
            raise DataLoadError(f"Could not read {path!r}: {e}") from e
        raise DataLoadError(f"Unsupported file format for {path!r}. Use a .csv or .json path.")
    try:
        return pd.DataFrame(df)
    except Exception as e:
        raise DataLoadError(f"Failed to create DataFrame: {e}") from e


def get_dataframe_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Get comprehensive summary of a DataFrame."""
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": dict(df.dtypes),
        "memory_usage": df.memory_usage(deep=True).sum(),
        "null_counts": df.isnull().sum().to_dict(),
        "unique_counts": {col: df[col].nunique() for col in df.columns},
        "sample_data": df.head(3).to_dict("records"),
    }


def format_number(value: int | float) -> str:
    """Format numbers for better readability."""
    if isinstance(value, (int, float)):
        if abs(value) >= 1e6:
            return f"{value / 1e6:.2f}M"
        if abs(value) >= 1e3:
            return f"{value / 1e3:.2f}K"
        return f"{value:.2f}"
    return str(value)


def detect_data_types(df: pd.DataFrame) -> dict[str, str]:
    """Detect and suggest optimal data types for DataFrame columns."""
    suggestions = {}

    for col in df.columns:
        if is_text_column(df[col]):
            # Check if it's actually numeric
            try:
                pd.to_numeric(df[col], errors="raise")
                suggestions[col] = "numeric"
            except (ValueError, TypeError):
                # Check if it's datetime
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        pd.to_datetime(df[col], errors="raise")
                    suggestions[col] = "datetime"
                except (ValueError, TypeError):
                    suggestions[col] = "categorical"
        elif pd.api.types.is_integer_dtype(df[col]):
            suggestions[col] = "int"
        elif pd.api.types.is_float_dtype(df[col]):
            suggestions[col] = "float"
        else:
            suggestions[col] = str(df[col].dtype)

    return suggestions


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names by removing special characters and standardizing format."""
    df_clean = df.copy()
    df_clean.columns = (
        df_clean.columns.str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
        .str.strip("_")
    )
    return df_clean


def get_memory_usage_mb(df: pd.DataFrame) -> float:
    """Get memory usage of DataFrame in MB."""
    return df.memory_usage(deep=True).sum() / 1024 / 1024
