# Reflection — Marketing Channel Statistical Analysis Lab

## What surprised you about the results?  

The most striking finding was how **absolute** the channel differences are. In real marketing analytics work, you usually wrestle with borderline results — channels that perform 10–20% better or worse, where you're genuinely uncertain whether the signal is real. Here, every single one of the 21 pairwise CPA comparisons survived even the most conservative Bonferroni correction with adjusted p-values effectively at zero, and Cohen's d values ranging from 0.88 to 4.82 (all "large" by conventional thresholds).

This reflects a realistic truth: **channel mix matters far more than most within-channel optimisations.** The difference between Email ($0.89 CPA) and Display ($163.10 CPA) is not a marginal performance gap — it is a structural difference in how these channels work. Email reaches people who already trust the brand (high intent, pre-warmed audience). Display reaches random users with banner ads they mostly ignore (low intent, cold audience).

The power analysis was also instructive: for the massive differences we observed, even 30 days of data would have been more than enough. But for realistic within-channel A/B tests (5–8% improvement on Paid Search CPA), we would need 150+ days — far longer than most marketing teams run experiments before declaring a winner.

## How did multiple comparisons correction change your conclusions?

In this particular dataset, corrections changed nothing — all results survived all three thresholds. But the exercise is important for two reasons:

1. **It almost always matters.** In a real dataset with 7 channels, you might find 8 out of 21 pairs nominally significant at p < 0.05. After FDR correction, that might reduce to 4 or 5. The channels you deprioritise based on those extra 3–4 "significant" results could cost the business real money.

2. **The choice of correction method encodes a business judgment.** Bonferroni asks: "What's the probability we have *any* false positive?" This is appropriate when a single false positive is catastrophic (e.g. medical device approvals). BH-FDR asks: "What fraction of our significant findings are false?" This is appropriate when we're making portfolio-level decisions and can absorb occasional false positives — exactly the situation in marketing budget allocation. Using Bonferroni for a 7-channel budget decision would be overly conservative and might cause us to under-act on real opportunities.

## What are the limitations of this analysis?

**Attribution model**: Last-click attribution, which is the implicit model in this data, systematically undervalues channels that operate higher in the funnel (Display, Social, Influencer). A user might see a Display ad, search on Google, and convert via Email — last-click credits Email entirely. The true contribution of Display may be larger than this analysis suggests.

**Diminishing returns**: The budget allocation model assumes linear returns — giving Email 2× the budget produces 2× the conversions. This is unlikely to be true at scale. Email lists are finite, sender reputation limits daily sends, and the marginal subscriber is harder to convert than the average subscriber in historical data.

**Seasonality**: 90 days captures one quarter. If the dataset were from Q4 (holiday season), Email performance might be inflated; if from Q2, Display might be relatively stronger. Budget decisions made on a single quarter's data should be validated across multiple seasons.

**The synthetic data problem**: Real marketing data is messier, with attribution gaps, tracking failures, multi-device journeys, and fraudulent clicks that inflate Display and Social metrics artificially. The clean structure of synthetic data makes statistical testing "too easy."

**Confounding**: Channels aren't independent. Paid Search performance is partly driven by how much brand awareness Email and Display have built. Cutting Display might reduce Paid Search branded query volume 6 months later — a lagged effect invisible to a 90-day snapshot.

## How would you communicate these findings to non-technical stakeholders?

The key is to translate from statistical language to business consequences, while being honest about uncertainty:

**Instead of:** "At α = 0.05 with BH-FDR correction, all 21 pairwise CPA comparisons are significant (all d > 0.8)."

**Say:** "The performance differences between our channels are so large and consistent across 90 days that we can be very confident they're real, not random fluctuations. Email generates conversions for under $1 each; Display costs over $160 per conversion. That's not a measurement error — it's a genuine structural difference in how these channels work."

**For the caveats:** "Before shifting the entire budget, it's worth knowing that this analysis looks backwards — it tells us what worked last quarter, not what will work next quarter. Email is very efficient right now, but there's a ceiling to how many emails we can send profitably. We recommend a phased reallocation with close monitoring rather than a one-time dramatic shift."

**For power analysis:** "If you want to test whether a small change to our Paid Search strategy (say, a 5–10% CPA improvement) is working, you'll need to run that test for at least 3–6 months before you can trust the result. Declaring a winner after two weeks is very likely to be wrong."

The underlying message: **statistics tells us where to look with more confidence, not where the truth definitely lies.**
