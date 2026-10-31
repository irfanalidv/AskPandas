# Contributing to askpandas

Thanks for helping improve `askpandas`!

## Development setup

```bash
git clone https://github.com/irfanalidv/AskPandas.git
cd AskPandas
uv venv && source .venv/bin/activate   # or: python -m venv .venv
uv pip install -e ".[dev]"             # or: pip install -e ".[dev]"
pre-commit install                     # run Ruff on every commit
```

## Before opening a pull request

```bash
ruff check .                                   # lint
ruff format --check .                          # formatting
mypy askpandas                                 # type-check
pytest --cov=askpandas --cov-fail-under=85     # tests (all offline, LLM calls are mocked)
```

- Add or update tests for any behaviour change.
- Add a line to `CHANGELOG.md` under **Unreleased**.
- Keep pull requests focused: one fix or feature per PR.

## Reporting bugs and requesting features

Use the [issue templates](https://github.com/irfanalidv/AskPandas/issues/new/choose).
