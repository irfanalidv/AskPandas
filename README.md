<div align="center">

# AskPandas

**Ask questions about pandas DataFrames and CSV files in plain English. An LLM writes the pandas code, AskPandas runs it in a restricted sandbox and returns the answer.**

[![PyPI version](https://img.shields.io/pypi/v/askpandas.svg)](https://pypi.org/project/askpandas/)
[![Python versions](https://img.shields.io/pypi/pyversions/askpandas.svg)](https://pypi.org/project/askpandas/)
[![Tests](https://github.com/irfanalidv/AskPandas/actions/workflows/tests.yml/badge.svg)](https://github.com/irfanalidv/AskPandas/actions/workflows/tests.yml)
[![Downloads](https://static.pepy.tech/badge/askpandas)](https://pepy.tech/project/askpandas)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/irfanalidv/AskPandas/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

AskPandas is an open-source Python library that lets you query and transform CSV data using natural language. Run it **fully local and free** with open-source models via [Ollama](https://ollama.com) (no API keys, no cloud), or plug in **OpenAI, Mistral, Hugging Face Inference Providers or any OpenAI-compatible API**.

## ✨ **Why AskPandas?**

- **Plain-English analytics**: `df.chat("total revenue by region, sorted")` returns the printed result of real pandas code.
- **Local or hosted LLMs**: `OllamaLLM` for local models, `OpenAICompatibleLLM` for OpenAI/Mistral/vLLM/LM Studio/Groq/..., `HuggingFaceLLM` for HF Inference Providers.
- **Multi-DataFrame questions**: pass several DataFrames (`df0`, `df1`, ...) and ask for joins and comparisons.
- **Restricted execution**: generated code runs without imports, file access or dunder attribute access, with a whitelisted set of builtins.
- **Batteries included**: chart helpers, data-quality, statistics and performance utilities, query categorization and validation.
- **Lightweight**: depends only on pandas, numpy, matplotlib, seaborn, scipy, psutil and requests (no torch/transformers).

## ⚙️ **How it works**

1. AskPandas builds a prompt with your question plus a summary of each DataFrame (columns, dtypes, null counts, sample rows).
2. The LLM replies with pandas code; AskPandas extracts the code block and validates it.
3. The code runs in a restricted namespace where your data is available as `df0`, `df1`, ... and its printed output is returned. Invalid replies are retried with correction hints, LLM errors are retried with backoff.

> **Safety note:** the sandbox blocks the common escape routes (imports, `open`, dunder access, `eval`/`exec`), but it is a best-effort guard, not a security boundary. Only run AskPandas with models and data you trust, and do not expose it to untrusted users.

## 🚀 **Quick Start (5 minutes!)**

### 1. **Install AskPandas**

```bash
pip install askpandas
```

### 2. **Install Ollama (one command)**

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download
```

### 3. **Pull a lightweight model**

```bash
ollama pull phi3:mini    # Very small, very fast
```

### 4. **Start Ollama**

```bash
ollama serve
```

### 5. **Start analyzing data!**

Prefer a hosted model? See [Using hosted LLMs](#-using-hosted-llms-openai-mistral-hugging-face) below.

```python
import askpandas as ap

# Set up AI
llm = ap.OllamaLLM(model_name="phi3:mini")
ap.set_llm(llm)

# Load your data
df = ap.DataFrame("your_data.csv")

# Ask questions in plain English!
result = df.chat("What is the total revenue?")
print(result)
```

### 🚀 **See It In Action!**

```python
import askpandas as ap
import pandas as pd

# Create sample data
data = {
    'product': ['Apple', 'Banana', 'Orange'],
    'price': [2.50, 1.00, 1.50],
    'quantity': [100, 200, 150]
}
df = pd.DataFrame(data)
df['revenue'] = df['price'] * df['quantity']

# Create AskPandas DataFrame
sales_df = ap.DataFrame(df)

# AI-powered analysis
result = sales_df.chat("What is the total revenue?")
print(result)
# Output (exact wording depends on the model): Total Revenue: $675.00

# More complex queries
result = sales_df.chat("Show me the top 3 products by revenue")
# Output: Product analysis with rankings

result = sales_df.chat("Calculate average price by product")
# Output: Average Price: $1.67
```

## 🎯 **What Can You Do? (Everything!)**

### 📊 **Data Analysis - Just Ask!**

```python
# Basic questions
df.chat("What is the average price?")
# Output: Average Price: $1.67

df.chat("Show me the top 5 customers by revenue")
# Output: Customer rankings with revenue amounts

df.chat("How many sales were made in each region?")
# Output: Regional sales breakdown

# Complex analysis
df.chat("""
    Analyze our sales performance:
    1. Calculate total revenue by month
    2. Show the trend over time
    3. Identify the best performing products
    4. Create a visualization
""")
# Output: Comprehensive analysis with insights
```

### 🎨 **Visualizations**

```python
# Ask for a chart; the generated code saves it with save_plot() to askpandas_plots/
df.chat("Create a bar chart of sales by region")
df.chat("Plot revenue trends over time")
df.chat("Show correlation between price and quantity")
df.chat("Display distribution of customer ages")
```

### 🔍 **Data Quality & Cleaning**

```python
# Automatic data assessment
df.chat("Check for missing values and duplicates")
df.chat("Identify outliers in numeric columns")
df.chat("Clean column names and standardize formats")
df.chat("Validate data types and suggest improvements")
```

### 🌐 **Multi-Dataset Analysis**

```python
# Work with multiple files
customers = ap.DataFrame("customers.csv")
orders = ap.DataFrame("orders.csv")
products = ap.DataFrame("products.csv")

# Cross-dataset insights
ap.chat("""
    Customer analysis:
    1. Join customers with their orders
    2. Calculate lifetime value by segment
    3. Show purchase patterns
    4. Identify high-value customers
""", customers, orders, products)
```

## 💡 **Real-World Examples**

### 📈 **Sales Analysis**

```python
import askpandas as ap

# Load sales data
sales = ap.DataFrame("sales_data.csv")

# Comprehensive sales report
sales.chat("What is our total revenue?")
# Output: Total Revenue: $78,586.11

sales.chat("Show me the top 3 products by revenue")
# Output: Product rankings with revenue amounts

sales.chat("Calculate average order value by region")
# Output: Regional performance metrics

sales.chat("How many sales were made in each region?")
# Output: Regional sales breakdown
```

### 👥 **Customer Analytics**

```python
# Customer behavior analysis
customers = ap.DataFrame("customers.csv")
transactions = ap.DataFrame("transactions.csv")

ap.chat("""
    Customer behavior insights:
    1. Customer lifetime value analysis
    2. Purchase frequency patterns
    3. Churn prediction factors
    4. Customer satisfaction metrics
    5. Personalized marketing recommendations
""", customers, transactions)
```

### 📊 **Financial Analysis**

```python
# Financial data processing
financial = ap.DataFrame("financial_data.csv")

financial.chat("""
    Financial performance review:
    1. Profit and loss analysis
    2. Cash flow trends
    3. Expense categorization
    4. Budget vs actual comparison
    5. Financial ratios and KPIs
    6. Risk assessment and recommendations
""")
```

### 🔬 **Research & Academic**

```python
# Research data analysis
research = ap.DataFrame("research_data.csv")

research.chat("""
    Statistical analysis:
    1. Descriptive statistics for all variables
    2. Correlation analysis between key factors
    3. Hypothesis testing results
    4. Outlier detection and treatment
    5. Data distribution visualizations
    6. Statistical significance testing
""")
```

## ☁️ **Using hosted LLMs (OpenAI, Mistral, Hugging Face)**

```python
import askpandas as ap

# OpenAI (reads OPENAI_API_KEY)
ap.set_llm(ap.OpenAICompatibleLLM.openai("gpt-4o-mini"))

# Mistral (reads MISTRAL_API_KEY)
ap.set_llm(ap.OpenAICompatibleLLM.mistral("mistral-small-latest"))

# Hugging Face Inference Providers (reads HF_TOKEN)
ap.set_llm(ap.HuggingFaceLLM("Qwen/Qwen2.5-Coder-7B-Instruct"))

# Any OpenAI-compatible server (vLLM, LM Studio, Ollama's /v1, Groq, Together, ...)
ap.set_llm(ap.OpenAICompatibleLLM("my-model", base_url="http://localhost:8000/v1", api_key="..."))

df = ap.DataFrame("demo_sales.csv")
print(df.chat("What is the total revenue by region? Sort descending."))
```

Verified output with `gpt-4o-mini` on the bundled `demo_sales.csv` (matches a direct pandas `groupby`):

```
Total Revenue by Region:
region
South    50557.76
North    40075.88
East     30787.38
West     26978.72
Name: revenue, dtype: float64
```

### **Environment variables**

| Variable | Used by |
| --- | --- |
| `OPENAI_API_KEY` | `OpenAICompatibleLLM.openai()` / `OpenAICompatibleLLM(...)` default |
| `MISTRAL_API_KEY` | `OpenAICompatibleLLM.mistral()` |
| `HF_TOKEN` (or `HF_API_KEY`) | `HuggingFaceLLM` |

Ollama needs no key; point `OllamaLLM(host=...)` at a remote server if it is not on `localhost:11434`.

## 🧩 **API Overview**

| Object | What it does |
| --- | --- |
| `ap.DataFrame(data)` / `AskDataFrame` | Wrap a pandas DataFrame, dict, list of records, or a `.csv`/`.json` path. Adds `.chat()`, `.info()`, `.get_summary_stats()`, `.get_column_info()`, `.clean_columns()`; other attributes pass through to pandas. |
| `ap.set_llm(llm)` / `ap.get_llm()` | Set/get the global LLM used by `.chat()` and `ap.chat()`. |
| `ap.chat(query, *dfs)` | Ask a question across several DataFrames (`df0`, `df1`, ...). |
| `OllamaLLM`, `OpenAICompatibleLLM`, `HuggingFaceLLM`, `BaseLLM` | LLM clients; subclass `BaseLLM` (implement `generate` and `is_available`) to add your own. |
| `AskPandasEngine(llm)` | The engine behind `.chat()`; keeps execution history (`get_execution_history()`, `get_engine_stats()`, `export_execution_history()`). |
| `ap.analyze_query`, `ap.validate_query`, `ap.get_query_examples` | Query categorization, validation against columns, example prompts. |
| `ap.set_config(...)` / `ap.get_config()` | Global settings (verbosity, plot style, output directory, ...). |
| `askpandas.visualization.charts` | `create_bar_chart`, `create_line_chart`, `create_scatter_plot`, `create_histogram`, `create_correlation_heatmap`, `create_box_plot`, `save_plot`. |
| `askpandas.utils` | `data_quality`, `statistical` and `performance` helper modules. |

## 🛠️ **Advanced Features**

### 🔧 **Custom Configuration**

```python
import askpandas as ap

# Set your preferences
ap.set_config(
    verbose=True,                    # See what's happening
    plot_style="seaborn",           # Beautiful charts
    output_dir="my_analysis",       # Save results here
    max_execution_time=120,         # Allow longer analysis
    enable_history=True             # Track all queries
)
```

### 🎨 **Custom Visualizations**

```python
# Create custom charts
from askpandas.visualization.charts import create_bar_chart, save_plot

# Custom bar chart
fig = create_bar_chart(
    df.df,
    x_col="category",
    y_col="value",
    title="My Custom Chart",
    figsize=(12, 8)
)

# Save with high quality
save_plot(fig, "custom_chart.png", dpi=300)
```

### 🔍 **Query Intelligence**

```python
# Get help with your queries
query = "Show me sales trends"
analysis = ap.analyze_query(query)
print(f"Query type: {analysis['primary_category']}")

# Get suggestions
suggestions = ap.get_query_examples('visualization')
print("Try these:", suggestions[:3])

# Validate your query
validation = ap.validate_query(query, df.columns)
if validation['is_valid']:
    print("✅ Query is valid!")
```

## 🚀 **Performance Tips for Best Results**

### 💪 **Optimize Your Queries**

```python
# ✅ Good - Specific and clear
df.chat("Calculate total revenue by month for 2024, excluding returns")

# ❌ Avoid - Too vague
df.chat("Analyze this data")

# ✅ Good - Step-by-step analysis
df.chat("""
    1. Filter data for Q4 2024
    2. Group by product category
    3. Calculate sum of revenue
    4. Sort by revenue descending
    5. Show top 10 results
""")

# ✅ Good - Include context
df.chat("Show customer retention rate, considering customers who made purchases in both 2023 and 2024")
```

### 🎯 **Choose the Right Model**

```python
# For speed and basic analysis
llm = ap.OllamaLLM(model_name="phi3:mini")      # Fastest

# For better quality and complex queries
llm = ap.OllamaLLM(model_name="mistral:7b")     # Balanced

# For best results (slower)
llm = ap.OllamaLLM(model_name="llama3.2:13b")   # Highest quality
```

### 📊 **Data Preparation Tips**

```python
# Clean your data first
df = ap.DataFrame("messy_data.csv")

# Ask AskPandas to help clean it
df.chat("""
    Help me clean this data:
    1. Identify and handle missing values
    2. Remove duplicates
    3. Fix data type issues
    4. Standardize column names
    5. Show me what was cleaned
""")

# Then analyze the clean data
df.chat("Now analyze the cleaned data for insights")
```

## 🔧 **Installation Options**

### **Basic Installation**

```bash
pip install askpandas
```

### **Full Installation (Recommended)**

```bash
pip install "askpandas[full]"
```

### **Development Installation**

```bash
git clone https://github.com/irfanalidv/AskPandas
cd AskPandas
pip install -e ".[dev]"
```

## 📱 **Platform Support**

- ✅ **macOS, Linux and Windows** (pure Python; Python 3.10-3.13)
- ✅ **Notebooks and cloud environments** such as Google Colab (use a hosted LLM or a reachable Ollama server)

## 🆘 **Troubleshooting**

### **Common Issues & Solutions**

**"No LLM configured" error?**

```bash
# Make sure Ollama is running
ollama serve

# Check if model is downloaded
ollama list
```

**Slow responses?**

```bash
# Try a smaller model
ollama pull phi3:mini

# Close other applications to free memory
```

**Installation issues?**

```bash
# Update pip
pip install --upgrade pip

# AskPandas requires Python 3.10+
python3.12 -m pip install askpandas
```

## 📚 **Learning Resources**

### **Interactive Examples**

```bash
# Run the interactive demo
python simple_demo.py

# Try the configuration setup
python simple_config.py
```

### **Sample Datasets**

- `fake_sample.csv` - Small sample for testing
- `comprehensive_sample.csv` - Larger dataset for practice
- Create your own CSV files and start analyzing!

## 🚀 **Roadmap**

### **Next**

- [ ] Jupyter notebook integration
- [ ] More visualization options (Plotly, Bokeh)
- [ ] SQL query generation
- [ ] Data pipeline automation

### **Version 1.0.0 (Future)**

- [ ] Enterprise features
- [ ] Advanced ML integration
- [ ] Real-time data streaming
- [ ] Community plugins

## 🤝 **Get Help & Contribute**

- **📖 Documentation**: this README and the [examples](https://github.com/irfanalidv/AskPandas/tree/main/examples)
- **🛠️ Contributing**: see [CONTRIBUTING.md](https://github.com/irfanalidv/AskPandas/blob/main/CONTRIBUTING.md)
- **📝 Changelog**: [CHANGELOG.md](https://github.com/irfanalidv/AskPandas/blob/main/CHANGELOG.md)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/irfanalidv/AskPandas/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/irfanalidv/AskPandas/discussions)
- **⭐ Star**: [GitHub Repository](https://github.com/irfanalidv/AskPandas)

## 📄 **License**

MIT License - see [LICENSE](https://github.com/irfanalidv/AskPandas/blob/main/LICENSE). Use freely for personal and commercial projects!

## 🙏 **Acknowledgments**

- **Ollama Team** - Making local AI accessible
- **HuggingFace** - Open-source AI models
- **Pandas Community** - Amazing data tools
- **Open Source Contributors** - Building the future together

## 🎯 **Complete Working Demonstration**

Want to see everything in action? Run our comprehensive demo:

```bash
# Clone the repository
git clone https://github.com/irfanalidv/AskPandas.git
cd AskPandas

# Run the complete demonstration
python final_working_demo.py
```

This demo showcases:

- ✅ **DataFrame Creation & Analysis** - Real data processing
- ✅ **Data Quality & Cleaning** - Automatic column standardization
- ✅ **AI-Powered Queries** - Natural language analysis
- ✅ **Multi-Dataset Analysis** - Joining and complex queries
- ✅ **Configuration Management** - Customizable settings
- ✅ **Query Intelligence** - Automatic query categorization

### **🚀 Quick Test**

```python
import askpandas as ap
import pandas as pd

# Create test data
data = {'name': ['Alice', 'Bob'], 'age': [25, 30], 'salary': [50000, 60000]}
df = pd.DataFrame(data)
ap_df = ap.DataFrame(df)

# Test basic methods
print(f"Shape: {ap_df.shape()}")  # Output: Shape: (2, 3)
print(f"Columns: {ap_df.columns()}")  # Output: Columns: ['name', 'age', 'salary']

# Get comprehensive info
print(ap_df.info())  # Output: Detailed DataFrame information

# Statistical description
print(ap_df.describe())  # Output: Statistical summary
```

---

**🚀 Ready to transform your data analysis? Install AskPandas today!**

```bash
pip install askpandas
```

**Made with ❤️ by Md Irfan Ali**
