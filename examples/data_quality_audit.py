"""Audit and clean a messy customer table, then test a hypothesis. No LLM involved.

Use case: before analysing ``data/comprehensive_sample.csv`` (1,000 customers) you want a
data-quality score, a cleaned copy and a quick statistical check. These helpers are plain
Python and work without any model.

Needs: nothing beyond ``pip install askpandas``.

Run: python examples/data_quality_audit.py
"""

from __future__ import annotations

from pathlib import Path

import askpandas as ap
from askpandas.utils.data_quality import assess_data_quality, clean_dataframe
from askpandas.utils.statistical import StatisticalAnalyzer

df = ap.DataFrame(Path(__file__).parent / "data" / "comprehensive_sample.csv").df

report = assess_data_quality(df)
print(f"Quality score: {report['data_quality_score']:.1f}/100")
missing = {c: n for c, n in report["missing_data"]["missing_by_column"].items() if n}
print(f"Missing cells: {report['missing_data']['total_missing']} {missing}")
print(f"Duplicate rows: {report['duplicates']['total_duplicates']}")
outlier_cols = sorted(report["outliers"])
print(f"Columns with outlier analysis: {outlier_cols}")
for rec in report["recommendations"][:3]:
    print(f"- [{rec['priority']}] {rec['action']}")

cleaned, log = clean_dataframe(df)
print(f"\nCleaning steps ({len(log)}):")
for step in log:
    print(f"- {step}")

analyzer = StatisticalAnalyzer(cleaned)
anova = analyzer.hypothesis_testing("anova", group_col="membership_type", value_col="income")
print(
    f"\nDoes income differ by membership type? ANOVA F={anova['f_statistic']:.2f}, "
    f"p={anova['p_value']:.3f} -> {'yes' if anova['significant'] else 'no evidence'} at 5%"
)
corr = analyzer.correlation_analysis(method="spearman")
significant = corr["significant_correlations"]
print(f"Significant Spearman correlations at 5%: {len(significant)}")
for c in sorted(significant, key=lambda c: -abs(c["correlation"]))[:3]:
    print(f"- {c['variables'][0]} ~ {c['variables'][1]}: rho={c['correlation']:.2f}")
