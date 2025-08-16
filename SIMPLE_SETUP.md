# 🚀 Simple AskPandas Setup Guide

## Quick Start (5 minutes!)

### Option 1: Ollama (Recommended - Easiest)

1. **Install Ollama** (one command):

   ```bash
   brew install ollama
   ```

2. **Start Ollama**:

   ```bash
   ollama serve
   ```

3. **Pull a lightweight model**:

   ```bash
   ollama pull phi3:mini    # Very small, very fast
   ```

4. **Run the simple demo**:
   ```bash
   python simple_demo.py
   ```

### Option 2: Hugging Face (Alternative)

1. **Install requirements**:

   ```bash
   pip install transformers torch
   ```

2. **Run with Hugging Face**:
   ```bash
   python simple_config.py
   ```

## 🎯 What You Get

- **Lightweight models** that run on any computer
- **Simple setup** - no complex configuration
- **Fast responses** - models are optimized for speed
- **Easy to use** - just ask questions in plain English

## 📊 Example Usage

```python
import askpandas as ap

# Load your data
df = ap.DataFrame("your_data.csv")

# Ask questions naturally
result = ap.chat("What is the total revenue?", df)
print(result)
```

## 🔧 Available Lightweight Models

| Model         | Size | Speed    | Quality  |
| ------------- | ---- | -------- | -------- |
| `phi3:mini`   | 3.8B | ⚡⚡⚡   | ⭐⭐     |
| `llama3.2:3b` | 3B   | ⚡⚡⚡   | ⭐⭐⭐   |
| `gemma:2b`    | 2B   | ⚡⚡⚡⚡ | ⭐⭐     |
| `mistral:7b`  | 7B   | ⚡⚡     | ⭐⭐⭐⭐ |

## 💡 Pro Tips

- **Start with `phi3:mini`** - it's the fastest and easiest
- **Keep Ollama running** in the background
- **Use simple questions** for best results
- **Check `simple_demo.py`** for examples

## 🆘 Troubleshooting

**"No LLM configured" error?**

- Make sure Ollama is running: `ollama serve`
- Check if model is pulled: `ollama list`

**Slow responses?**

- Try a smaller model like `phi3:mini`
- Close other applications to free up memory

**Installation issues?**

- Make sure you have Python 3.8+
- Try: `pip install --upgrade askpandas`

## 🎉 You're Ready!

Run `python simple_demo.py` and start asking questions about your data!
