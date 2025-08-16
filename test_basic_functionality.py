#!/usr/bin/env python3
"""
Basic AskPandas Functionality Test
Tests core features without requiring LLM setup
"""

import askpandas as ap
import pandas as pd
import numpy as np

def test_basic_dataframe_operations():
    """Test basic DataFrame operations."""
    print("🔍 Testing Basic DataFrame Operations")
    print("=" * 50)
    
    # Test with the demo data
    sales_df = ap.DataFrame("demo_sales.csv")
    customers_df = ap.DataFrame("demo_customers.csv")
    
    print(f"✅ Sales DataFrame created: {sales_df}")
    print(f"✅ Customers DataFrame created: {customers_df}")
    
    # Test basic info
    print("\n📊 Sales DataFrame Info:")
    print(sales_df.info())
    
    print("\n📊 Customers DataFrame Info:")
    print(customers_df.info())
    
    # Test shape and columns
    print(f"\n📏 Sales DataFrame shape: {sales_df.shape()}")
    print(f"📋 Sales DataFrame columns: {sales_df.columns()}")
    
    # Test head and tail
    print("\n📄 First 3 rows of sales data:")
    print(sales_df.head(3))
    
    print("\n📄 Last 3 rows of sales data:")
    print(sales_df.tail(3))
    
    # Test data types
    print(f"\n🔧 Sales DataFrame data types: {sales_df.dtypes()}")
    
    return sales_df, customers_df

def test_data_analysis():
    """Test data analysis capabilities."""
    print("\n🧮 Testing Data Analysis Capabilities")
    print("=" * 50)
    
    sales_df = ap.DataFrame("demo_sales.csv")
    
    # Test describe
    print("📊 Statistical Description:")
    print(sales_df.describe())
    
    # Test summary stats
    print("\n📈 Summary Statistics:")
    summary = sales_df.get_summary_stats()
    for key, value in summary.items():
        if key in ['shape', 'columns', 'numeric_columns', 'categorical_columns']:
            print(f"   {key}: {value}")
        elif key in ['memory_usage', 'total_memory_mb']:
            print(f"   {key}: {value:.2f} MB")
        else:
            print(f"   {key}: {value}")
    
    # Test column info
    print("\n📋 Revenue Column Information:")
    revenue_info = sales_df.get_column_info("revenue")
    for key, value in revenue_info.items():
        if key in ['min', 'max', 'mean', 'median', 'std']:
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    return sales_df

def test_data_manipulation():
    """Test data manipulation capabilities."""
    print("\n🔧 Testing Data Manipulation Capabilities")
    print("=" * 50)
    
    sales_df = ap.DataFrame("demo_sales.csv")
    
    # Test filtering
    print("🔍 Filtering high-value orders (>$1000):")
    high_value = sales_df.query("revenue > 1000")
    print(f"   Found {len(high_value)} high-value orders")
    if len(high_value) > 0:
        print("   Sample high-value orders:")
        print(high_value.head(3))
    
    # Test sorting
    print("\n📊 Top 5 orders by revenue:")
    top_orders = sales_df.sort_values("revenue", ascending=False).head(5)
    print(top_orders[['date', 'region', 'product', 'revenue']])
    
    # Test grouping
    print("\n📈 Revenue by region:")
    region_revenue = sales_df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    print(region_revenue)
    
    # Test aggregation
    print("\n📊 Product performance:")
    product_stats = sales_df.groupby("product").agg({
        'quantity': ['sum', 'mean'],
        'revenue': ['sum', 'mean'],
        'price': 'mean'
    }).round(2)
    print(product_stats)
    
    return sales_df

def test_utility_functions():
    """Test utility functions."""
    print("\n🛠️ Testing Utility Functions")
    print("=" * 50)
    
    # Test column cleaning
    print("🧹 Testing column name cleaning:")
    messy_df = ap.DataFrame({
        "First Name": ["Alice", "Bob", "Charlie"],
        "Last Name": ["Smith", "Jones", "Brown"],
        "Age (Years)": [25, 30, 35],
        "Salary ($)": [50000, 60000, 70000]
    })
    
    print("   Before cleaning:")
    print(f"     Columns: {list(messy_df.df.columns)}")
    
    cleaned_df = messy_df.clean_columns()
    print("   After cleaning:")
    print(f"     Columns: {list(cleaned_df.df.columns)}")
    
    # Test data validation
    print("\n✅ Testing data validation:")
    try:
        valid_df = ap.DataFrame("demo_sales.csv")
        print("   ✅ Valid CSV file loaded successfully")
    except Exception as e:
        print(f"   ❌ Error loading CSV: {e}")
    
    return cleaned_df

def test_visualization_setup():
    """Test visualization setup (without creating plots)."""
    print("\n🎨 Testing Visualization Setup")
    print("=" * 50)
    
    # Test configuration
    print("⚙️ Current configuration:")
    config = ap.get_config()
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # Test plot style setting
    print("\n🎨 Setting plot style to 'ggplot':")
    ap.set_config(plot_style="ggplot", verbose=True)
    
    print("✅ Configuration updated successfully")
    
    # Test available models
    print("\n🤖 Available models:")
    models = ap.get_available_models()
    for provider, model_list in models.items():
        print(f"   {provider}: {', '.join(model_list[:3])}...")
    
    return True

def main():
    """Main test function."""
    print("🚀 AskPandas Basic Functionality Test")
    print("=" * 60)
    print("Testing core features without LLM requirement")
    print("=" * 60)
    
    try:
        # Run all tests
        sales_df, customers_df = test_basic_dataframe_operations()
        sales_df = test_data_analysis()
        sales_df = test_data_manipulation()
        cleaned_df = test_utility_functions()
        test_visualization_setup()
        
        print("\n🎉 All basic functionality tests completed successfully!")
        print("\n📊 Test Summary:")
        print(f"   - Sales data: {sales_df.shape()} records")
        print(f"   - Customer data: {customers_df.shape()} records")
        print(f"   - Cleaned test data: {cleaned_df.shape()} records")
        
        print("\n💡 To test AI-powered features, set up Ollama:")
        print("   ollama serve")
        print("   ollama pull mistral")
        print("   Then run: python demo.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
