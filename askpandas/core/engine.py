import json
import logging
import re
import textwrap
import time
import warnings
from collections import Counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ..exceptions import CodeGenerationError, QueryProcessingError
from ..security.sandbox import SafeExecutor
from ..utils.helpers import get_dataframe_summary, is_text_column
from ..visualization.charts import save_plot

logger = logging.getLogger(__name__)

# Appended to every prompt template so that all query types follow the sandbox rules.
SANDBOX_RULES = """SANDBOX RULES (always apply):
- The dataframes are already loaded as df0, df1, df2, ... Do not read files.
- pd, np, plt and sns are already available. Do not write import statements.
- Do not define functions or classes, and do not use open(), eval() or exec().
- Print every result you want the user to see with print().
- To keep a chart, call save_plot(fig, "name.png"). Helpers available: create_bar_chart,
  create_line_chart, create_scatter_plot, create_histogram, create_correlation_heatmap,
  create_box_plot (each takes a DataFrame and returns a matplotlib Figure)."""


class AskPandasEngine:
    """Advanced query processing engine with intelligent code generation."""

    def __init__(self, llm: Any, config: dict[str, Any] | None = None) -> None:
        """Initialize the query processing engine with an LLM.

        Args:
            llm: Any object with ``generate(prompt) -> str`` and ``is_available() -> bool``.
            config: Optional engine settings. Supported key: ``retry_backoff`` (seconds,
                default 1.0) - base delay between retries after an LLM error.
        """
        self.llm = llm
        self.safe_executor = SafeExecutor()
        self.execution_history: list[dict[str, Any]] = []
        self.config = config or {}
        self._last_execution_time: float | None = None
        # Base delay in seconds between retries after an LLM error (doubles each retry)
        self.retry_backoff = float(self.config.get("retry_backoff", 1.0))

        # Enhanced prompt templates
        self.prompt_templates = {
            "analysis": self._get_analysis_prompt(),
            "visualization": self._get_visualization_prompt(),
            "data_quality": self._get_data_quality_prompt(),
            "statistical": self._get_statistical_prompt(),
            "multi_dataframe": self._get_multi_dataframe_prompt(),
        }

    def process_query(self, query: str, dataframes: list[Any]) -> Any:
        """Answer ``query`` by generating pandas code with the LLM and running it.

        Args:
            query: The question in plain English.
            dataframes: :class:`~askpandas.core.dataframe.AskDataFrame` objects, exposed to
                the generated code as ``df0``, ``df1``, ...

        Returns:
            The text printed by the generated code (or an explanatory message if the code
            failed inside the sandbox).

        Raises:
            ValueError: If ``dataframes`` is empty.
            QueryProcessingError: If prompting the LLM or running the code fails.
        """
        if not dataframes:
            raise ValueError("At least one dataframe must be provided.")

        try:
            # Enhanced context generation
            context = self._generate_enhanced_context(dataframes)

            # Intelligent prompt selection
            prompt_type = self._classify_query(query)
            prompt = self._generate_enhanced_prompt(query, context, prompt_type)

            # Generate code with retry mechanism
            code = self._generate_code_with_retry(prompt, query)

            # Execute code safely with enhanced monitoring
            started = time.perf_counter()
            result = self._execute_code_enhanced(code, dataframes)
            self._last_execution_time = time.perf_counter() - started

            # Store execution history with metadata
            self._store_execution_history(
                query, code, result, prompt_type, error=self.safe_executor.last_error
            )

            return result

        except Exception as e:
            error_msg = f"Query processing failed: {e!s}"
            self._store_execution_history(query, None, error_msg, "error", error=str(e))
            raise QueryProcessingError(error_msg) from e

    def _classify_query(self, query: str) -> str:
        """Intelligently classify the query type for better prompt selection."""
        query_lower = query.lower()

        # Define classification patterns
        patterns = {
            "visualization": [
                r"\b(plot|chart|graph|visualize|show|display|create)\b",
                r"\b(bar|line|scatter|histogram|box|heatmap|pie)\s+(chart|plot|graph)\b",
                r"\b(visualization|chart|plot)\b",
            ],
            "data_quality": [
                r"\b(null|missing|duplicate|unique|clean|validate|outlier)\b",
                r"\b(data\s+quality|integrity|consistency)\b",
                r"\b(check|find|identify)\s+(missing|duplicate|outlier)\b",
            ],
            "statistical": [
                r"\b(correlation|variance|standard\s+deviation|distribution|anova|t-test)\b",
                r"\b(statistical|analysis|insights|patterns|trends)\b",
                r"\b(mean|median|mode|percentile|quartile)\b",
            ],
            "multi_dataframe": [
                r"\b(join|merge|combine|compare|across|between)\b",
                r"\b(multiple|both|all|together)\b",
                r"\b(relationship|connection|link)\b",
            ],
        }

        for query_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return query_type

        return "analysis"  # Default to general analysis

    def _generate_enhanced_context(self, dataframes: list) -> str:
        """Generate comprehensive context with advanced data insights."""
        context_parts = []

        for i, ask_df in enumerate(dataframes):
            summary = get_dataframe_summary(ask_df.df)

            # Enhanced data insights
            df_info = f"""
DataFrame {i} (df{i}):
- Shape: {summary["shape"]}
- Columns: {summary["columns"]}
- Data types: {summary["dtypes"]}
- Memory usage: {summary["memory_usage"] / 1024 / 1024:.2f} MB
- Null counts: {summary["null_counts"]}
- Unique counts: {summary["unique_counts"]}
- Duplicate rows: {summary.get("duplicate_rows", 0)}
- Numeric columns: {summary.get("numeric_columns", [])}
- Categorical columns: {summary.get("categorical_columns", [])}
- Date columns: {summary.get("datetime_columns", [])}

Sample data (first 3 rows):
{dataframes[i].df.head(3).to_string()}

Data quality insights:
- Missing data percentage: {self._calculate_missing_percentage(dataframes[i].df):.1f}%
- Data type suggestions: {self._suggest_data_types(dataframes[i].df)}
- Potential outliers: {self._detect_potential_outliers(dataframes[i].df)}
"""
            context_parts.append(df_info)

        return "\n".join(context_parts)

    def _calculate_missing_percentage(self, df: pd.DataFrame) -> float:
        """Calculate percentage of missing data."""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        return (missing_cells / total_cells) * 100 if total_cells > 0 else 0

    def _suggest_data_types(self, df: pd.DataFrame) -> dict[str, str]:
        """Suggest optimal data types for columns."""
        suggestions = {}
        for col in df.columns:
            if is_text_column(df[col]):
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        pd.to_datetime(df[col], errors="raise")
                    suggestions[col] = "datetime"
                except (ValueError, TypeError):
                    try:
                        pd.to_numeric(df[col], errors="raise")
                        suggestions[col] = "numeric"
                    except (ValueError, TypeError):
                        suggestions[col] = "categorical"
            elif pd.api.types.is_integer_dtype(df[col]):
                suggestions[col] = "int"
            elif pd.api.types.is_float_dtype(df[col]):
                suggestions[col] = "float"
        return suggestions

    def _detect_potential_outliers(self, df: pd.DataFrame) -> list[str]:
        """Detect potential outliers in numeric columns."""
        outliers = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outlier_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if outlier_count > 0:
                outliers.append(f"{col}: {outlier_count} potential outliers")

        return outliers

    def _generate_enhanced_prompt(self, query: str, context: str, prompt_type: str) -> str:
        """Generate enhanced prompts based on query type."""
        base_prompt = self.prompt_templates.get(prompt_type, self.prompt_templates["analysis"])
        base_prompt = f"{base_prompt}\n\n{SANDBOX_RULES}"

        # Add query-specific enhancements
        enhancements = self._get_query_enhancements(query)

        return f"{base_prompt}\n\n{enhancements}\n\nDATAFRAMES AVAILABLE:\n{context}\n\nUSER QUERY: {query}\n\nGENERATE ONLY THE PYTHON CODE:"

    def _get_query_enhancements(self, query: str) -> str:
        """Get query-specific enhancements and suggestions."""
        enhancements = []

        if "correlation" in query.lower():
            enhancements.append(
                "CORRELATION ANALYSIS: Use pandas corr() method and consider creating a heatmap visualization."
            )

        if "trend" in query.lower() or "time" in query.lower():
            enhancements.append(
                "TIME SERIES ANALYSIS: Consider sorting by date and using line charts for trends."
            )

        if "outlier" in query.lower():
            enhancements.append(
                "OUTLIER DETECTION: Use IQR method, z-score, or box plots to identify outliers."
            )

        if "group" in query.lower():
            enhancements.append(
                "GROUPING: Use groupby() with multiple aggregation functions for comprehensive analysis."
            )

        if "missing" in query.lower():
            enhancements.append(
                "MISSING DATA: Check null values, suggest imputation strategies, and show missing data patterns."
            )

        return "\n".join(enhancements) if enhancements else ""

    def _get_analysis_prompt(self) -> str:
        """Get the enhanced analysis prompt template."""
        return """You are an expert Python data analyst specializing in pandas, numpy, matplotlib, and seaborn.
Generate clean, efficient, and production-ready Python code to answer user queries.

CRITICAL INSTRUCTIONS:
- Use df0, df1, df2... to reference the dataframes (NOT total0, total1, etc.)
- All necessary libraries are already available (pandas, numpy, matplotlib, seaborn)
- Write simple, clear code that answers the query directly
- Use descriptive variable names like 'total_revenue', 'avg_price', 'product_counts'
- Use pandas built-in methods over loops
- Return results using print() statements for clarity

AVAILABLE FUNCTIONS:
- save_plot(fig, filename) - saves plots to askpandas_plots/ directory
- create_bar_chart(), create_line_chart(), create_scatter_plot()
- create_histogram(), create_correlation_heatmap(), create_box_plot()

CODE QUALITY REQUIREMENTS:
- Keep code simple and readable
- Use meaningful variable names (e.g., 'total_revenue', not 'total0')
- Provide clear output formatting
- Focus on answering the specific query

EXAMPLE CODE STRUCTURE:
# Calculate total revenue
total_revenue = df0['revenue'].sum()
print(f"Total Revenue: ${total_revenue:,.2f}")

# For grouping operations
revenue_by_product = df0.groupby('product')['revenue'].sum()
print("Revenue by Product:")
print(revenue_by_product)

# For averages
avg_price = df0['price'].mean()
print(f"Average Price: ${avg_price:.2f}")

IMPORTANT: Use descriptive variable names like 'total_revenue', 'avg_price', 'product_counts' - NOT 'total0', 'total1', etc."""

    def _get_visualization_prompt(self) -> str:
        """Get the enhanced visualization prompt template."""
        return """You are an expert data visualization specialist. Create compelling, publication-ready charts.

VISUALIZATION GUIDELINES:
- Choose the most appropriate chart type for the data
- Use consistent color schemes and styling
- Add proper titles, labels, and legends
- Ensure charts are readable and professional
- Consider accessibility (color contrast, font sizes)
- Use appropriate scales and ranges
- Handle edge cases (empty data, single values)

CHART TYPES AND USE CASES:
- Bar Charts: Categorical comparisons, rankings
- Line Charts: Time series, trends, continuous data
- Scatter Plots: Correlation analysis, distribution patterns
- Histograms: Data distribution, frequency analysis
- Heatmaps: Correlation matrices, 2D data patterns
- Box Plots: Statistical summaries, outlier detection

STYLING RECOMMENDATIONS:
- Use seaborn default styles for consistency
- Set appropriate figure sizes (10x6 for standard, 12x8 for detailed)
- Use color palettes that are colorblind-friendly
- Add grid lines where they improve readability
- Rotate labels if they're too long"""

    def _get_data_quality_prompt(self) -> str:
        """Get the enhanced data quality prompt template."""
        return """You are a data quality expert. Perform comprehensive data quality assessment and cleaning.

DATA QUALITY CHECKLIST:
- Missing values: Count, percentage, patterns
- Duplicates: Identify and analyze duplicate records
- Data types: Verify and suggest optimizations
- Outliers: Detect and analyze unusual values
- Consistency: Check for data format consistency
- Completeness: Assess data coverage and gaps
- Validity: Verify data meets business rules

ANALYSIS APPROACH:
- Start with descriptive statistics
- Identify data quality issues systematically
- Provide actionable recommendations
- Show before/after comparisons where applicable
- Consider business impact of data issues

CLEANING STRATEGIES:
- Handle missing values appropriately (drop, impute, flag)
- Remove or flag duplicate records
- Convert data types for efficiency
- Standardize formats and values
- Create data quality summary reports"""

    def _get_statistical_prompt(self) -> str:
        """Get the enhanced statistical analysis prompt template."""
        return """You are a statistical analysis expert. Perform rigorous statistical analysis and hypothesis testing.

STATISTICAL METHODS:
- Descriptive statistics: mean, median, mode, variance, std
- Inferential statistics: confidence intervals, hypothesis tests
- Correlation analysis: Pearson, Spearman, correlation matrices
- Distribution analysis: normality tests, QQ plots
- Outlier detection: IQR, z-score, statistical tests
- Trend analysis: time series decomposition, seasonal patterns

ANALYSIS APPROACH:
- Start with exploratory data analysis (EDA)
- Choose appropriate statistical tests
- Interpret results with practical significance
- Consider assumptions and limitations
- Provide clear statistical conclusions

VISUALIZATION REQUIREMENTS:
- Use appropriate statistical plots
- Include confidence intervals where relevant
- Show distributions and relationships clearly
- Use statistical annotations on charts"""

    def _get_multi_dataframe_prompt(self) -> str:
        """Get the enhanced multi-dataframe prompt template."""
        return """
You are an expert in multi-dataset analysis and data integration. Work with multiple dataframes effectively.

INTEGRATION STRATEGIES:
- Identify common keys for joins
- Choose appropriate join types (inner, left, right, outer)
- Handle data type mismatches
- Resolve naming conflicts
- Ensure data consistency across datasets

ANALYSIS APPROACH:
- Start with individual dataset exploration
- Identify relationships and dependencies
- Perform cross-dataset analysis
- Create unified views and summaries
- Handle missing data in joined datasets

PERFORMANCE CONSIDERATIONS:
- Use efficient join operations
- Consider memory usage with large datasets
- Optimize query performance
- Use appropriate data structures

GENERATE ONLY THE PYTHON CODE:

# Your multi-dataframe analysis code here
# Use df0, df1, df2... to reference the dataframes
# All necessary libraries are already available
"""

    def _generate_code_with_retry(self, prompt: str, query: str, max_retries: int = 3) -> str:
        """Generate code with retry mechanism and fallback strategies."""
        for attempt in range(max_retries):
            try:
                response = self.llm.generate(prompt)
                code = self._extract_and_clean_code(response)

                # Validate generated code
                if self._validate_generated_code(code):
                    return code

                # If validation fails, try to fix common issues
                if attempt < max_retries - 1:
                    prompt = self._add_error_correction_hints(prompt, code)

            except Exception as e:
                if attempt == max_retries - 1:
                    raise CodeGenerationError(
                        f"Failed to generate code after {max_retries} attempts: {e}"
                    ) from e
                # Back off before retrying (helps with rate limits / transient errors)
                time.sleep(self.retry_backoff * (2**attempt))
                continue

        # Fallback to basic code generation
        return self._generate_fallback_code(query)

    def _extract_and_clean_code(self, response: str) -> str:
        """Extract and clean generated code from LLM response."""
        # Prefer the first fenced code block (```python, ```py or a bare ```)
        code_match = re.search(r"```(?:python|py)?[ \t]*\n(.*?)```", response, re.DOTALL)
        # Fallback: assume the entire response is code
        code = code_match.group(1) if code_match else response

        return self._clean_generated_code(code)

    def _clean_generated_code(self, code: str) -> str:
        """Remove markdown fences and import lines while preserving indentation."""
        code = re.sub(r"^\s*```(?:python|py)?\s*", "", code)
        code = re.sub(r"\s*```\s*$", "", code)

        cleaned_lines = []
        for line in code.splitlines():
            stripped = line.strip()
            # Libraries are pre-loaded in the sandbox; imports are not allowed there
            if stripped.startswith(("import ", "from ")):
                continue
            cleaned_lines.append(line.rstrip())

        body = "\n".join(cleaned_lines).strip("\n")
        # Remove common leading indentation (e.g. code indented inside a reply)
        body = textwrap.dedent(body).strip()
        if not body:
            body = "# No code generated"
        return "# All necessary libraries are already available\n" + body

    def _validate_generated_code(self, code: str) -> bool:
        """Validate that generated code meets quality standards."""
        try:
            # Basic syntax check
            compile(code, "<string>", "exec")

            # Check for dangerous operations
            dangerous_patterns = [
                r"import\s+os",
                r"import\s+subprocess",
                r"import\s+requests",
                r"open\(",
                r"file\(",
                r"exec\(",
                r"eval\(",
            ]

            return all(not re.search(pattern, code) for pattern in dangerous_patterns)

        except SyntaxError:
            return False

    def _add_error_correction_hints(self, prompt: str, failed_code: str) -> str:
        """Add hints for correcting common code generation errors."""
        hints = "\n\nCODE CORRECTION HINTS:\n"

        if "import" not in failed_code:
            hints += "- Ensure all necessary imports are included\n"

        if "print(" not in failed_code:
            hints += "- Include print statements to show results\n"

        if "save_plot(" not in failed_code and "chart" in prompt.lower():
            hints += "- Use save_plot() function to save visualizations\n"

        hints += "- Check for syntax errors and proper indentation\n"
        hints += "- Ensure all variables are defined before use\n"

        return prompt + hints

    def _generate_fallback_code(self, query: str) -> str:
        """Generate basic exploration code when LLM generation keeps failing."""
        return f"""# Fallback code (the LLM did not return valid code)
print("Shape of df0:", df0.shape)
print("Basic statistics for df0:")
print(df0.describe(include="all"))
print("Query:", {query!r})
print("Note: This is fallback output. Please check your LLM configuration.")
"""

    def _execute_code_enhanced(self, code: str, dataframes: list) -> Any:
        """Execute generated code with enhanced monitoring and error handling."""
        # Prepare execution environment
        local_vars = {f"df{i}": df.df for i, df in enumerate(dataframes)}

        # Add common aliases and utilities
        local_vars.update(
            {
                "pd": pd,
                "np": np,
                "plt": plt,
                "sns": sns,
                "len": len,
                "range": range,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "sum": sum,
                "max": max,
                "min": min,
                "sorted": sorted,
                "abs": abs,
                "round": round,
                "print": print,
                "type": type,
                "isinstance": isinstance,
                "any": any,
                "all": all,
                "filter": filter,
                "map": map,
                "enumerate": enumerate,
                "zip": zip,
            }
        )

        figures_before = set(plt.get_fignums())
        try:
            output = self.safe_executor.execute(code, local_vars)
        except Exception as e:
            # Provide helpful error messages
            if "timeout" in str(e).lower():
                return "Execution timed out. Consider simplifying your query or using smaller datasets."
            if "memory" in str(e).lower():
                return (
                    "Out of memory. Consider using smaller datasets or more efficient operations."
                )
            return f"Execution failed: {e!s}"
        finally:
            saved = self._save_open_figures(figures_before)
        if saved:
            output = output.rstrip("\n") + "\n" + "\n".join(saved)
        return output

    def _save_open_figures(self, figures_before: set[int]) -> list[str]:
        """Save and close figures the generated code created but did not save.

        Without this every chart request would leak an open matplotlib figure.
        """
        messages = []
        for num in sorted(set(plt.get_fignums()) - figures_before):
            fig = plt.figure(num)
            if fig.axes:
                messages.append(save_plot(fig, f"askpandas_figure_{time.time_ns()}_{num}.png"))
            plt.close(fig)
        return messages

    def _store_execution_history(
        self,
        query: str,
        code: str | None,
        result: Any,
        prompt_type: str,
        error: str | None = None,
    ) -> None:
        """Store detailed execution history with metadata."""
        history_entry = {
            "query": query,
            "code": code,
            "result": result,
            "prompt_type": prompt_type,
            "timestamp": pd.Timestamp.now(),
            "llm_model": getattr(self.llm, "model_name", "unknown"),
            "execution_time": getattr(self, "_last_execution_time", None),
            "memory_usage": getattr(self, "_last_memory_usage", None),
            "error": error,
            "success": error is None,
        }

        self.execution_history.append(history_entry)

    def get_execution_history(self) -> list[dict]:
        """Get the history of executed queries with enhanced metadata."""
        return self.execution_history

    def get_last_query(self) -> dict | None:
        """Get the most recent query execution details."""
        return self.execution_history[-1] if self.execution_history else None

    def clear_history(self) -> None:
        """Clear the execution history."""
        self.execution_history.clear()

    def get_engine_stats(self) -> dict[str, Any]:
        """Get comprehensive engine statistics."""
        total_queries = len(self.execution_history)
        successful_queries = len([q for q in self.execution_history if q.get("success", True)])
        failed_queries = total_queries - successful_queries

        # Calculate average execution time
        execution_times: list[float] = [
            q["execution_time"] for q in self.execution_history if q.get("execution_time")
        ]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Get prompt type distribution
        prompt_types: dict[str, int] = {}
        for entry in self.execution_history:
            prompt_type = entry.get("prompt_type", "unknown")
            prompt_types[prompt_type] = prompt_types.get(prompt_type, 0) + 1

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "success_rate": (
                (successful_queries / total_queries * 100) if total_queries > 0 else 0
            ),
            "average_execution_time": avg_execution_time,
            "prompt_type_distribution": prompt_types,
            "sandbox_stats": self.safe_executor.get_execution_stats(),
            "llm_info": {
                "model": getattr(self.llm, "model_name", "unknown"),
                "provider": type(self.llm).__name__,
                "available": getattr(self.llm, "is_available", lambda: False)(),
            },
        }

    def export_execution_history(self, format: str = "json") -> str:
        """Export execution history in various formats."""
        if format.lower() == "json":
            return json.dumps(self.execution_history, default=str, indent=2)
        if format.lower() == "csv":
            df = pd.DataFrame(self.execution_history)
            return df.to_csv(index=False)
        raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'.")

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics and optimization suggestions."""
        stats = self.get_engine_stats()

        # Performance analysis
        return {
            "success_rate": stats["success_rate"],
            "average_execution_time": stats["average_execution_time"],
            "query_complexity": self._analyze_query_complexity(),
            "optimization_suggestions": self._generate_optimization_suggestions(stats),
        }

    def _analyze_query_complexity(self) -> dict[str, Any]:
        """Analyze the complexity of executed queries."""
        if not self.execution_history:
            return {}

        complexity_metrics: dict[str, Any] = {
            "simple_queries": 0,
            "medium_queries": 0,
            "complex_queries": 0,
            "average_code_length": 0,
            "most_common_operations": {},
        }

        code_lengths = []
        operations = []

        for entry in self.execution_history:
            if entry.get("code"):
                code = entry["code"]
                code_lengths.append(len(code))

                # Count common operations
                if "groupby" in code:
                    operations.append("groupby")
                if "merge" in code or "join" in code:
                    operations.append("merge/join")
                if "plot" in code or "chart" in code:
                    operations.append("visualization")
                if "corr" in code:
                    operations.append("correlation")
                if "fillna" in code or "dropna" in code:
                    operations.append("data_cleaning")

        if code_lengths:
            complexity_metrics["average_code_length"] = sum(code_lengths) / len(code_lengths)

            # Classify complexity based on code length
            for length in code_lengths:
                if length < 200:
                    complexity_metrics["simple_queries"] += 1
                elif length < 500:
                    complexity_metrics["medium_queries"] += 1
                else:
                    complexity_metrics["complex_queries"] += 1

        # Count operations
        complexity_metrics["most_common_operations"] = dict(Counter(operations).most_common(5))

        return complexity_metrics

    def _generate_optimization_suggestions(self, stats: dict[str, Any]) -> list[str]:
        """Generate optimization suggestions based on performance metrics."""
        suggestions = []

        if stats["success_rate"] < 80:
            suggestions.append("Consider improving LLM prompt quality or using a different model")

        if stats.get("average_execution_time", 0) > 10:
            suggestions.append("Optimize code generation for faster execution")

        if stats.get("failed_queries", 0) > 0:
            suggestions.append("Review failed queries to identify common failure patterns")

        if len(stats.get("prompt_type_distribution", {})) < 3:
            suggestions.append("Diversify query types to test all prompt templates")

        return suggestions
