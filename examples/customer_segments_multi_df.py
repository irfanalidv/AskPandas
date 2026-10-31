"""Join two tables in one question: which customer segment brings the most revenue?

Use case: orders live in ``data/demo_sales.csv`` and customer profiles in
``data/demo_customers.csv``. ``askpandas.chat`` exposes them to the generated code as
``df0`` and ``df1`` so a single question can join and aggregate across both.

Needs: nothing beyond ``pip install askpandas`` (scripted offline backend, see
``offline_llm.py``).

Run: python examples/customer_segments_multi_df.py
"""

from __future__ import annotations

from pathlib import Path

from offline_llm import ScriptedLLM

import askpandas as ap

DATA = Path(__file__).parent / "data"

ap.set_llm(
    ScriptedLLM(
        {
            "segment": """
orders = df0.merge(df1[['customer_id', 'segment']], on='customer_id', how='left')
summary = orders.groupby('segment').agg(
    orders=('revenue', 'size'),
    revenue=('revenue', 'sum'),
    avg_order=('revenue', 'mean'),
).sort_values('revenue', ascending=False)
print(summary.round(2))
""",
            "never ordered": """
inactive = df1[~df1['customer_id'].isin(df0['customer_id'])]
print(f"{len(inactive)} of {len(df1)} customers have no orders in this period")
print(inactive[['customer_id', 'name', 'segment']].head(5).to_string(index=False))
""",
        }
    )
)

sales = ap.DataFrame(DATA / "demo_sales.csv")
customers = ap.DataFrame(DATA / "demo_customers.csv")

for question in [
    "Join orders with customers and compare revenue by customer segment",
    "Which customers never ordered?",
]:
    print(f"Q: {question}")
    print(ap.chat(question, sales, customers))
