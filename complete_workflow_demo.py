#!/usr/bin/env python3
"""
Complete AskPandas Workflow Demo
Showcases all features from the README with real outputs
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

import askpandas as ap


def create_comprehensive_sample_data():
    """Create comprehensive sample data for demonstration."""
    print("📊 Creating comprehensive sample data...")

    # Sales data
    np.random.seed(42)
    n_records = 50

    dates = [datetime.now() - timedelta(days=i) for i in range(n_records)]
    regions = ["North", "South", "East", "West"]
    products = ["Product A", "Product B", "Product C", "Product D"]
    customer_segments = ["Premium", "Standard", "Basic"]

    sales_data = []
    for i in range(n_records):
        sales_data.append(
            {
                "date": dates[i].strftime("%Y-%m-%d"),
                "region": random.choice(regions),
                "product": random.choice(products),
                "quantity": random.randint(1, 50),
                "price": round(random.uniform(10, 100), 2),
                "customer_id": random.randint(1, 25),
                "customer_segment": random.choice(customer_segments),
                "salesperson": f"Sales_{random.randint(1, 5)}",
            }
        )

    sales_df = pd.DataFrame(sales_data)
    sales_df["revenue"] = sales_df["quantity"] * sales_df["price"]

    # Customer data
    customer_data = []
    for i in range(25):
        customer_data.append(
            {
                "customer_id": i + 1,
                "name": f"Customer {i + 1}",
                "segment": random.choice(customer_segments),
                "join_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime(
                    "%Y-%m-%d"
                ),
                "total_purchases": random.randint(1, 20),
                "avg_order_value": round(random.uniform(50, 500), 2),
            }
        )

    customer_df = pd.DataFrame(customer_data)

    print(f"✅ Created {len(sales_df)} sales records and {len(customer_df)} customer records")
    return sales_df, customer_df


def demo_basic_analysis():
    """Demonstrate basic data analysis capabilities."""
    print("\n🔍 Basic Data Analysis Demo")
    print("=" * 50)

    sales_df, customer_df = create_comprehensive_sample_data()
    sales_ap = ap.DataFrame(sales_df)
    customer_ap = ap.DataFrame(customer_df)

    print("\n📊 Sample Sales Data:")
    print(sales_ap.head())

    print("\n📊 Sample Customer Data:")
    print(customer_ap.head())

    # Basic statistics
    print("\n📈 Basic Statistics:")
    print(f"   Total sales records: {len(sales_ap)}")
    print(f"   Total revenue: ${sales_ap['revenue'].sum():.2f}")
    print(f"   Average order value: ${sales_ap['revenue'].mean():.2f}")
    print(f"   Number of customers: {len(customer_ap)}")

    return sales_ap, customer_ap


def demo_ai_powered_queries():
    """Demonstrate AI-powered natural language queries."""
    print("\n🤖 AI-Powered Queries Demo")
    print("=" * 50)

    # Setup LLM
    try:
        llm = ap.OllamaLLM(model_name="phi3:mini")
        if llm.is_available():
            ap.set_llm(llm)
            print("✅ LLM configured successfully!")
        else:
            print("⚠️  LLM not available. Some demos will be limited.")
            return False
    except Exception as e:
        print(f"❌ LLM setup failed: {e}")
        return False

    sales_ap, customer_ap = demo_basic_analysis()

    # Test various query types
    queries = [
        "What is the total revenue?",
        "Show me the top 5 products by revenue",
        "Calculate average order value by region",
        "How many sales were made in each region?",
        "Show customer distribution by segment",
    ]

    print("\n💬 Testing AI-Powered Queries:")
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        try:
            if "customer" in query.lower():
                result = customer_ap.chat(query)
            else:
                result = sales_ap.chat(query)
            print(f"🤖 AI Answer:\n{result}")
        except Exception as e:
            print(f"❌ Query failed: {e}")

    return True


def demo_advanced_features():
    """Demonstrate advanced features."""
    print("\n🚀 Advanced Features Demo")
    print("=" * 50)

    sales_ap, customer_ap = demo_basic_analysis()

    # Configuration
    print("\n⚙️ Configuration Demo:")
    ap.set_config(verbose=True, plot_style="seaborn", output_dir="demo_output")
    config = ap.get_config()
    print("   Current configuration:")
    for key, value in config.items():
        print(f"     {key}: {value}")

    # Query analysis
    print("\n🔍 Query Analysis Demo:")
    test_query = "Show me sales trends by region"
    analysis = ap.analyze_query(test_query)
    print(f"   Query: {test_query}")
    print(f"   Analysis: {analysis}")

    # Available models
    print("\n🤖 Available Models:")
    models = ap.get_available_models()
    for provider, model_list in models.items():
        print(f"   {provider}: {', '.join(model_list[:3])}...")

    return True


def demo_data_quality_and_cleaning():
    """Demonstrate data quality and cleaning features."""
    print("\n🧹 Data Quality & Cleaning Demo")
    print("=" * 50)

    # Create messy data
    messy_data = {
        "First Name": ["Alice", "Bob", "Charlie", "Diana"],
        "Last Name": ["Smith", "Jones", "Brown", "Wilson"],
        "Age (Years)": [25, 30, 35, 28],
        "Salary ($)": [50000, 60000, 70000, 55000],
        "Department": ["IT", "HR", "IT", "Finance"],
    }

    messy_df = pd.DataFrame(messy_data)
    messy_ap = ap.DataFrame(messy_df)

    print("📊 Messy Data (Before Cleaning):")
    print(f"   Columns: {list(messy_ap.df.columns)}")
    print(messy_ap.head())

    # Clean columns
    print("\n🧹 Cleaning Column Names...")
    cleaned_ap = messy_ap.clean_columns()
    print("📊 Cleaned Data (After Cleaning):")
    print(f"   Columns: {list(cleaned_ap.df.columns)}")
    print(cleaned_ap.head())

    # Data summary
    print("\n📈 Data Summary Statistics:")
    summary = cleaned_ap.get_summary_stats()
    print(f"   Shape: {summary['shape']}")
    print(f"   Memory usage: {summary['total_memory_mb']:.2f} MB")
    print(f"   Duplicate rows: {summary['duplicate_rows']}")
    print(f"   Numeric columns: {summary['numeric_columns']}")

    return True


def demo_visualization_setup():
    """Demonstrate visualization setup."""
    print("\n🎨 Visualization Setup Demo")
    print("=" * 50)

    # Test plot style setting
    print("🎨 Setting plot style to 'ggplot':")
    ap.set_config(plot_style="ggplot", verbose=True)

    # Test available visualization functions
    print("\n📊 Available Visualization Functions:")
    viz_functions = [
        "create_bar_chart",
        "create_line_chart",
        "create_scatter_plot",
        "create_histogram",
        "create_correlation_heatmap",
        "create_box_plot",
    ]

    for func in viz_functions:
        print(f"   ✅ {func}")

    print("\n🎨 Visualization setup completed!")
    return True


def main():
    """Main demonstration function."""
    print("🚀 AskPandas Complete Workflow Demonstration")
    print("=" * 60)
    print("This demo showcases all features from the README")
    print("=" * 60)

    try:
        # Run all demos
        demo_basic_analysis()
        demo_ai_powered_queries()
        demo_advanced_features()
        demo_data_quality_and_cleaning()
        demo_visualization_setup()

        print("\n🎉 All demonstrations completed successfully!")
        print("\n📁 Generated files:")
        print("   - demo_output/ (if visualizations were created)")

        print("\n💡 Next Steps:")
        print("   1. Try your own CSV files")
        print("   2. Experiment with different queries")
        print("   3. Customize configurations")
        print("   4. Explore advanced features")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
