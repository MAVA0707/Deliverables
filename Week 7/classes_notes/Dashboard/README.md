# Week 7 · Day 5 — Example Evaluation Dashboard (Python: Plotly + Panel)

Extra material for **W7 · Day 5 (Data Visualization & the Project 5 Evaluation Dashboard)**.
It's the **code** counterpart to the Tableau/PowerBI lab
(`…/module-5/submodule-3-ai-strategy-business-impact/labs/01_lab_evaluation_dashboard.md`):
the *same* support-ticket scoring eval dashboard, built two ways —

| File | Stack | What it is |
|------|-------|-----------|
| `eval_dashboard_plotly.py` | **Plotly** | One static, shareable dashboard → `eval_dashboard.html` (+ `.png`) |
| `eval_dashboard_panel.py`  | **Panel + Plotly** | The *interactive* app with a category filter (drill-down) |
| `eval_data.py` | pandas/numpy | Shared, **deterministic** sample dataset (reads the lab's real CSV if present) |

Audience: **learning + template** — read it to see the Day-5 data-viz principles applied,
then point `eval_data.load_eval()` at your own evaluation data and the dashboards work unchanged.

## Run it

First, set up an environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then run any of the three pieces:

```bash
# 1. inspect the data
python eval_data.py

# 2. static Plotly dashboard  → eval_dashboard.html (+ eval_dashboard.png)
python eval_dashboard_plotly.py

# 3. interactive Panel app (live filtering) — open the URL it prints
panel serve eval_dashboard_panel.py --show
#    (or `python eval_dashboard_panel.py` for a static panel_dashboard.html snapshot)
```

## The scenario (matches the lab)

A support-ticket classifier is graded by an LLM judge. Stakeholders can't read notebooks —
they need the **communication layer**: accuracy + judge scores **by category**, a **trend**
over time, and the score **distribution**. `eval_data.py` loads the lab's
`support_tickets_labeled.csv` (auto-located), simulates a model prediction + a 0–10 judge
score + latency/cost per ticket (seeded, so output is identical every run), and injects a
**drift on 2024-10-01** (a quiet prompt edit) for the trend panel to expose.

## Each panel applies a Day-5 principle

| Panel | Chart (matched to the question) | Principle on show |
|-------|----------------------------------|-------------------|
| KPI cards | Indicators | Layer-3 business metrics; red when below target |
| Score by category | **Bar** (comparison) | **Color the signal, gray the noise** — only the worst category is colored; **target reference line** |
| Weekly trend | **Line** (trend over time) | **Headline title states the conclusion**; the drift line annotates the *why* |
| Score distribution | **Histogram** (distribution) | Shows the low-score tail a KPI would hide |
| Accuracy by category | **Bar** (comparison) | Same worst-category highlight → the two charts corroborate ("so what: fix billing") |

Deliberately avoided (the lecture's pitfalls): dual-axis, 3D, truncated axes, 12-colour legends,
and any p-values / confidence intervals (dashboards show *conclusions*, not methodology).

## Use it as a template

Replace the data source — return a DataFrame with the columns in `eval_data.EVAL_COLUMNS`
(`ticket_id, submitted_at, category, predicted_category, correct, judge_score, latency_s,
cost_usd`) from your own eval run (LangSmith export, a scoring notebook, etc.) and both
dashboards render it. Tune `TARGET`, `PROFILE`, and `RUN_META` to your engagement.

## Generated artifacts (safe to delete / regenerate)

`eval_dashboard.html`, `eval_dashboard.png`, `panel_dashboard.html`.
