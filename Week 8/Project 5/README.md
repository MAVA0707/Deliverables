# Project 5: AI churn prediction for a medium B2B SaaS company

**Module 5 — AI Strategy & Business Impact**
Markus von Aschoff · markus@vonaschoff.de · June 2026

---

## Scenario  

Cleo is the CEO of Ravenstack, a medium B2B SaaS company (200 employees). She's skeptical about AI and worried it isn't open about how it works. After a brief pitch at a dinner, she agreed to a meeting.

The goal of this project was to prepare for that meeting: research the sector, find the best use case, validate it with her company's data, and make the case clearly enough that a non-technical CEO can check every claim.

The use case: churn prediction with early-warning alerts.

---

## Sector and company profile

- **Sector:** B2B SaaS (software as a service)
- **Company size:** Medium, 200 employees
- **Use case:** Weekly churn risk scoring with ranked alerts to the customer success team
- **Why this use case:** Direct revenue impact, uses data Ravenstack already has, and the model can show its reasoning — which addresses Cleo's core concern about AI transparency

---

## Deliverables

### Documents

| File | What it is |
|---|---|
| `Ravenstack_Churn_Prediction.docx` | Main proposal: use case discovery, sector research, opportunity and risk mapping, the time-series complexity explanation, solution design, phased implementation plan, and cost estimate |
| `Ravenstack_Churn_Pitch.pptx` | Slide deck to pitch to Cleo and get her approval |
| `/research/Client_Background_Research.docx` | Research notes written for Cleo: all 4 source documents cited in the proposal, with methodology, sample size, and an honest "reliable for / not reliable for" breakdown per source |
| `/research/Internal_Research_Dossier.docx` | Research notes & internal remarks for presenting it to Cleo |

### Dashboard

| File | What it is |
|---|---|
| `/dashboard/Churn_Evidence_Dashboard.html` | Interactive HTML dashboard. Open in any browser. Self-contained (no internet required). 5 sections: headlines, when churn happens, where it concentrates, why customers leave, and which signals are actually predictive |
| `/dashboard/dashboard_compute_data.py` | Reads the 5 Ravenstack CSV files and computes all dashboard metrics. Run this first. Outputs `dashboard_data.json` |
| `/dashboard/ dashboard_build.py` | Reads `dashboard_data.json` and builds the HTML dashboard. Run second |

### Data

| File | Rows | Contents |
|---|---|---|
| `/data/raw/ravenstack_accounts.csv` | 500 | Customer records: industry, country, signup date, plan tier, churn flag |
| `/data/raw/ravenstack_subscriptions.csv` | 5,000 | Subscription history: MRR, ARR, plan changes, billing frequency |
| `/data/raw/ravenstack_feature_usage.csv` | 25,000 | Daily feature events: feature name, usage count, duration, error count |
| `/data/raw/ravenstack_support_tickets.csv` | 2,000 | Support tickets: priority, response time, satisfaction score |
| `/data/raw/ravenstack_churn_events.csv` | 600 | Cancellations: date, reason code, feedback text |

---

## Running the dashboard

You need Python 3.8+ with `pandas` and `numpy`.

```bash
# Install dependencies
pip install pandas numpy

# Step 1: compute metrics from the CSV files
python3 dashboard_compute_data.py

# Step 2: build the HTML file
python3 dashboard_build.py

# Step 3: open in browser
open Churn_Evidence_Dashboard.html   # macOS
xdg-open Churn_Evidence_Dashboard.html   # Linux
```

The CSV files must be in the same directory as the scripts when you run step 1.

---

## Key findings

The data covered January 2023 to December 2024 across 500 accounts, 4,514 active subscriptions, and 600 churn events.

**What the data shows clearly:**

- 53% of churn happens in the first 90 days after signup. This matches the published B2B SaaS benchmark of 70% (Optifai 2026, 939 companies). Onboarding is the highest-leverage moment.
- DevTools is the highest-churn industry segment at 31%, nearly 2x the lowest (Cybersecurity at 16%).
- "Features" and "support" are the top 2 stated cancellation reasons, together accounting for 36% of exits.
- Lifetime lost ARR: $14.1M across the 2-year window.

**What the data does not show clearly:**

- The classic "usage drop before churn" signal is weak in this dataset. Median usage ratio in the 90 days before cancellation versus the 90 days before that: 1.02. Only 18% of churned accounts dropped to under 50% of prior activity.
- Support ticket spikes before churn: no signal. Average tickets in 60 days before churn versus the prior 60 days: 0.3 vs 0.3.
- Plan tier: Basic, Pro, and Enterprise churn at 9 to 10% per subscription. Plan tier is not a risk signal.

**Implication:** the two strong signals (tenure under 90 days and DevTools industry) work for a rule-based health score on day one. The two commonly assumed signals (usage drop, ticket spike) are absent here. This is exactly why the proposal recommends a Phase 1 data audit before committing to an ML approach, and why rule-based heuristics are the documented fallback.

---

## Sources

4 research sources cited in the proposal and documented in `Cleo_Background_Research.docx`:

- **Recurly 2025 Churn Benchmarks** — B2B SaaS median annual churn 3.8%, 1,200+ subscription sites. [recurly.com/research/churn-rate-benchmarks](https://recurly.com/research/churn-rate-benchmarks/)
- **Paddle / ProfitWell Q1 and Q2 2025 reports** — SaaS market churn trends, 34,000+ companies on ProfitWell Metrics
- **Optifai B2B SaaS Benchmark** — SMB monthly churn 3 to 5%, 939 B2B SaaS companies, Q2 2025 to Q1 2026. [optif.ai](https://optif.ai/learn/questions/b2b-saas-churn-rate-benchmark/)
- **Lighter Capital 2025 B2B SaaS Startup Benchmarks** — annual churn by vertical, 155 private B2B SaaS startups. [lightercapital.com](https://www.lightercapital.com/blog/2025-b2b-saas-startup-benchmarks)

