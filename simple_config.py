#!/usr/bin/env python3
"""
Simple AskPandas Configuration
Easy setup for different lightweight models
"""

import askpandas as ap


def setup_lightweight_ollama():
    """Set up lightweight Ollama models."""
    print("🤖 Setting up lightweight Ollama model...")

    # List of lightweight models (small and fast)
    light_models = [
        "phi3:mini",  # Very small, very fast
        "llama3.2:3b",  # Small but capable
        "mistral:7b",  # Good balance
        "gemma:2b",  # Google's lightweight model
    ]

    for model in light_models:
        try:
            print(f"   Trying {model}...")
            llm = ap.OllamaLLM(model_name=model)
            if llm.is_available():
                ap.set_llm(llm)
                print(f"✅ Successfully configured {model}!")
                return True
        except Exception as e:
            print(f"   ❌ {model} failed: {e}")
            continue

    print("❌ No lightweight models available")
    return False


def setup_huggingface_lightweight():
    """Set up lightweight Hugging Face models."""
    print("🤖 Setting up lightweight Hugging Face model...")

    try:
        # Use a very small model
        llm = ap.HuggingFaceLLM(
            model_name="microsoft/DialoGPT-small",  # Only 117M parameters
            max_length=100,
            temperature=0.7,
        )

        if llm.is_available():
            ap.set_llm(llm)
            print("✅ Successfully configured Hugging Face lightweight model!")
            return True
        else:
            print("❌ Hugging Face model not available")
            return False

    except Exception as e:
        print(f"❌ Hugging Face setup failed: {e}")
        return False


def auto_setup():
    """Automatically set up the best available lightweight model."""
    print("🚀 Auto-setting up lightweight LLM...")

    # Try Ollama first (usually easier)
    if setup_lightweight_ollama():
        return True

    # Try Hugging Face as backup
    if setup_huggingface_lightweight():
        return True

    print("❌ No lightweight models could be set up")
    print("💡 To get started:")
    print("   1. Install Ollama: brew install ollama")
    print("   2. Start Ollama: ollama serve")
    print("   3. Pull a model: ollama pull phi3:mini")

    return False


def show_current_config():
    """Show current configuration."""
    print("\n📋 Current Configuration:")
    config = ap.get_config()
    for key, value in config.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    print("⚙️  Simple AskPandas Configuration")
    print("=" * 40)

    if auto_setup():
        show_current_config()
        print("\n✅ Ready to use AskPandas!")
    else:
        print("\n⚠️  Manual setup required")
