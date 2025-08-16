#!/usr/bin/env python3
"""
Simple AskPandas Demo - Easy to Use!
No complex setup required - just run this script!
"""

import askpandas as ap
import pandas as pd
import numpy as np


def create_simple_data():
    """Create simple sample data."""
    print("📊 Creating simple sample data...")

    # Simple sales data
    data = {
        "product": ["Apple", "Banana", "Orange", "Grape", "Mango"],
        "price": [2.50, 1.00, 1.50, 3.00, 2.00],
        "quantity": [100, 200, 150, 50, 120],
        "region": ["North", "South", "North", "South", "North"],
    }

    df = pd.DataFrame(data)
    df["revenue"] = df["price"] * df["quantity"]

    print("✅ Sample data created!")
    return df


def setup_simple_llm():
    """Set up a simple LLM configuration."""
    print("\n🤖 Setting up lightweight LLM...")

    try:
        # Try to use the lightweight phi3:mini model
        llm = ap.OllamaLLM(model_name="phi3:mini")
        if llm.is_available():
            ap.set_llm(llm)
            print("✅ Lightweight LLM (phi3:mini) configured successfully!")
            return True
        else:
            print("⚠️  Ollama not running. Starting it...")
            return False
    except Exception as e:
        print(f"❌ LLM setup failed: {e}")
        return False


def demo_simple_queries():
    """Show simple, easy-to-understand queries."""
    print("\n🔍 Simple Queries Demo")
    print("=" * 40)

    # Create data
    df = create_simple_data()
    sales_df = ap.DataFrame(df)

    print("\n📋 Our simple data:")
    print(sales_df.head())

    # Simple queries that anyone can understand
    simple_queries = [
        "What is the total revenue?",
        "Which product has the highest price?",
        "Show me products from the North region",
        "What is the average price?",
        "Calculate total quantity sold",
    ]

    print("\n💡 Simple questions you can ask:")
    for i, query in enumerate(simple_queries, 1):
        print(f"   {i}. {query}")

    # Try one query to show it works
    print(f"\n❓ Let's try: {simple_queries[0]}")
    try:
        result = ap.chat(simple_queries[0], sales_df)
        print(f"🤖 AI Answer:\n{result}")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        print("💡 This usually means the LLM needs to be started.")
        print("   Run: ollama serve")


def show_manual_analysis():
    """Show manual analysis without LLM."""
    print("\n📊 Manual Analysis (No LLM Required)")
    print("=" * 40)

    df = create_simple_data()
    sales_df = ap.DataFrame(df)

    print("\n📈 Basic Statistics:")
    print(f"   Total products: {len(sales_df)}")
    print(f"   Total revenue: ${sales_df['revenue'].sum():.2f}")
    print(f"   Average price: ${sales_df['price'].mean():.2f}")

    print("\n🏆 Top performing product:")
    top_product = sales_df.sort_values("revenue", ascending=False).iloc[0]
    print(f"   {top_product['product']} - ${top_product['revenue']:.2f}")

    print("\n🌍 Revenue by region:")
    region_revenue = sales_df.groupby("region")["revenue"].sum()
    for region, revenue in region_revenue.items():
        print(f"   {region}: ${revenue:.2f}")


def main():
    """Main function - super simple!"""
    print("🚀 Simple AskPandas Demo")
    print("=" * 50)
    print("Easy to use - just run this script!")
    print("=" * 50)

    # Show manual analysis first (always works)
    show_manual_analysis()

    # Try to set up LLM
    if setup_simple_llm():
        # If LLM works, show AI queries
        demo_simple_queries()
        print("\n🎉 Full demo completed with AI!")
    else:
        # If no LLM, show manual analysis
        print("\n💡 To use AI features:")
        print("   1. Make sure Ollama is running: ollama serve")
        print("   2. Run this script again!")
        print("\n✅ Manual analysis completed successfully!")


if __name__ == "__main__":
    main()
