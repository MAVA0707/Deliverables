# MEMORANDUM

**To:** Chief Marketing Officer  
**From:** Marketing Analytics Team  
**Date:** 2024-04-01  
**Re:** Statistically-Rigorous Marketing Channel Budget Allocation — $500K Monthly  
**Dataset:** Synthetic Marketing Channel Performance Dataset (90 days, 7 channels, N=630 daily observations)  
**Period Analysed:** January 1 – March 31, 2024 

---

## Executive Summary

We analysed 90 days of daily performance data across seven marketing channels using rigorous statistical testing, multiple-comparisons correction, and bootstrap confidence intervals. **All seven channels show statistically significant differences** in both cost-per-acquisition (CPA) and conversion rate — differences so large (Cohen's d > 1.0 for all pairs) that they are clearly economically meaningful, not statistical noise.

**Recommended allocation of the $500,000 monthly budget:**

| Priority | Channel | Recommended Allocation | Share |
|---|---|---|---|
| 1 | Email | $123,239 | 24.6% |
| 2 | SEO/Organic | $105,634 | 21.1% |
| 3 | Affiliate | $82,160 | 16.4% |
| 4 | Paid Search | $76,291 | 15.3% |
| 5 | Social Media | $46,948 | 9.4% |
| 6 | Influencer | $41,080 | 8.2% |
| 7 | Display | $24,648 | 4.9% |

**Total: $500,000**

---

## Key Findings

### 1. Top Performing Channels

**Email** is the highest-performing channel by every metric:
- CPA: **$0.89** (95% Bootstrap CI: $0.91–$1.06) — over 160× cheaper than Display
- ROAS: **101×** — every $1 in email spend returns $101 in revenue
- Conversion Rate: **6.17%** — highest of any channel

**SEO/Organic** is the second-best performer:
- CPA: **$1.55** (95% CI: $1.57–$1.79)
- ROAS: **58.9×** — extremely capital-efficient
- Conversion Rate: **5.58%**

Both channels are statistically distinct from all paid channels (Benjamini–Hochberg FDR-adjusted p ≈ 0 for all pairings, Cohen's d range 1.5–4.8, indicating *large* practical effect sizes).

### 2. Statistically Significant Differences Found

Using pairwise independent t-tests for CPA (21 pairs) and Fisher's exact test for conversion rates (21 pairs):

- **Before correction**: 21/21 CPA pairs and 21/21 conversion-rate pairs significant at α = 0.05
- **After Bonferroni correction** (α/21 = 0.0024): All 42 tests still significant — indicating effect sizes are genuine, not marginal
- **After Benjamini–Hochberg FDR correction** (expected FDR ≤ 5%): All 42 tests remain significant

This is unusually strong evidence. In a typical marketing dataset we would expect many borderline results; here, every channel combination is reliably distinguishable.

### 3. Data Adequacy (Power Analysis)

Using Monte Carlo simulation (1,000 iterations per scenario):

| True CPA Difference | Power at 90 Days | Min Days for 80% Power | Status |
|---|---|---|---|
| 5% | 61% | ~180 days | ✗ Insufficient |
| 10% | 99% | ~60 days | ✓ Sufficient |
| 15% | 100% | ~30 days | ✓ Sufficient |
| 20% | 100% | ~30 days | ✓ Sufficient |

**Conclusion**: For the large differences observed (50%–16,000% CPA gaps), 90 days is vastly adequate. For *future* A/B tests within a single channel (e.g., testing ad copy variants likely to differ by 5–8%), we would need **at least 150–180 days** to achieve 80% power.

---

## Recommendations

### Strategic Actions

1. **Email — Scale aggressively.** Current spend is proportionally low relative to its returns. Invest in list growth, segmentation, and automation. Budget: $123,239/month (↑ from a naive even split of $71,429).

2. **SEO/Organic — Sustained content investment.** With near-zero marginal conversion cost, every incremental improvement in organic rankings compounds over time. Budget: $105,634/month.

3. **Affiliate — Maintain with structure.** Positive ROAS (4.86×) and solid CPA ($21.10). Introduce performance-based contracts and regular audits to sustain quality. Budget: $82,160/month.

4. **Paid Search — Optimise, don't cut.** ROAS of 3.19× is acceptable and provides intent-driven traffic. Focus on Quality Score improvement and negative keyword expansion to push CPA below $25. Budget: $76,291/month.

5. **Social Media — Reduce and focus.** CPA of $66.12 with ROAS of only 1.23× is marginally profitable. Redirect spend to retargeting (users who visited site) and abandon cold-audience prospecting campaigns. Budget: $46,948/month (↓).

6. **Influencer — Treat as brand, not performance.** ROAS of 1.43× and the highest CPA after Display do not justify a large direct-response budget. Retain for seasonal campaigns and brand storytelling only. Budget: $41,080/month (↓).

7. **Display — Minimum floor only.** ROAS of 0.47× means Display currently loses money on direct response. Retain only for remarketing (cookie-based retargeting can be profitable even when prospecting is not). Budget: $24,648/month (↓ significantly).

---

## Statistical Caveats

**1. Dataset limitations and source.**  
This analysis uses a 90-day synthetic dataset modelled on real e-commerce marketing benchmarks. The synthetic nature means the data cannot capture real-world confounders (seasonality, competitive bids, attribution window debates, cross-channel assist effects). Results should be validated against your actual attribution system.

**2. Multiple comparisons correction applied.**  
With 42 total tests, we expected ~2.1 false positives by chance at α = 0.05 (uncorrected). We applied both Bonferroni and Benjamini–Hochberg (FDR) corrections; all results survive both. This substantially reduces the risk of acting on noise.

**3. Confidence intervals.**  
All CPA figures are reported with 95% bootstrap confidence intervals (1,000 resamples). CIs are narrow relative to inter-channel differences, confirming stability. Example: Email CPA CI [$0.91–$1.06] does not overlap with Paid Search CI [$30.10–$33.75].

**4. Statistical significance ≠ practical sufficiency.**  
We can confirm that Email and Display are *different* channels. Whether reallocating $50,000 from Display to Email will produce $5M in incremental revenue depends on **scale constraints** not captured here: email list saturation, sender reputation limits, and diminishing returns at higher send volumes.

**5. Attribution assumptions.**  
This analysis uses a last-click attribution model implicit in the conversion data. Display and Social Media are typically undervalued by last-click, as they often contribute to awareness without being the final touchpoint. A multi-touch attribution model may partially rehabilitate their apparent performance.

**6. Power analysis limitations.**  
Simulation assumes normally-distributed daily CPA with 15% coefficient of variation. If actual CPA is heavy-tailed (common in paid search), power estimates may be optimistic. We recommend treating the 5%-effect-size requirement of 150+ days as a conservative lower bound.

**7. External factors.**  
Seasonality, macroeconomic conditions, competitive activity, and platform algorithm changes can all shift channel performance significantly in ways that 90 days of historical data cannot predict.

---

## Next Steps

1. **Implement reallocation** in two phases: 30% adjustment this month, full adjustment next month, to allow campaign managers to adapt.
2. **Commission multi-touch attribution study** to fairly evaluate Display and Social's upper-funnel contributions.
3. **Set up prospective tracking**: log daily CPA per channel for the next 90 days post-reallocation to measure whether the changes produced the expected improvements.
4. **A/B test Email at higher budgets**: Run a controlled 60-day test at 2× current Email spend (requires 90+ day runway for 80% power on 5% CPA improvement).
5. **Investigate Email/SEO interaction effects**: High-converting email recipients may be the same users who found the brand through organic search — understanding this assists with cross-channel attribution.
6. **Review Display creative**: Low ROAS may partly reflect poor ad creative or audience targeting rather than channel-level inefficiency.

---

*Prepared by the Marketing Analytics team. Statistical methodology: independent Welch t-tests, Fisher's exact test, Bonferroni and Benjamini–Hochberg FDR corrections, Monte Carlo power analysis (1,000 simulations), 95% bootstrap confidence intervals (1,000 resamples). All code available in the accompanying notebooks.*
