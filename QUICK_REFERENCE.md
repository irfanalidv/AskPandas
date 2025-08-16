# 🚀 AskPandas Quick Reference Card

## ⚡ **5-Minute Setup**

```bash
# 1. Install AskPandas
pip install askpandas

# 2. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 3. Pull model
ollama pull phi3:mini

# 4. Start Ollama
ollama serve
```

## 🐍 **Basic Usage**

```python
import askpandas as ap

# Setup AI
llm = ap.OllamaLLM(model_name="phi3:mini")
ap.set_llm(llm)

# Load data
df = ap.DataFrame("your_file.csv")

# Ask questions!
result = df.chat("What is the total revenue?")
```

## 💬 **Query Examples by Category**

### 📊 **Basic Analysis**

```python
df.chat("What is the average price?")
df.chat("Show me the top 5 customers by revenue")
df.chat("How many sales in each region?")
df.chat("Calculate total revenue by month")
```

### 🎨 **Visualizations**

```python
df.chat("Create a bar chart of sales by region")
df.chat("Plot revenue trends over time")
df.chat("Show correlation between price and quantity")
df.chat("Display distribution of customer ages")
```

### 🔍 **Data Quality**

```python
df.chat("Check for missing values and duplicates")
df.chat("Identify outliers in numeric columns")
df.chat("Clean column names and standardize formats")
df.chat("Validate data types and suggest improvements")
```

### 🌐 **Multi-Dataset**

```python
customers = ap.DataFrame("customers.csv")
orders = ap.DataFrame("orders.csv")

ap.chat("""
    Customer analysis:
    1. Join customers with orders
    2. Calculate lifetime value
    3. Show purchase patterns
    4. Identify high-value customers
""", customers, orders)
```

## 🎯 **Pro Tips for Best Results**

### ✅ **Good Query Examples**

```python
# Specific and clear
df.chat("Calculate total revenue by month for 2024, excluding returns")

# Step-by-step analysis
df.chat("""
    1. Filter data for Q4 2024
    2. Group by product category
    3. Calculate sum of revenue
    4. Sort by revenue descending
    5. Show top 10 results
""")

# Include context
df.chat("Show customer retention rate, considering customers who made purchases in both 2023 and 2024")
```

### ❌ **Avoid These**

```python
# Too vague
df.chat("Analyze this data")

# Too complex in one query
df.chat("Do everything possible with this data and create a comprehensive report with all insights and visualizations")
```

## 🔧 **Configuration**

```python
# Set preferences
ap.set_config(
    verbose=True,                    # See what's happening
    plot_style="seaborn",           # Beautiful charts
    output_dir="my_analysis",       # Save results here
    max_execution_time=120          # Allow longer analysis
)
```

## 🚨 **Troubleshooting**

| Problem             | Solution                                |
| ------------------- | --------------------------------------- |
| "No LLM configured" | Run `ollama serve`                      |
| Slow responses      | Use `phi3:mini` model                   |
| Installation fails  | Update pip: `pip install --upgrade pip` |
| Memory issues       | Close other apps, use smaller model     |

## 📱 **Platform Commands**

### **macOS/Linux**

```bash
ollama serve
ollama pull phi3:mini
```

### **Windows**

```bash
# Download from https://ollama.com/download
ollama serve
ollama pull phi3:mini
```

## 🎉 **Success Patterns**

### **Data Exploration**

1. Start with basic questions
2. Ask for visualizations
3. Request data quality checks
4. Explore relationships between variables

### **Business Analysis**

1. Define clear objectives
2. Ask for specific metrics
3. Request trend analysis
4. Get actionable insights

### **Research**

1. Descriptive statistics first
2. Correlation analysis
3. Outlier detection
4. Statistical testing

## 📞 **Need Help?**

- **Demo**: `python simple_demo.py`
- **Setup**: `python simple_config.py`
- **Issues**: [GitHub Issues](https://github.com/irfanalidv/AskPandas/issues)
- **Email**: irfanali29@hotmail.com

---

**🚀 Ready to analyze data? Just ask!**
