# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-10-31

### Added

- `askpandas.exceptions`: `AskPandasError` with `DataLoadError`, `LLMNotConfiguredError`,
  `LLMError`, `CodeGenerationError` and `QueryProcessingError`, all exported from `askpandas`.
  Each also subclasses the `ValueError`/`RuntimeError` raised before, so existing handlers work.
- The chart helpers (`create_bar_chart`, ...) are callable from generated code, and every prompt
  template now includes the sandbox rules (previously only the "analysis" template did).
- Figures that generated code creates but does not save are saved to `output_dir` and closed.
- `ap.DataFrame` / `validate_dataframe` accept `pathlib.Path`.
- `validate_query` returns `matched_columns`.
- Examples rewritten as four offline, runnable use cases (`examples/`), with sample data in
  `examples/data/`.
- CI runs mypy and enforces 85% coverage; CodeQL workflow; pre-commit config.

### Fixed

- `StatisticalAnalyzer.hypothesis_testing` with `"mann_whitney"`, `"kruskal_wallis"` or
  `"t_test_paired"` raised `AttributeError` (the methods were nested inside another function).
- `"anova"` always failed ("truth value of a Series is ambiguous"); eta squared is now computed
  from the pooled observations.
- `correlation_analysis` p-values used columns with NaNs dropped independently (misaligned
  samples); missing values are now dropped pairwise.
- The `benchmark_function` decorator always raised `KeyError`; it now returns the function's
  value, logs instead of printing, and re-raises the original exception on failure.
- Peak memory was always 0.0 outside Windows.
- `validate_query` flagged every English word as a missing column.
- A later `set_llm()` was ignored by existing `AskDataFrame` objects.
- Execution history recorded sandbox failures as successes and never recorded execution time.
- `copy.copy(AskDataFrame)` recursed forever.
- `get_plot_colors` returned an RGBA array instead of the documented list of colour strings.
- Bare `except:` clauses replaced with specific exceptions.

### Changed

- Importing `askpandas` no longer changes the global matplotlib/seaborn style; use
  `set_config(plot_style=...)` to apply one.
- `verbose=True` logs through the `askpandas` logger instead of printing.
- Ruff rule set broadened (`SIM`, `C4`, `RUF`, `PTH`, `RET`, `PIE`); mypy config added.
- Removed stale root-level demo scripts and status documents.

## [0.2.0] - 2026-10-31

### Fixed

- **Generated code lost its indentation**: the code cleaner stripped every line, so any
  LLM answer containing a `for`/`if` block failed validation and fell back to generic output.
  Indentation is now preserved (and common leading indentation removed).
- **Sandbox builtins were empty** when AskPandas was imported as a package (it read
  `__builtins__`, which is a dict outside `__main__`). It now uses the `builtins` module.
- **List comprehensions could not see `df0`, `df1`, ...** on Python 3.10/3.11 because code ran
  with separate globals/locals. Code now runs in a single namespace.
- Warnings written to stderr replaced the actual printed result; both are now returned.
- The fallback code referenced `df1`/`df2` even with one DataFrame and raised `NameError`.
- **`HuggingFaceLLM` was broken**: `api-inference.huggingface.co` no longer resolves. It now uses
  the Hugging Face Inference Providers router (`https://router.huggingface.co/v1`, OpenAI-compatible),
  reads `HF_TOKEN`/`HF_API_KEY`, and raises a clear error instead of blocking on `input()`.
- **pandas 3 compatibility**: text columns (now `str` dtype instead of `object`) were not detected
  as categorical in summaries, data-type suggestions, data-quality and statistics helpers.
- `create_bar_chart` crashed on numeric x values; `save_plot` ignored `set_config(output_dir=...)`.
- `scipy` and `psutil` were imported but not declared as dependencies.
- Code fences without a language tag (```` ``` ```` or ```` ```py ````) are now recognized.

### Added

- `OpenAICompatibleLLM` for any OpenAI-compatible Chat Completions API, with `.openai()` and
  `.mistral()` presets (OpenAI, Mistral, vLLM, LM Studio, Groq, Together, Ollama `/v1`, ...).
- `BaseLLM` exported at package level; `OllamaLLM` accepts `temperature` and `timeout`.
- Retry with exponential backoff after LLM errors (configurable via `retry_backoff`).
- Sandbox blocks dunder attribute/name access (common restricted-builtins escape) and removes
  introspection builtins (`getattr`, `vars`, `dir`, `compile`, `breakpoint`, ...).
- `askpandas.__version__` from package metadata, `py.typed`, type hints on the public API.
- Offline test suite for the engine, sandbox and LLM clients (mocked HTTP), GitHub Actions CI
  (Ruff + pytest on Python 3.10-3.13) and community files.

### Changed

- Packaging moved to `pyproject.toml` (PEP 639 `license = "MIT"`); `setup.py`, `requirements.txt`
  and committed build artifacts removed. Requires Python 3.10+.
- **Removed unused heavy dependencies** `torch`, `transformers` and `faker` (faker is now the
  optional `demo` extra). Installing AskPandas no longer pulls in PyTorch.
- Default Hugging Face model is now `Qwen/Qwen2.5-Coder-7B-Instruct`; `get_available_models()`
  updated (removed `gpt2`/`DialoGPT`, which cannot follow code-generation prompts).
- Linting switched from black/flake8 to Ruff.
- README: hosted-LLM guide, API overview, environment variables, safety note; removed
  unverifiable testimonials.

## [0.1.1] - 2025

- Previous release on PyPI.

## [0.1.0] - 2025

- Initial release.
