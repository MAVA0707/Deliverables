# Lab: In God We Trust, Everyone Else Bring Data
## Marketing Channel Statistical Analysis

**Analyst:** Student  
**Date:** 2024-04-01  
**Budget decision:** $500,000/month across 7 marketing channels  

---

## File Map

| File | Description |
|---|---|
| `data_exploration.ipynb` | Part 1 — Dataset generation, exploration, key metric calculations, and distribution visualisations |
| `statistical_analysis.ipynb` | Parts 2–3 — Pairwise t-tests (CPA), Fisher's exact tests (conversion rates), Bonferroni & BH-FDR correction |
| `power_analysis.ipynb` | Part 4 — Empirical power curves, minimum sample size requirements, current data adequacy assessment |
| `business_recommendations.ipynb` | Part 5 — Composite channel ranking, $500K budget allocation, confidence intervals, visualisations |
| `executive_memo.md` | Business-facing summary with recommendations and statistical caveats |
| `reflection.md` | Personal reflection on surprises, limitations, and communication strategies |
| `marketing_data.csv` | Generated 90-day daily dataset (630 rows × 12 columns) |
| `cpa_comparisons.csv` | All 21 pairwise CPA t-test results with Bonferroni and FDR corrections |
| `fisher_comparisons.csv` | All 21 pairwise Fisher's exact test results with corrections |
| `bootstrap_ci.csv` | 95% bootstrap confidence intervals for CPA per channel |
| `budget_allocation.csv` | Composite score and final budget allocation per channel |
| `group_metrics_overview.png` | Bar charts: CPA, ROAS, CVR, conversions, cost, profit by channel |
| `group_distributions.png` | Histogram overlays of daily CPA and CVR per channel |
| `metric_comparison_heatmap.png` | Heatmap of pairwise CPA p-values |
| `rate_comparison.png` | Horizontal bar chart of conversion rates |
| `correction_comparison.png` | Before/after multiple-comparisons correction comparison |
| `power_analysis_cpa.png` | Power curves for different effect sizes and sample sizes |
| `cpa_confidence_intervals.png` | Error-bar chart of CPA with 95% bootstrap CIs |
| `budget_recommendation.png` | Pie chart + bar chart of recommended budget allocation |

---

## How to Run

1. Install dependencies (all standard):
   ```bash
   pip install numpy pandas scipy matplotlib seaborn
   ```
   SciPy ≥ 1.11 required for `false_discovery_control`.

2. Run notebooks **in order**:
   ```
   data_exploration.ipynb          → generates marketing_data.csv + PNGs
   statistical_analysis.ipynb      → generates cpa_comparisons.csv, fisher_comparisons.csv + PNGs
   power_analysis.ipynb            → generates power_analysis_cpa.png
   business_recommendations.ipynb  → generates budget_recommendation.png, cpa_confidence_intervals.png
   ```

3. Each notebook is self-contained and re-runnable. The synthetic dataset is generated with a fixed random seed (`numpy.random.default_rng(42)`) so results are fully reproducible.

---

## Key Findings (one-line summary per section)

- **Data**: 7 channels × 90 days of daily impressions, clicks, conversions, cost, revenue
- **t-tests**: All 21 CPA pairs significant (Cohen's d 0.88–4.82, all "large")
- **Fisher's**: All 21 conversion-rate pairs significant (p < 0.001 after FDR)
- **Multiple corrections**: All 42 results survive both Bonferroni and BH-FDR
- **Power**: 90 days is sufficient for 10%+ CPA differences; need 150+ days for 5% differences
- **Recommendation**: Email and SEO/Organic are dramatically underinvested; Display should be minimised

See `executive_memo.md` for the full narrative and `reflection.md` for methodological discussion.
