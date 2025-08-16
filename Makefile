.PHONY: help install install-dev install-full clean test test-cov lint format type-check build dist demo examples

help:  ## Show this help message
	@echo "AskPandas Development Commands"
	@echo "=============================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install AskPandas in development mode
	pip install -e .

install-dev:  ## Install with development dependencies
	pip install -e ".[dev]"

install-full:  ## Install with all optional dependencies
	pip install -e ".[full]"

clean:  ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf askpandas/__pycache__/
	rm -rf askpandas/*/__pycache__/
	rm -rf tests/__pycache__/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ --cov=askpandas --cov-report=html --cov-report=term

test-fast:  ## Run tests excluding LLM integration
	pytest tests/ -v -m "not llm"

lint:  ## Run linting checks
	flake8 askpandas/ tests/
	black --check askpandas/ tests/

format:  ## Format code with black
	black askpandas/ tests/

type-check:  ## Run type checking with mypy
	mypy askpandas/

check-all:  ## Run all code quality checks
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

build:  ## Build distribution packages
	python setup.py sdist bdist_wheel

dist:  ## Build and upload to PyPI (requires twine)
	$(MAKE) build
	twine upload dist/*

demo:  ## Run the demo script
	python demo.py

examples:  ## Run example scripts
	python examples/basic_usage.py
	python examples/multi_dataframe.py

docs:  ## Generate documentation
	python -m pydoc -w askpandas
	@echo "Documentation generated in askpandas.html"

setup-dev:  ## Set up development environment
	$(MAKE) install-dev
	$(MAKE) format
	@echo "Development environment setup complete!"

setup-ollama:  ## Install and setup Ollama (macOS/Linux)
	@echo "Installing Ollama..."
	curl -fsSL https://ollama.com/install.sh | sh
	@echo "Starting Ollama..."
	ollama serve &
	@echo "Pulling Mistral model..."
	ollama pull mistral
	@echo "Ollama setup complete! You can now run: make demo"

setup-ollama-windows:  ## Setup Ollama on Windows
	@echo "Please download and install Ollama from: https://ollama.com/download"
	@echo "Then run: ollama serve && ollama pull mistral"

ci:  ## Run CI checks (used by GitHub Actions)
	$(MAKE) install-dev
	$(MAKE) check-all
	$(MAKE) test-cov

release:  ## Prepare a new release
	@echo "Preparing release..."
	$(MAKE) clean
	$(MAKE) check-all
	$(MAKE) build
	@echo "Release packages built in dist/ directory"
	@echo "To upload to PyPI, run: make dist"

.PHONY: help install install-dev install-full clean test test-cov lint format type-check build dist demo examples
