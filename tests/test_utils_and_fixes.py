"""Tests for the statistics, data-quality, performance and chart helpers, plus
regression tests for bugs fixed in 0.2.1. Everything runs offline."""

from __future__ import annotations

import copy
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import askpandas as ap
from askpandas.core.engine import AskPandasEngine
from askpandas.security.sandbox import SafeExecutor
from askpandas.utils import data_quality, performance, statistical
from askpandas.utils.helpers import format_number, validate_dataframe
from askpandas.visualization import charts


class FakeLLM(ap.BaseLLM):
    """Always answers with the same reply."""

    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.prompts: list[str] = []
        self.model_name = "fake"

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.reply

    def is_available(self) -> bool:
        return True


@pytest.fixture
def numbers() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    x = rng.normal(size=60)
    return pd.DataFrame(
        {
            "x": x,
            "y": 2 * x + rng.normal(scale=0.1, size=60),
            "noise": rng.normal(size=60),
            "group": ["a", "b", "c"] * 20,
            "flag": ["yes", "no"] * 30,
        }
    )


@pytest.fixture(autouse=True)
def _restore_config(tmp_path: Path):
    """Keep tests from leaking global config or writing plots into the repo."""
    saved = ap.get_config()
    saved_llm = ap.get_llm()
    ap.set_config(output_dir=str(tmp_path / "plots"))
    yield
    ap.config.update(**saved)
    ap.config.llm = saved_llm
    plt.close("all")


# --------------------------------------------------------------- exceptions


def test_exception_hierarchy_is_backward_compatible() -> None:
    assert issubclass(ap.LLMNotConfiguredError, ValueError)
    assert issubclass(ap.DataLoadError, ValueError)
    assert issubclass(ap.QueryProcessingError, RuntimeError)
    assert issubclass(ap.CodeGenerationError, RuntimeError)
    assert issubclass(ap.LLMError, RuntimeError)
    for exc in (ap.LLMNotConfiguredError, ap.DataLoadError, ap.LLMError):
        assert issubclass(exc, ap.AskPandasError)


def test_chat_without_llm_raises_specific_error() -> None:
    ap.config.llm = None
    with pytest.raises(ap.LLMNotConfiguredError):
        ap.chat("total?", pd.DataFrame({"a": [1]}))
    with pytest.raises(ap.LLMNotConfiguredError):
        ap.DataFrame({"a": [1]}).chat("total?")


def test_unknown_config_key_lists_valid_keys() -> None:
    with pytest.raises(ValueError, match="output_dir"):
        ap.set_config(not_a_key=1)


# ------------------------------------------------------------ data loading


def test_validate_dataframe_accepts_pathlib(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    pd.DataFrame({"a": [1, 2]}).to_csv(path, index=False)
    assert validate_dataframe(path)["a"].tolist() == [1, 2]
    json_path = tmp_path / "data.JSON"
    pd.DataFrame({"a": [3]}).to_json(json_path)
    assert validate_dataframe(json_path)["a"].tolist() == [3]


def test_validate_dataframe_errors_are_data_load_errors(tmp_path: Path) -> None:
    with pytest.raises(ap.DataLoadError, match="Unsupported file format"):
        validate_dataframe("data.parquet")
    with pytest.raises(ap.DataLoadError, match="Could not read"):
        validate_dataframe(tmp_path / "missing.csv")
    with pytest.raises(ap.DataLoadError):
        ap.DataFrame(42)


def test_format_number() -> None:
    assert format_number(1_500_000) == "1.50M"
    assert format_number(2500) == "2.50K"
    assert format_number(3) == "3.00"
    assert format_number("n/a") == "n/a"  # type: ignore[arg-type]


# ------------------------------------------------------------ AskDataFrame


def test_askdataframe_can_be_copied() -> None:
    adf = ap.DataFrame({"a": [1, 2]})
    clone = copy.copy(adf)
    assert clone.df.equals(adf.df)
    assert copy.deepcopy(adf).shape() == (2, 1)


def test_dataframe_follows_new_llm_after_set_llm() -> None:
    adf = ap.DataFrame({"a": [1, 2]})
    ap.set_llm(FakeLLM("```python\nprint('first')\n```"))
    assert "first" in adf.chat("q")
    ap.set_llm(FakeLLM("```python\nprint('second')\n```"))
    assert "second" in adf.chat("q")
    assert len(adf._engine.get_execution_history()) == 2  # history kept


def test_set_config_verbose_logs_instead_of_printing(
    caplog: pytest.LogCaptureFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    with caplog.at_level(logging.INFO, logger="askpandas"):
        ap.set_config(verbose=True)
        ap.set_llm(FakeLLM("x"))
    assert "LLM set to: FakeLLM" in caplog.text
    assert capsys.readouterr().out == ""


# ---------------------------------------------------------------- engine


def test_chart_helpers_are_callable_from_generated_code(tmp_path: Path) -> None:
    reply = (
        "```python\n"
        "totals = df0.groupby('country', as_index=False)['revenue'].sum()\n"
        "fig = create_bar_chart(totals, 'country', 'revenue', title='Revenue')\n"
        "print(save_plot(fig, 'revenue.png'))\n"
        "```"
    )
    engine = AskPandasEngine(FakeLLM(reply))
    df = ap.DataFrame({"country": ["US", "UK", "US"], "revenue": [1, 2, 3]})
    out = engine.process_query("bar chart of revenue by country", [df])
    assert "Plot saved to" in out
    assert (tmp_path / "plots" / "revenue.png").exists()


def test_unsaved_figures_are_saved_and_closed(tmp_path: Path) -> None:
    reply = "```python\nfig, ax = plt.subplots()\nax.plot([1, 2, 3])\nprint('drawn')\n```"
    engine = AskPandasEngine(FakeLLM(reply))
    before = len(plt.get_fignums())
    out = engine.process_query("plot it", [ap.DataFrame({"a": [1]})])
    assert "drawn" in out
    assert "Plot saved to" in out
    assert len(plt.get_fignums()) == before
    assert list((tmp_path / "plots").glob("askpandas_figure_*.png"))


def test_every_prompt_type_includes_sandbox_rules() -> None:
    llm = FakeLLM("```python\nprint(1)\n```")
    engine = AskPandasEngine(llm)
    df = ap.DataFrame({"a": [1, 2]})
    for query in ["plot a chart", "find missing values", "correlation", "merge both", "total"]:
        engine.process_query(query, [df])
    assert all("SANDBOX RULES" in p and "df0" in p for p in llm.prompts)


def test_history_records_sandbox_failures_and_timing() -> None:
    engine = AskPandasEngine(FakeLLM("```python\nprint(df0['missing'])\n```"))
    out = engine.process_query("q", [ap.DataFrame({"a": [1]})])
    assert out.startswith("Execution failed")
    last = engine.get_last_query()
    assert last is not None
    assert last["success"] is False
    assert last["execution_time"] is not None
    stats = engine.get_engine_stats()
    assert stats["failed_queries"] == 1
    assert stats["average_execution_time"] > 0
    metrics = engine.get_performance_metrics()
    assert "optimization_suggestions" in metrics
    assert metrics["query_complexity"]["simple_queries"] == 1


def test_export_history_formats() -> None:
    engine = AskPandasEngine(FakeLLM("```python\nprint(df0['a'].sum())\n```"))
    engine.process_query("total", [ap.DataFrame({"a": [1, 2]})])
    assert '"query": "total"' in engine.export_execution_history("json")
    assert "query" in engine.export_execution_history("csv").splitlines()[0]
    with pytest.raises(ValueError, match="Unsupported format"):
        engine.export_execution_history("xml")
    engine.clear_history()
    assert engine.get_execution_history() == []


def test_engine_context_mentions_quality_insights() -> None:
    engine = AskPandasEngine(FakeLLM("x"))
    df = ap.DataFrame(
        {"when": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"], "v": [1, 2, 3, 100]}
    )
    context = engine._generate_enhanced_context([df])
    assert "df0" in context
    assert "'when': 'datetime'" in context
    assert "v: 1 potential outliers" in context


def test_sandbox_last_error_resets_after_success() -> None:
    executor = SafeExecutor()
    executor.execute("import os", {})
    assert executor.last_error is not None
    assert executor.execute("print(1)", {}).strip() == "1"
    assert executor.last_error is None


# ------------------------------------------------------------ query checks


def test_validate_query_ignores_plain_english_words() -> None:
    result = ap.validate_query("Show total revenue by region for 'New York'", ["revenue", "region"])
    assert result["is_valid"] is True
    assert result["matched_columns"] == ["revenue", "region"]


def test_validate_query_flags_explicit_unknown_columns() -> None:
    result = ap.validate_query("average unit_price by `Segment`", ["Revenue", "segment"])
    assert result["is_valid"] is False
    assert result["missing_columns"] == ["unit_price"]
    assert result["matched_columns"] == ["segment"]
    assert ap.validate_query("   ", ["a"])["errors"] == ["Query cannot be empty"]


# --------------------------------------------------------------- statistics


def test_correlation_analysis_handles_missing_values(numbers: pd.DataFrame) -> None:
    numbers.loc[0, "x"] = np.nan
    numbers.loc[5, "y"] = np.nan
    result = statistical.StatisticalAnalyzer(numbers).correlation_analysis()
    # Independent dropna() used to misalign the samples and yield NaN here
    assert result["p_values"].loc["x", "y"] < 1e-10
    pairs = [c["variables"] for c in result["significant_correlations"]]
    assert ("x", "y") in pairs


@pytest.mark.parametrize("method", ["spearman", "kendall"])
def test_correlation_methods(numbers: pd.DataFrame, method: str) -> None:
    result = statistical.StatisticalAnalyzer(numbers).correlation_analysis(method=method)
    assert result["method"] == method
    assert result["p_values"].loc["x", "y"] < 0.001


def test_correlation_needs_two_numeric_columns() -> None:
    result = statistical.StatisticalAnalyzer(pd.DataFrame({"a": [1, 2]})).correlation_analysis()
    assert "error" in result


@pytest.mark.parametrize(
    ("test_type", "kwargs", "key"),
    [
        (
            "mann_whitney",
            {"group_col": "flag", "value_col": "x", "group1": "yes", "group2": "no"},
            "u_statistic",
        ),
        ("kruskal_wallis", {"group_col": "group", "value_col": "x"}, "h_statistic"),
        (
            "t_test_independent",
            {"group_col": "flag", "value_col": "x", "group1": "yes", "group2": "no"},
            "t_statistic",
        ),
        ("anova", {"group_col": "group", "value_col": "x"}, "f_statistic"),
        ("chi_square", {"var1": "group", "var2": "flag"}, "chi2_statistic"),
    ],
)
def test_hypothesis_tests(numbers: pd.DataFrame, test_type: str, kwargs: dict, key: str) -> None:
    result = statistical.StatisticalAnalyzer(numbers).hypothesis_testing(test_type, **kwargs)
    assert "error" not in result, result
    assert key in result
    assert 0.0 <= result["p_value"] <= 1.0


def test_anova_effect_size_matches_definition() -> None:
    df = pd.DataFrame({"g": ["a"] * 3 + ["b"] * 3, "v": [1.0, 2.0, 3.0, 5.0, 6.0, 7.0]})
    result = statistical.StatisticalAnalyzer(df).hypothesis_testing(
        "anova", group_col="g", value_col="v"
    )
    # SS_between = 3*(2-4)^2 + 3*(6-4)^2 = 24, SS_total = 24 + 4 = 28
    assert result["effect_size"] == pytest.approx(24 / 28)


def test_hypothesis_testing_reports_unknown_and_unimplemented(numbers: pd.DataFrame) -> None:
    analyzer = statistical.StatisticalAnalyzer(numbers)
    assert "error" in analyzer.hypothesis_testing("nope")
    paired = analyzer.hypothesis_testing(
        "t_test_paired", group_col="flag", value_col="x", group1="yes", group2="no"
    )
    assert "not yet implemented" in paired["error"]


def test_descriptive_outliers_normality_distribution(numbers: pd.DataFrame) -> None:
    numbers.loc[0, "noise"] = 50.0
    analyzer = statistical.StatisticalAnalyzer(numbers)
    desc = analyzer.descriptive_statistics()
    assert set(desc) == {"x", "y", "noise"}
    for method, key in (("iqr", "iqr"), ("zscore", "zscore"), ("both", "combined")):
        outliers = analyzer.outlier_detection(["noise"], method=method)
        assert outliers["noise"][key]["count"] >= 1, method
        assert 0 in outliers["noise"][key]["indices"]
    assert "noise" in analyzer.normality_tests()
    assert "noise" in analyzer.distribution_analysis()
    report = analyzer.generate_statistical_report()
    assert "STATISTICAL" in report.upper()


def test_module_level_statistical_helpers(numbers: pd.DataFrame) -> None:
    assert "x" in statistical.quick_stats(numbers)
    assert statistical.correlation_matrix(numbers).shape == (3, 3)
    assert "x" in statistical.detect_outliers(numbers, ["x"])


# ------------------------------------------------------------- data quality


@pytest.fixture
def messy() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": [" Alice", "bob ", "Carol", "Carol", None, "dave"],
            "age": [25, -3, 40, 40, 33, 200],
            "amount": ["10", "20", "30", "30", "40", "x"],
            "joined": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-03-01", None, "2024-05-01"],
        }
    )


def test_quality_assessment_finds_issues(messy: pd.DataFrame) -> None:
    report = data_quality.assess_data_quality(messy)
    assert report["duplicates"]["total_duplicates"] == 1
    assert report["missing_data"]["total_missing"] == 2
    assert 0 <= report["data_quality_score"] <= 100
    issues = {i["type"] for i in report["consistency"]["logical_inconsistencies"]}
    assert "negative_age" in issues
    assert report["recommendations"]
    text = data_quality.generate_quality_report(messy)
    assert "Overall Quality Score" in text


def test_auto_clean(messy: pd.DataFrame) -> None:
    cleaned, log = data_quality.clean_dataframe(messy)
    assert cleaned["name"].iloc[0] == "Alice"  # whitespace stripped
    assert pd.api.types.is_numeric_dtype(cleaned["amount"])
    assert "Converted amount to numeric type" in log
    aggressive, agg_log = data_quality.clean_dataframe(messy, aggressive=True)
    assert len(aggressive) < len(messy)
    assert "Removed 1 duplicate rows" in agg_log
    assert aggressive["name"].isna().sum() == 0
    cleaner = data_quality.DataCleaner(messy)
    cleaner.auto_clean()
    summary = cleaner.get_cleaning_summary()
    assert summary["original_shape"] == messy.shape
    assert cleaner.get_cleaning_log() == summary["cleaning_log"]


# -------------------------------------------------------------- performance


def test_benchmark_operation_keeps_result_and_error() -> None:
    bench = performance.PerformanceBenchmark()
    ok = bench.benchmark_operation("sum", lambda a, b: a + b, 2, 3)
    assert ok["success"] is True
    assert ok["result"] == 5
    bad = bench.benchmark_operation("boom", lambda: 1 / 0)
    assert bad["success"] is False
    assert "division by zero" in bad["error"]
    summary = bench.get_benchmark_summary()
    assert summary["total_operations"] == 2
    assert summary["successful_operations"] == 1
    bench.clear_benchmarks()
    assert bench.benchmarks == {}


def test_benchmark_decorator_returns_value_and_reraises(
    caplog: pytest.LogCaptureFixture,
) -> None:
    @performance.benchmark_function("adder")
    def add(a: int, b: int) -> int:
        return a + b

    @performance.benchmark_function()
    def fail() -> None:
        raise KeyError("missing")

    with caplog.at_level(logging.INFO, logger="askpandas.utils.performance"):
        assert add(2, 3) == 5
    assert "Benchmark adder" in caplog.text
    with pytest.raises(KeyError):
        fail()


def test_benchmark_dataframe_operations_and_compare() -> None:
    bench = performance.PerformanceBenchmark()
    df = pd.DataFrame({"a": range(100)})
    results = bench.benchmark_dataframe_operations(
        df, [{"name": "sum", "function": lambda d: d["a"].sum()}]
    )
    assert results["sum"]["result"] == 4950
    comparison = bench.compare_operations(
        [
            {"name": "fast", "operations": [{"name": "noop", "function": lambda: None}]},
            {
                "name": "slow",
                "operations": [{"name": "sum", "function": lambda: sum(range(10**5))}],
            },
        ]
    )
    assert {s["name"] for s in comparison["performance_ranking"]} == {"fast", "slow"}
    assert len(comparison["operation_sets"]) == 2


def test_optimizer_and_optimize_dataframe() -> None:
    df = pd.DataFrame(
        {
            "small_int": np.arange(1000, dtype="int64") % 100,
            "flt": np.linspace(0, 1, 1000),
            "cat": ["a", "b"] * 500,
        }
    )
    analysis = performance.PerformanceOptimizer().analyze_dataframe_performance(df)
    assert "size_analysis" in analysis
    assert analysis["recommendations"] is not None
    optimized, applied = performance.optimize_dataframe(df)
    assert optimized.memory_usage(deep=True).sum() < df.memory_usage(deep=True).sum()
    assert applied


def test_peak_memory_is_positive_on_this_platform() -> None:
    assert performance.PerformanceOptimizer()._get_peak_memory() > 0


def test_memory_tracker() -> None:
    tracker = performance.MemoryTracker()
    usage = tracker.get_memory_usage()
    assert usage["rss"] > 0
    trend = tracker.get_memory_trend(duration=0.05, interval=0.01)
    assert trend


# ------------------------------------------------------------------- charts


def test_all_chart_helpers_produce_figures(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "category": ["a long category name", "b", "c"],
            "value": [3, 1, 2],
            "other": [1.0, 2.0, 3.5],
            "size": [10, 20, 30],
        }
    )
    figures = [
        charts.create_bar_chart(df, "category", "value", title="t"),
        charts.create_line_chart(df, "category", "value", title="t"),
        charts.create_scatter_plot(df, "value", "other", title="t"),
        charts.create_scatter_plot(df, "value", "other", color_col="size"),
        charts.create_scatter_plot(df, "value", "other", size_col="size"),
        charts.create_scatter_plot(df, "value", "other", color_col="size", size_col="size"),
        charts.create_histogram(df, "other", bins=3, title="t"),
        charts.create_correlation_heatmap(df),
        charts.create_box_plot(df, "category", "value", title="t"),
    ]
    for i, fig in enumerate(figures):
        assert fig.axes
        assert "Plot saved" in charts.save_plot(fig, f"f{i}.png", output_dir=str(tmp_path))
    assert len(list(tmp_path.glob("*.png"))) == len(figures)


def test_heatmap_requires_numeric_columns() -> None:
    with pytest.raises(ValueError, match="No numeric columns"):
        charts.create_correlation_heatmap(pd.DataFrame({"a": ["x"]}))


def test_save_plot_failure_is_reported(tmp_path: Path) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("not a directory")
    fig, _ = plt.subplots()
    assert charts.save_plot(fig, "x.png", output_dir=str(blocker)).startswith("Failed")


@pytest.mark.parametrize("style", ["seaborn", "minimal", "dark", "default"])
def test_set_plot_style(style: str) -> None:
    charts.set_plot_style(style)
    plt.style.use("default")


def test_plot_colors_are_hex() -> None:
    colors = charts.get_plot_colors(4)
    assert len(colors) == 4
    assert all(c.startswith("#") and len(c) == 7 for c in colors)


def test_import_does_not_change_global_style() -> None:
    import subprocess
    import sys

    code = (
        "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; "
        "before = dict(plt.rcParams); import askpandas; "
        "assert dict(plt.rcParams) == before"
    )
    subprocess.run([sys.executable, "-c", code], check=True)
