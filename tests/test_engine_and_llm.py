"""Tests for the query engine, sandbox and LLM clients (network calls are mocked)."""

from __future__ import annotations

from typing import Any
from unittest import mock

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

import askpandas as ap
from askpandas.core.engine import AskPandasEngine
from askpandas.security.sandbox import SafeExecutor
from askpandas.utils.helpers import detect_data_types, is_numeric_column, is_text_column


class FakeLLM(ap.BaseLLM):
    """Returns canned responses in order and records the prompts it received."""

    def __init__(self, *responses: str) -> None:
        self.responses = list(responses)
        self.prompts: list[str] = []
        self.model_name = "fake"

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]

    def is_available(self) -> bool:
        return True


@pytest.fixture
def sales() -> ap.AskDataFrame:
    return ap.DataFrame(
        {
            "country": ["US", "UK", "US", "DE"],
            "product": ["a", "b", "c", "a"],
            "revenue": [100, 50, 25, 75],
        }
    )


# ----------------------------------------------------------------- package level


def test_version_matches_metadata() -> None:
    from importlib.metadata import version

    assert ap.__version__ == version("askpandas")


def test_all_exports_resolve() -> None:
    for name in ap.__all__:
        assert hasattr(ap, name), name


def test_set_llm_validates_interface() -> None:
    with pytest.raises(ValueError):
        ap.set_llm(object())


def test_chat_requires_llm_and_dataframes(sales: ap.AskDataFrame) -> None:
    ap.config.llm = None
    with pytest.raises(ValueError, match="No LLM configured"):
        ap.chat("total revenue", sales)
    ap.set_llm(FakeLLM("print(1)"))
    with pytest.raises(ValueError, match="At least one dataframe"):
        ap.chat("total revenue")
    ap.config.llm = None


# ------------------------------------------------------------------------ engine


def test_engine_runs_code_from_markdown_block(sales: ap.AskDataFrame) -> None:
    llm = FakeLLM(
        "Here you go:\n```python\nimport pandas as pd\n"
        "total = df0['revenue'].sum()\nprint(f'Total: {total}')\n```\nDone."
    )
    result = AskPandasEngine(llm).process_query("What is the total revenue?", [sales])
    assert result.strip() == "Total: 250"
    assert "USER QUERY: What is the total revenue?" in llm.prompts[0]
    assert "revenue" in llm.prompts[0]  # dataframe context included


def test_engine_preserves_indentation(sales: ap.AskDataFrame) -> None:
    code = (
        "```python\n"
        "for country, value in df0.groupby('country')['revenue'].sum().items():\n"
        "    if value > 60:\n"
        "        print(country, value)\n"
        "```"
    )
    result = AskPandasEngine(FakeLLM(code)).process_query("Countries over 60", [sales])
    assert result.split("\n")[:2] == ["DE 75", "US 125"]


def test_engine_comprehension_can_see_dataframes(sales: ap.AskDataFrame) -> None:
    code = "```py\nprint([float(df0[c].mean()) for c in ['revenue']])\n```"
    result = AskPandasEngine(FakeLLM(code)).process_query("mean", [sales])
    assert result.strip() == "[62.5]"


def test_engine_multiple_dataframes() -> None:
    left = ap.DataFrame({"id": [1, 2], "name": ["A", "B"]})
    right = ap.DataFrame({"id": [1, 2], "value": [10, 20]})
    code = "```python\nmerged = df0.merge(df1, on='id')\nprint(merged['value'].sum())\n```"
    result = ap.AskPandasEngine(FakeLLM(code)).process_query("join and sum", [left, right])
    assert result.strip() == "30"


def test_engine_falls_back_when_code_is_invalid(sales: ap.AskDataFrame) -> None:
    engine = AskPandasEngine(FakeLLM("this is not python ((("))
    result = engine.process_query("anything", [sales])
    assert "fallback output" in result
    assert "Shape of df0: (4, 3)" in result


def test_engine_history_and_stats(sales: ap.AskDataFrame) -> None:
    engine = AskPandasEngine(FakeLLM("print(df0.shape[0])"))
    engine.process_query("how many rows", [sales])
    last = engine.get_last_query()
    assert last["query"] == "how many rows" and last["success"]
    stats = engine.get_engine_stats()
    assert stats["total_queries"] == 1
    assert '"query": "how many rows"' in engine.export_execution_history("json")
    engine.clear_history()
    assert engine.get_execution_history() == []


def test_dataframe_chat_uses_global_llm(sales: ap.AskDataFrame) -> None:
    ap.set_llm(FakeLLM("print(df0['revenue'].max())"))
    try:
        assert sales.chat("max revenue").strip() == "100"
    finally:
        ap.config.llm = None


# ----------------------------------------------------------------------- sandbox


def test_sandbox_blocks_imports_and_dunder_escapes() -> None:
    ex = SafeExecutor()
    assert "not allowed" in ex.execute("import os", {})
    assert "not allowed" in ex.execute("print(().__class__.__bases__)", {})
    assert "not allowed" in ex.execute("open('x.txt', 'w')", {})
    assert "not allowed" in ex.execute("__import__('os')", {})


def test_sandbox_provides_safe_builtins_without_engine_help() -> None:
    out = SafeExecutor().execute("print(len(range(3)), sorted([3, 1, 2]))", {})
    assert out.strip() == "3 [1, 2, 3]"


def test_sandbox_reports_runtime_errors() -> None:
    assert SafeExecutor().execute("print(1 / 0)", {}).startswith("Execution failed")


# ------------------------------------------------------------------- LLM clients


def _response(json_data: Any, status: int = 200) -> mock.Mock:
    resp = mock.Mock(status_code=status)
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


def test_openai_compatible_generate_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    llm = ap.OpenAICompatibleLLM.mistral(temperature=0.0, max_tokens=50)
    reply = {"choices": [{"message": {"content": "print(1)"}}]}
    with mock.patch("askpandas.llm.openai_compatible.requests.post") as post:
        post.return_value = _response(reply)
        assert llm.generate("hello") == "print(1)"
    url = post.call_args.args[0]
    kwargs = post.call_args.kwargs
    assert url == "https://api.mistral.ai/v1/chat/completions"
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"]["model"] == "mistral-small-latest"
    assert kwargs["json"]["messages"][-1] == {"role": "user", "content": "hello"}
    assert kwargs["json"]["max_tokens"] == 50


def test_openai_compatible_error_is_wrapped(monkeypatch: pytest.MonkeyPatch) -> None:
    llm = ap.OpenAICompatibleLLM("m", base_url="http://localhost:1/v1", api_key="k")
    with (
        mock.patch(
            "askpandas.llm.openai_compatible.requests.post", side_effect=ConnectionError("down")
        ),
        pytest.raises(RuntimeError, match="down"),
    ):
        llm.generate("x")


def test_openai_compatible_is_available(monkeypatch: pytest.MonkeyPatch) -> None:
    llm = ap.OpenAICompatibleLLM.openai(api_key="k")
    with mock.patch("askpandas.llm.openai_compatible.requests.get") as get:
        get.return_value = _response({}, status=200)
        assert llm.is_available()
        get.return_value = _response({}, status=401)
        assert not llm.is_available()


def test_huggingface_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("HF_API_KEY", raising=False)
    with pytest.raises(ValueError, match="Hugging Face token"):
        ap.HuggingFaceLLM()


def test_huggingface_uses_router(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_TOKEN", "hf_test")
    llm = ap.HuggingFaceLLM("meta-llama/Llama-3.1-8B-Instruct")
    assert llm.base_url == "https://router.huggingface.co/v1"
    assert llm.headers["Authorization"] == "Bearer hf_test"
    with mock.patch("askpandas.llm.openai_compatible.requests.post") as post:
        post.return_value = _response({"choices": [{"message": {"content": "ok"}}]})
        assert llm.generate("hi") == "ok"
    assert post.call_args.args[0] == "https://router.huggingface.co/v1/chat/completions"


def test_ollama_generate_and_availability() -> None:
    llm = ap.OllamaLLM(model_name="llama3.1", host="http://ollama:11434/")
    with mock.patch("askpandas.llm.ollama_client.requests.post") as post:
        post.return_value = _response({"response": "print(2)"})
        assert llm.generate("p") == "print(2)"
    assert post.call_args.args[0] == "http://ollama:11434/api/generate"
    assert post.call_args.kwargs["json"]["model"] == "llama3.1"
    import requests

    with mock.patch(
        "askpandas.llm.ollama_client.requests.get",
        side_effect=requests.ConnectionError(),
    ):
        assert llm.is_available() is False


# ------------------------------------------------------------- dtype handling


def test_text_and_numeric_column_detection() -> None:
    df = pd.DataFrame({"s": ["a", "b"], "i": [1, 2], "f": [1.5, 2.5], "b": [True, False]})
    assert is_text_column(df["s"])
    assert not is_text_column(df["i"])
    assert is_numeric_column(df["i"]) and is_numeric_column(df["f"])
    assert not is_numeric_column(df["b"])


def test_string_columns_are_categorical_on_any_pandas(sales: ap.AskDataFrame) -> None:
    types = detect_data_types(sales.df)
    assert types["country"] == "categorical"
    assert types["revenue"] == "int"
    info = sales.get_column_info("country")
    assert info["most_common"] == "US"
    assert "country" in sales.get_summary_stats()["categorical_columns"]


def test_engine_retries_then_raises_on_llm_errors(sales: ap.AskDataFrame) -> None:
    class BrokenLLM(FakeLLM):
        def generate(self, prompt: str) -> str:
            self.prompts.append(prompt)
            raise RuntimeError("rate limited")

    llm = BrokenLLM("unused")
    engine = AskPandasEngine(llm, config={"retry_backoff": 0})
    with pytest.raises(RuntimeError, match="after 3 attempts: rate limited"):
        engine.process_query("total", [sales])
    assert len(llm.prompts) == 3
    assert engine.get_last_query()["success"] is False


def test_save_plot_uses_configured_output_dir(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    import matplotlib.pyplot as plt

    from askpandas.visualization.charts import save_plot

    monkeypatch.setattr(ap.config, "output_dir", str(tmp_path / "plots"))
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])
    msg = save_plot(fig, "line.png", dpi=50)
    assert (tmp_path / "plots" / "line.png").exists()
    assert "line.png" in msg
