"""Sales KPI questions over a CSV file, answered in plain English.

Use case: an analyst wants revenue by region, the best products and a monthly trend
chart from ``data/demo_sales.csv`` (100 orders) without writing pandas by hand.

Needs: nothing beyond ``pip install askpandas``. A scripted offline backend stands in for
the LLM (see ``offline_llm.py``); swap in ``OllamaLLM`` or ``OpenAICompatibleLLM`` to let a
real model write the code.

Run: python examples/sales_kpis.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from offline_llm import ScriptedLLM

import askpandas as ap

DATA = Path(__file__).parent / "data" / "demo_sales.csv"

llm = ScriptedLLM(
    {
        "by region": """
revenue_by_region = df0.groupby('region')['revenue'].sum().sort_values(ascending=False)
print(revenue_by_region.round(2))
""",
        "top 3 products": """
top_products = df0.groupby('product')['revenue'].sum().nlargest(3)
for product, revenue in top_products.items():
    print(f"{product}: ${revenue:,.2f}")
""",
        "monthly": """
monthly = df0.assign(month=pd.to_datetime(df0['date']).dt.to_period('M').astype(str))
monthly = monthly.groupby('month', as_index=False)['revenue'].sum()
fig = create_line_chart(monthly, 'month', 'revenue', title='Monthly revenue')
print(monthly.to_string(index=False))
print(save_plot(fig, 'monthly_revenue.png'))
""",
    }
)
ap.set_llm(llm)
ap.set_config(output_dir=str(Path(tempfile.gettempdir()) / "askpandas_examples"))

sales = ap.DataFrame(DATA)
print(f"Loaded {sales.shape()[0]} orders with columns {sales.columns()}\n")

for question in [
    "What is the total revenue by region?",
    "Which are the top 3 products by revenue?",
    "Plot the monthly revenue trend",
]:
    print(f"Q: {question}")
    print(sales.chat(question))

stats = sales._engine.get_engine_stats() if sales._engine else {}
print(f"Queries run: {stats.get('total_queries')}, success rate: {stats.get('success_rate')}%")
