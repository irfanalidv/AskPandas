#!/usr/bin/env python3
"""
AskPandas Demo Script
Showcases the main features of the AskPandas library
"""

import askpandas as ap
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def create_sample_data():
    """Create sample data for demonstration."""
    print("📊 Creating sample data...")

    # Create sales data
    np.random.seed(42)
    n_records = 100

    dates = [datetime.now() - timedelta(days=i) for i in range(n_records)]
    regions = ["North", "South", "East", "West"]
    products = ["Product A", "Product B", "Product C", "Product D"]

    sales_data = []
    for i in range(n_records):
        sales_data.append(
            {
                "date": dates[i].strftime("%Y-%m-%d"),
                "region": random.choice(regions),
                "product": random.choice(products),
                "quantity": random.randint(1, 50),
                "price": round(random.uniform(10, 100), 2),
                "customer_id": random.randint(1, 50),
            }
        )

    sales_df = pd.DataFrame(sales_data)
    sales_df["revenue"] = sales_df["quantity"] * sales_df["price"]
    sales_df.to_csv("demo_sales.csv", index=False)

    # Create customer data
    customer_data = []
    for i in range(50):
        customer_data.append(
            {
                "customer_id": i + 1,
                "name": f"Customer {i+1}",
                "segment": random.choice(["Premium", "Standard", "Basic"]),
                "join_date": (
                    datetime.now() - timedelta(days=random.randint(30, 365))
                ).strftime("%Y-%m-%d"),
                "total_purchases": random.randint(1, 20),
            }
        )

    customer_df = pd.DataFrame(customer_data)
    customer_df.to_csv("demo_customers.csv", index=False)

    print(
        f"✅ Created {len(sales_df)} sales records and {len(customer_df)} customer records"
    )
    return sales_df, customer_df


def setup_llm():
    """Set up the LLM for AskPandas."""
    print("\n🤖 Setting up LLM...")

    try:
        # Try Ollama first
        llm = ap.OllamaLLM(model_name="mistral")
        if llm.is_available():
            ap.set_llm(llm)
            print("✅ Ollama LLM configured successfully (Mistral model)")
            return True
        else:
            print(
                "⚠️  Ollama is not running. Please start Ollama and pull the mistral model."
            )
            print("   Run: ollama serve && ollama pull mistral")
            return False
    except Exception as e:
        print(f"❌ Failed to configure Ollama LLM: {e}")
        print("   Please ensure Ollama is installed and running")
        return False


def demo_basic_queries():
    """Demonstrate basic query functionality."""
    print("\n🔍 Basic Queries Demo")
    print("=" * 50)

    # Load data
    sales = ap.DataFrame("demo_sales.csv")
    customers = ap.DataFrame("demo_customers.csv")

    # Basic info
    print("\n📋 Sales Data Info:")
    print(sales.info())

    print("\n📋 Customer Data Info:")
    print(customers.info())

    # Simple queries
    queries = [
        "What is the total revenue?",
        "Show the top 5 regions by total sales",
        "What is the average order value?",
        "How many customers do we have in each segment?",
    ]

    for query in queries:
        print(f"\n❓ Query: {query}")
        try:
            result = ap.chat(query, sales, customers)
            print(f"📊 Result:\n{result}")
        except Exception as e:
            print(f"❌ Error: {e}")


def demo_visualizations():
    """Demonstrate visualization capabilities."""
    print("\n📈 Visualizations Demo")
    print("=" * 50)

    sales = ap.DataFrame("demo_sales.csv")

    viz_queries = [
        "Create a bar chart showing total revenue by region",
        "Plot a line chart of daily sales over time",
        "Show a scatter plot of quantity vs price",
        "Create a histogram of order quantities",
    ]

    for query in viz_queries:
        print(f"\n🎨 Query: {query}")
        try:
            result = ap.chat(query, sales)
            print(f"📊 Result:\n{result}")
        except Exception as e:
            print(f"❌ Error: {e}")


def demo_advanced_analysis():
    """Demonstrate advanced analysis features."""
    print("\n🧠 Advanced Analysis Demo")
    print("=" * 50)

    sales = ap.DataFrame("demo_sales.csv")
    customers = ap.DataFrame("demo_customers.csv")

    advanced_queries = [
        "What is the correlation between customer segment and order value?",
        "Show the top 10 customers by total revenue with their segments",
        "Analyze sales performance by product and region",
        "Find any outliers in the price data",
    ]

    for query in advanced_queries:
        print(f"\n🔬 Query: {query}")
        try:
            result = ap.chat(query, sales, customers)
            print(f"📊 Result:\n{result}")
        except Exception as e:
            print(f"❌ Error: {e}")


def demo_query_analysis():
    """Demonstrate query analysis and validation features."""
    print("\n🔍 Query Analysis Demo")
    print("=" * 50)

    # Analyze different types of queries
    test_queries = [
        "Show me a bar chart of sales by region",
        "What is the total revenue by customer segment?",
        "Filter customers with more than 10 purchases",
        "Sort products by average price descending",
    ]

    for query in test_queries:
        print(f"\n🔍 Analyzing query: {query}")

        # Analyze query
        analysis = ap.analyze_query(query)
        print(f"   Categories: {list(analysis['categories'].keys())}")
        print(f"   Primary: {analysis['primary_category']}")

        # Get suggestions
        suggestions = ap.get_query_examples(analysis["primary_category"])
        if suggestions:
            print(f"   💡 Example: {suggestions[0]}")


def demo_configuration():
    """Demonstrate configuration management."""
    print("\n⚙️  Configuration Demo")
    print("=" * 50)

    # Show current config
    print("📋 Current Configuration:")
    config = ap.get_config()
    for key, value in config.items():
        print(f"   {key}: {value}")

    # Update config
    print("\n🔄 Updating configuration...")
    ap.set_config(verbose=True, plot_style="seaborn")

    print("📋 Updated Configuration:")
    new_config = ap.get_config()
    for key, value in new_config.items():
        print(f"   {key}: {value}")


def demo_utilities():
    """Demonstrate utility functions."""
    print("\n🛠️  Utilities Demo")
    print("=" * 50)

    sales = ap.DataFrame("demo_sales.csv")

    # Data summary
    print("📊 Data Summary:")
    summary = sales.get_summary_stats()
    print(f"   Shape: {summary['shape']}")
    print(f"   Memory usage: {summary['total_memory_mb']:.2f} MB")
    print(f"   Duplicate rows: {summary['duplicate_rows']}")

    # Column info
    print("\n📋 Column Information:")
    col_info = sales.get_column_info("revenue")
    print(f"   Revenue column:")
    print(f"     Type: {col_info['dtype']}")
    print(f"     Min: {col_info['min']:.2f}")
    print(f"     Max: {col_info['max']:.2f}")
    print(f"     Mean: {col_info['mean']:.2f}")

    # Clean columns
    print("\n🧹 Column Cleaning:")
    sales_with_special_chars = ap.DataFrame(
        {
            "First Name": ["Alice", "Bob"],
            "Last Name": ["Smith", "Jones"],
            "Age (Years)": [25, 30],
        }
    )

    print("   Before cleaning:")
    print(f"     Columns: {list(sales_with_special_chars.df.columns)}")

    cleaned = sales_with_special_chars.clean_columns()
    print("   After cleaning:")
    print(f"     Columns: {list(cleaned.df.columns)}")


def main():
    """Main demo function."""
    print("🚀 AskPandas Demo")
    print("=" * 60)
    print("This demo showcases the main features of AskPandas")
    print("=" * 60)

    # Create sample data
    sales_df, customer_df = create_sample_data()

    # Setup LLM
    if not setup_llm():
        print("\n⚠️  LLM not available. Some demos will be limited.")
        print("   Please set up Ollama to see full functionality.")
        return

    # Run demos
    try:
        demo_basic_queries()
        demo_visualizations()
        demo_advanced_analysis()
        demo_query_analysis()
        demo_configuration()
        demo_utilities()

        print("\n🎉 Demo completed successfully!")
        print("\n📁 Generated files:")
        print("   - demo_sales.csv")
        print("   - demo_customers.csv")
        print("   - askpandas_plots/ (if visualizations were created)")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
