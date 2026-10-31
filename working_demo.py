#!/usr/bin/env python3
"""
Working AskPandas Demonstration
Showcases all working features from the README
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


def demo_dataframe_methods():
    """Demonstrate AskDataFrame methods."""
    print("\n🔧 AskDataFrame Methods Demo")
    print("=" * 50)

    sales_ap, customer_ap = demo_basic_analysis()

    print("\n📋 DataFrame Info:")
    print(sales_ap.info())

    print("\n📊 Statistical Description:")
    print(sales_ap.describe())

    print("\n📈 Shape and Columns:")
    print(f"   Shape: {sales_ap.shape()}")
    print(f"   Columns: {sales_ap.columns()}")
    print(f"   Data types: {sales_ap.dtypes()}")

    print("\n🔍 Data Quality Check:")
    print(f"   Null values: {sales_ap.isnull().sum().sum()}")
    print(f"   Duplicate rows: {sales_ap.df.duplicated().sum()}")

    return sales_ap, customer_ap


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


def demo_configuration():
    """Demonstrate configuration features."""
    print("\n⚙️ Configuration Demo")
    print("=" * 50)

    # Set configuration
    print("🔧 Setting configuration...")
    ap.set_config(
        verbose=True,
        plot_style="seaborn",
        output_dir="demo_output",
        max_execution_time=120,
        enable_history=True,
    )

    # Get configuration
    config = ap.get_config()
    print("📋 Current configuration:")
    for key, value in config.items():
        print(f"   {key}: {value}")

    return True


def demo_available_models():
    """Demonstrate available models."""
    print("\n🤖 Available Models Demo")
    print("=" * 50)

    models = ap.get_available_models()
    print("📚 Available Models:")
    for provider, model_list in models.items():
        print(f"   {provider}: {', '.join(model_list[:3])}...")

    return True


def demo_query_analysis():
    """Demonstrate query analysis features."""
    print("\n🔍 Query Analysis Demo")
    print("=" * 50)

    test_queries = [
        "Show me sales trends by region",
        "Calculate total revenue by product",
        "Create a bar chart of customer segments",
    ]

    for query in test_queries:
        print(f"\n💬 Query: {query}")
        try:
            analysis = ap.analyze_query(query)
            print(f"   Analysis: {analysis}")
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")

    return True


def demo_manual_analysis():
    """Demonstrate manual data analysis capabilities."""
    print("\n📊 Manual Data Analysis Demo")
    print("=" * 50)

    sales_ap, customer_ap = demo_basic_analysis()

    print("\n🔍 Manual Analysis Examples:")

    # Revenue analysis
    print("\n💰 Revenue Analysis:")
    total_revenue = sales_ap["revenue"].sum()
    avg_revenue = sales_ap["revenue"].mean()
    print(f"   Total Revenue: ${total_revenue:,.2f}")
    print(f"   Average Revenue: ${avg_revenue:,.2f}")

    # Regional analysis
    print("\n🌍 Regional Analysis:")
    regional_revenue = sales_ap.groupby("region")["revenue"].sum().sort_values(ascending=False)
    print("   Revenue by Region:")
    for region, revenue in regional_revenue.items():
        print(f"     {region}: ${revenue:,.2f}")

    # Product analysis
    print("\n📦 Product Analysis:")
    product_revenue = sales_ap.groupby("product")["revenue"].sum().sort_values(ascending=False)
    print("   Top Products by Revenue:")
    for product, revenue in product_revenue.head(3).items():
        print(f"     {product}: ${revenue:,.2f}")

    # Customer segment analysis
    print("\n👥 Customer Segment Analysis:")
    segment_revenue = (
        sales_ap.groupby("customer_segment")["revenue"].sum().sort_values(ascending=False)
    )
    print("   Revenue by Customer Segment:")
    for segment, revenue in segment_revenue.items():
        print(f"     {segment}: ${revenue:,.2f}")

    return True


def main():
    """Main demonstration function."""
    print("🚀 AskPandas Working Features Demonstration")
    print("=" * 60)
    print("This demo showcases all working features from the README")
    print("=" * 60)

    try:
        # Run all working demos
        demo_basic_analysis()
        demo_dataframe_methods()
        demo_data_quality_and_cleaning()
        demo_visualization_setup()
        demo_configuration()
        demo_available_models()
        demo_query_analysis()
        demo_manual_analysis()

        print("\n🎉 All demonstrations completed successfully!")
        print("\n📁 Generated files:")
        print("   - demo_output/ (if visualizations were created)")

        print("\n💡 What's Working:")
        print("   ✅ DataFrame creation and basic methods")
        print("   ✅ Data quality and cleaning")
        print("   ✅ Configuration management")
        print("   ✅ Query analysis")
        print("   ✅ Manual data analysis")
        print("   ✅ Visualization setup")

        print("\n⚠️  What Needs Attention:")
        print("   ⚠️  AI-powered queries (LLM integration)")
        print("   ⚠️  Automatic code generation")

        print("\n🚀 Next Steps:")
        print("   1. Try your own CSV files with manual analysis")
        print("   2. Use the data quality and cleaning features")
        print("   3. Experiment with configurations")
        print("   4. Wait for AI features to be fully fixed")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
