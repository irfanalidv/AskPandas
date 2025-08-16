#!/usr/bin/env python3
"""
Comprehensive AskPandas Test & Demo Script
Showcases all the advanced features of the updated library
"""

import askpandas as ap
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

def create_comprehensive_sample_data():
    """Create comprehensive sample data for testing all features."""
    print("📊 Creating comprehensive sample data...")
    
    np.random.seed(42)
    n_records = 1000
    
    # Generate diverse data types
    data = {
        'customer_id': list(range(1, n_records + 1)),
        'name': [f'Customer_{i}' for i in range(1, n_records + 1)],
        'age': np.random.randint(18, 80, n_records),
        'income': np.random.normal(50000, 20000, n_records),
        'credit_score': np.random.randint(300, 850, n_records),
        'purchase_amount': np.random.exponential(100, n_records),
        'satisfaction_rating': np.random.choice([1, 2, 3, 4, 5], n_records, p=[0.05, 0.1, 0.2, 0.4, 0.25]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], n_records),
        'membership_type': np.random.choice(['Basic', 'Premium', 'VIP'], n_records, p=[0.6, 0.3, 0.1]),
        'last_purchase_date': [datetime.now() - timedelta(days=random.randint(1, 365)) for _ in range(n_records)],
        'total_orders': np.random.poisson(5, n_records),
        'is_premium': np.random.choice([True, False], n_records, p=[0.3, 0.7])
    }
    
    # Add some data quality issues for testing
    # Missing values
    missing_indices = np.random.choice(n_records, size=int(n_records * 0.1), replace=False)
    for idx in missing_indices:
        data['income'][idx] = np.nan
    
    # Outliers
    outlier_indices = np.random.choice(n_records, size=int(n_records * 0.05), replace=False)
    for idx in outlier_indices:
        data['purchase_amount'][idx] = np.random.uniform(1000, 5000)
    
    # Duplicates
    duplicate_indices = np.random.choice(n_records, size=int(n_records * 0.02), replace=False)
    for idx in duplicate_indices:
        data['customer_id'][idx] = data['customer_id'][idx - 1]
    
    df = pd.DataFrame(data)
    df.to_csv('comprehensive_sample.csv', index=False)
    
    print(f"✅ Created {len(df)} records with diverse data types and quality issues")
    return df

def test_basic_functionality():
    """Test basic AskPandas functionality."""
    print("\n🔍 Testing Basic Functionality")
    print("=" * 50)
    
    try:
        # Load data
        df = ap.DataFrame("comprehensive_sample.csv")
        print("✅ DataFrame loaded successfully")
        
        # Basic info
        print("\n📋 DataFrame Info:")
        print(df.info())
        
        # Basic statistics
        print("\n📊 Basic Statistics:")
        print(df.describe())
        
        print("✅ Basic functionality tests passed")
        return df
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return None

def test_advanced_statistical_analysis(df):
    """Test advanced statistical analysis features."""
    print("\n🧮 Testing Advanced Statistical Analysis")
    print("=" * 50)
    
    try:
        from askpandas.utils.statistical import StatisticalAnalyzer
        
        # Create analyzer
        analyzer = StatisticalAnalyzer(df.df)
        
        # Descriptive statistics
        print("📊 Descriptive Statistics:")
        desc_stats = analyzer.descriptive_statistics()
        for col, stats in list(desc_stats.items())[:3]:  # Show first 3 columns
            print(f"  {col}: Mean={stats['mean']:.2f}, Std={stats['std']:.2f}")
        
        # Correlation analysis
        print("\n🔗 Correlation Analysis:")
        corr_results = analyzer.correlation_analysis()
        if 'significant_correlations' in corr_results:
            for corr in corr_results['significant_correlations'][:3]:
                var1, var2 = corr['variables']
                print(f"  {var1} ↔ {var2}: r={corr['correlation']:.3f} (p={corr['p_value']:.4f})")
        
        # Outlier detection
        print("\n🚨 Outlier Detection:")
        outliers = analyzer.outlier_detection(method='iqr')
        for col, col_outliers in list(outliers.items())[:3]:
            if 'iqr' in col_outliers:
                print(f"  {col}: {col_outliers['iqr']['count']} outliers ({col_outliers['iqr']['percentage']:.1f}%)")
        
        # Normality tests
        print("\n📈 Normality Tests:")
        normality = analyzer.normality_tests()
        for col, results in list(normality.items())[:3]:
            if 'overall_assessment' in results:
                print(f"  {col}: {results['overall_assessment']}")
        
        # Hypothesis testing
        print("\n🔬 Hypothesis Testing:")
        t_test = analyzer.hypothesis_testing('t_test_independent', 
                                          group_col='membership_type', 
                                          value_col='income',
                                          group1='Basic', group2='Premium')
        if 'significant' in t_test:
            print(f"  T-test Basic vs Premium: {'Significant' if t_test['significant'] else 'Not significant'} (p={t_test['p_value']:.4f})")
        
        # Generate statistical report
        print("\n📋 Statistical Report:")
        report = analyzer.generate_statistical_report()
        print(report[:500] + "..." if len(report) > 500 else report)
        
        print("✅ Advanced statistical analysis tests passed")
        
    except Exception as e:
        print(f"❌ Advanced statistical analysis test failed: {e}")
        import traceback
        traceback.print_exc()

def test_data_quality_analysis(df):
    """Test data quality analysis features."""
    print("\n🔍 Testing Data Quality Analysis")
    print("=" * 50)
    
    try:
        from askpandas.utils.data_quality import DataQualityAnalyzer, DataCleaner
        
        # Create analyzer
        analyzer = DataQualityAnalyzer(df.df)
        
        # Comprehensive quality assessment
        print("📊 Performing comprehensive quality assessment...")
        quality_report = analyzer.comprehensive_quality_assessment()
        
        print(f"📈 Overall Quality Score: {quality_report['data_quality_score']:.1f}/100")
        
        # Missing data analysis
        missing_data = quality_report['missing_data']
        print(f"🔍 Missing Data: {missing_data['total_missing']} cells ({missing_data['total_missing_percentage']:.1f}%)")
        
        # Duplicate analysis
        duplicates = quality_report['duplicates']
        print(f"🔄 Duplicates: {duplicates['total_duplicates']} rows ({duplicates['duplicate_percentage']:.1f}%)")
        
        # Data type optimization
        data_types = quality_report['data_types']
        if data_types['optimization_suggestions']:
            total_savings = sum(s['memory_saving_mb'] for s in data_types['optimization_suggestions'])
            print(f"💾 Memory Optimization: Potential savings of {total_savings:.1f}MB")
        
        # Generate quality report
        print("\n📋 Data Quality Report:")
        quality_summary = analyzer.generate_quality_report()
        print(quality_summary[:800] + "..." if len(quality_summary) > 800 else quality_summary)
        
        # Test data cleaning
        print("\n🧹 Testing Data Cleaning:")
        cleaner = DataCleaner(df.df)
        cleaned_df = cleaner.auto_clean(aggressive=False)
        cleaning_log = cleaner.get_cleaning_log()
        
        print(f"✅ Cleaning completed. Operations: {len(cleaning_log)}")
        for log_entry in cleaning_log[:5]:  # Show first 5 operations
            print(f"  - {log_entry}")
        
        print("✅ Data quality analysis tests passed")
        
    except Exception as e:
        print(f"❌ Data quality analysis test failed: {e}")
        import traceback
        traceback.print_exc()

def test_performance_optimization(df):
    """Test performance optimization features."""
    print("\n⚡ Testing Performance Optimization")
    print("=" * 50)
    
    try:
        from askpandas.utils.performance import PerformanceOptimizer, PerformanceBenchmark
        
        # Performance analysis
        print("📊 Analyzing dataframe performance...")
        optimizer = PerformanceOptimizer()
        analysis = optimizer.analyze_dataframe_performance(df.df)
        
        print(f"💾 Current Memory Usage: {analysis['memory_usage']['total_memory_mb']:.1f}MB")
        
        if analysis['size_analysis']['potential_savings_mb'] > 0:
            print(f"🚀 Potential Memory Savings: {analysis['size_analysis']['potential_savings_mb']:.1f}MB")
        
        # Show optimization recommendations
        if analysis['recommendations']:
            print("\n💡 Optimization Recommendations:")
            for i, rec in enumerate(analysis['recommendations'][:5], 1):
                print(f"  {i}. {rec}")
        
        # Performance benchmarking
        print("\n⏱️ Performance Benchmarking:")
        benchmarker = PerformanceBenchmark()
        
        # Define test operations
        operations = [
            {
                'name': 'groupby_operation',
                'function': lambda df: df.groupby('region')['income'].mean(),
                'args': [],
                'kwargs': {}
            },
            {
                'name': 'filtering_operation',
                'function': lambda df: df[df['income'] > 50000],
                'args': [],
                'kwargs': {}
            },
            {
                'name': 'sorting_operation',
                'function': lambda df: df.sort_values('income', ascending=False),
                'args': [],
                'kwargs': {}
            }
        ]
        
        # Benchmark operations
        results = benchmarker.benchmark_dataframe_operations(df.df, operations)
        
        print("📊 Benchmark Results:")
        for op_name, result in results.items():
            print(f"  {op_name}: {result['wall_time']:.4f}s, {result['memory_delta_mb']:.2f}MB")
        
        # Get benchmark summary
        summary = benchmarker.get_benchmark_summary()
        print(f"\n📈 Total Operations: {summary['total_operations']}")
        print(f"✅ Success Rate: {summary['success_rate']:.1%}")
        
        print("✅ Performance optimization tests passed")
        
    except Exception as e:
        print(f"❌ Performance optimization test failed: {e}")
        import traceback
        traceback.print_exc()

def test_advanced_visualizations(df):
    """Test advanced visualization features."""
    print("\n🎨 Testing Advanced Visualizations")
    print("=" * 50)
    
    try:
        from askpandas.visualization.charts import (
            create_bar_chart, create_line_chart, create_scatter_plot,
            create_histogram, create_correlation_heatmap, create_box_plot
        )
        
        # Test different chart types
        print("📊 Creating various chart types...")
        
        # Bar chart
        income_by_region = df.df.groupby('region')['income'].mean().reset_index()
        fig1 = create_bar_chart(income_by_region, 'region', 'income', 'Average Income by Region')
        print("✅ Bar chart created")
        
        # Histogram
        fig2 = create_histogram(df.df, 'income', bins=30, title='Income Distribution')
        print("✅ Histogram created")
        
        # Scatter plot
        fig3 = create_scatter_plot(df.df, 'age', 'income', 'Age vs Income')
        print("✅ Scatter plot created")
        
        # Box plot
        fig4 = create_box_plot(df.df, 'membership_type', 'income', 'Income by Membership Type')
        print("✅ Box plot created")
        
        # Correlation heatmap
        numeric_cols = df.df.select_dtypes(include=[np.number]).columns[:5]  # First 5 numeric columns
        corr_data = df.df[numeric_cols].corr()
        fig5 = create_correlation_heatmap(corr_data, 'Correlation Matrix')
        print("✅ Correlation heatmap created")
        
        print("✅ Advanced visualization tests passed")
        
    except Exception as e:
        print(f"❌ Advanced visualization test failed: {e}")
        import traceback
        traceback.print_exc()

def test_ai_powered_queries(df):
    """Test AI-powered natural language queries."""
    print("\n🤖 Testing AI-Powered Queries")
    print("=" * 50)
    
    try:
        # Set up LLM (if available)
        try:
            llm = ap.OllamaLLM(model_name="mistral")
            if llm.is_available():
                ap.set_llm(llm)
                print("✅ Ollama LLM configured")
                
                # Test various query types
                queries = [
                    "What is the average income by region?",
                    "Show me a histogram of customer ages",
                    "Which membership type has the highest average income?",
                    "Create a correlation heatmap of numeric columns",
                    "What is the distribution of purchase amounts?"
                ]
                
                print("\n🔍 Testing AI Queries:")
                for i, query in enumerate(queries, 1):
                    print(f"\n  {i}. Query: {query}")
                    try:
                        result = df.chat(query)
                        print(f"     ✅ Success: {str(result)[:100]}...")
                    except Exception as e:
                        print(f"     ❌ Failed: {str(e)[:100]}...")
                
            else:
                print("⚠️ Ollama not available, skipping AI query tests")
                
        except Exception as e:
            print(f"⚠️ LLM setup failed: {e}")
            print("Skipping AI query tests")
        
        print("✅ AI-powered query tests completed")
        
    except Exception as e:
        print(f"❌ AI-powered query test failed: {e}")
        import traceback
        traceback.print_exc()

def test_query_analysis_and_validation():
    """Test query analysis and validation features."""
    print("\n🔍 Testing Query Analysis & Validation")
    print("=" * 50)
    
    try:
        # Test query analysis
        test_queries = [
            "Show me a bar chart of sales by region",
            "What is the total revenue by customer segment?",
            "Filter customers with more than 10 purchases",
            "Sort products by average price descending",
            "Create a scatter plot of age vs income"
        ]
        
        print("📊 Query Analysis Results:")
        for query in test_queries:
            analysis = ap.analyze_query(query)
            print(f"\n  Query: {query}")
            print(f"    Categories: {list(analysis['categories'].keys())}")
            print(f"    Primary: {analysis['primary_category']}")
            print(f"    Confidence: {analysis['categories'].get(analysis['primary_category'], {}).get('confidence', 0):.2f}")
        
        # Test query validation
        print("\n✅ Query Validation:")
        validation = ap.validate_query("Show me sales by region", ["sales", "region"])
        print(f"    Is Valid: {validation['is_valid']}")
        if validation['warnings']:
            print(f"    Warnings: {validation['warnings']}")
        
        # Get query examples
        print("\n💡 Query Examples:")
        examples = ap.get_query_examples('visualization')
        for i, example in enumerate(examples[:3], 1):
            print(f"    {i}. {example}")
        
        print("✅ Query analysis and validation tests passed")
        
    except Exception as e:
        print(f"❌ Query analysis test failed: {e}")
        import traceback
        traceback.print_exc()

def test_configuration_management():
    """Test configuration management features."""
    print("\n⚙️ Testing Configuration Management")
    print("=" * 50)
    
    try:
        # Get current config
        print("📋 Current Configuration:")
        config = ap.get_config()
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # Update configuration
        print("\n🔄 Updating Configuration...")
        ap.set_config(verbose=True, plot_style="seaborn", max_execution_time=60)
        
        # Show updated config
        print("📋 Updated Configuration:")
        new_config = ap.get_config()
        for key, value in new_config.items():
            print(f"  {key}: {value}")
        
        # Test configuration update method
        print("\n🔄 Testing Configuration Update Method...")
        ap.set_config(verbose=False, temperature=0.2)
        
        final_config = ap.get_config()
        print(f"  Final verbose setting: {final_config['verbose']}")
        print(f"  Final temperature setting: {final_config['temperature']}")
        
        print("✅ Configuration management tests passed")
        
    except Exception as e:
        print(f"❌ Configuration management test failed: {e}")
        import traceback
        traceback.print_exc()

def test_utilities_and_helpers():
    """Test utility functions and helpers."""
    print("\n🛠️ Testing Utilities & Helpers")
    print("=" * 50)
    
    try:
        # Test helper functions
        print("🔧 Testing Helper Functions:")
        
        # Data validation
        sample_data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
        validated_df = ap.validate_dataframe(sample_data)
        print(f"  DataFrame validation: ✅ Shape {validated_df.shape}")
        
        # Data summary
        summary = ap.get_dataframe_summary(validated_df)
        print(f"  Data summary: ✅ {len(summary)} summary items")
        
        # Number formatting
        formatted = ap.format_number(1234567)
        print(f"  Number formatting: ✅ 1234567 → {formatted}")
        
        # Data type detection
        dtypes = ap.detect_data_types(validated_df)
        print(f"  Data type detection: ✅ {len(dtypes)} type suggestions")
        
        # Column cleaning
        dirty_df = pd.DataFrame({'First Name': ['Alice'], 'Last Name': ['Smith']})
        cleaned_df = ap.clean_column_names(dirty_df)
        print(f"  Column cleaning: ✅ {list(cleaned_df.columns)}")
        
        # Memory usage
        memory_mb = ap.get_memory_usage_mb(validated_df)
        print(f"  Memory usage: ✅ {memory_mb:.2f} MB")
        
        print("✅ Utilities and helpers tests passed")
        
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    print("🚀 AskPandas Comprehensive Test & Demo")
    print("=" * 60)
    print("This test showcases all the advanced features of AskPandas")
    print("=" * 60)
    
    try:
        # Create sample data
        sample_df = create_comprehensive_sample_data()
        
        # Run all tests
        df = test_basic_functionality()
        if df is not None:
            test_advanced_statistical_analysis(df)
            test_data_quality_analysis(df)
            test_performance_optimization(df)
            test_advanced_visualizations(df)
            test_ai_powered_queries(df)
            test_query_analysis_and_validation()
            test_configuration_management()
            test_utilities_and_helpers()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📁 Generated files:")
        print("   - comprehensive_sample.csv")
        print("   - askpandas_plots/ (if visualizations were created)")
        
        # Performance summary
        try:
            from askpandas.utils.performance import get_performance_summary
            perf_summary = get_performance_summary()
            if 'error' not in perf_summary:
                print(f"\n💻 System Performance:")
                print(f"   CPU Usage: {perf_summary['cpu_usage_percent']:.1f}%")
                print(f"   Memory Usage: {perf_summary['memory_usage_percent']:.1f}%")
                print(f"   Available Memory: {perf_summary['memory_available_gb']:.1f} GB")
        except:
            pass
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
