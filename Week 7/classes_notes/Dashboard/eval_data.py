"""
eval_data.py — build the evaluation dataset for the Week 7 · Day 5 example dashboard.

Scenario (matches the Day 5 lab): a support-ticket classifier is scored by an
LLM judge. Stakeholders need a dashboard of *evaluation* results — accuracy and
judge scores by category, a trend over time, and the score distribution.

This module produces ONE tidy DataFrame the dashboards consume. It:
  1. Loads the real `support_tickets_labeled.csv` shipped with the lab if it can
     find it (ticket_id, submitted_at, raw_text, _true_category/_sentiment/_urgency).
  2. Simulates a model PREDICTION per ticket (realistic per-category accuracy) and
     an LLM-judge SCORE (0–10), plus latency and cost — the columns a real eval run
     would log. Everything is seeded, so the dashboard is identical every run.
  3. Falls back to a fully synthetic set if the CSV isn't found, so the template
     runs anywhere.

Swap in your own data: return a DataFrame with the columns documented in
`EVAL_COLUMNS` and the dashboards work unchanged.
"""
from __future__ import annotations
import pathlib
import numpy as np
import pandas as pd

SEED = 7  # week 7 :)  — every load_eval() call returns identical data

EVAL_COLUMNS = [
    "ticket_id", "submitted_at", "category",
    "predicted_category", "correct", "judge_score",
    "latency_s", "cost_usd",
]

# The four categories present in support_tickets_labeled.csv.
CATEGORIES = ["billing", "technical", "feature_request", "praise"]

# Per-category quality. `acc` = P(model predicts the right category);
# `score_mu` = mean LLM-judge score (0–10). "billing" is the weak spot the
# dashboard is designed to surface.
PROFILE = {
    "billing":         dict(acc=0.61, score_mu=6.1),
    "technical":       dict(acc=0.84, score_mu=8.0),
    "feature_request": dict(acc=0.90, score_mu=8.6),
    "praise":          dict(acc=0.92, score_mu=8.8),
}

# Model + judge identity that produced this run. A real eval logs these so the
# dashboard is reproducible (the §1/§3 observability tie-in on the board).
RUN_META = {
    "model": "ticket-classifier v2.3",
    "prompt": "score_prompt v7  (edited 2024-04-28)",
    "judge": "gpt-4o-mini  (temp 0)",
    "dataset": "support_tickets_labeled.csv",
}

# The week a quiet prompt edit shifted the judge baseline — the story the trend
# panel is built to tell. Sits in the back half of the date range so it reads as
# a clear step-down rather than tanking every category's average.
DRIFT_WEEK = pd.Timestamp("2024-10-01")


def _find_labeled_csv() -> pathlib.Path | None:
    """Look for the lab's labeled CSV near this file or under the repo."""
    here = pathlib.Path(__file__).resolve()
    candidates = [
        here.parent / "support_tickets_labeled.csv",
        here.parent.parent / "ac-bootcamp/course/module-5/"
        "submodule-3-ai-strategy-business-impact/labs/support_tickets_labeled.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    # last resort: shallow glob under the repo root
    for c in here.parent.parent.rglob("support_tickets_labeled.csv"):
        return c
    return None


def _simulate(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Add predicted_category, correct, judge_score, latency, cost."""
    out = df.copy()
    preds, scores = [], []
    for cat in out["category"]:
        prof = PROFILE.get(cat, dict(acc=0.8, score_mu=7.5))
        right = rng.random() < prof["acc"]
        if right:
            preds.append(cat)
        else:
            preds.append(rng.choice([c for c in CATEGORIES if c != cat]))
        # judge score: centered on the category mean, a touch lower when wrong
        mu = prof["score_mu"] - (0 if right else 1.6)
        scores.append(float(np.clip(rng.normal(mu, 1.1), 0, 10)))

    out["predicted_category"] = preds
    out["correct"] = (out["predicted_category"] == out["category"]).astype(int)
    out["judge_score"] = np.round(scores, 2)

    # A drift: tickets on/after DRIFT_WEEK score ~1.2 lower (the prompt edit).
    drift = out["submitted_at"] >= DRIFT_WEEK
    out.loc[drift, "judge_score"] = (out.loc[drift, "judge_score"] - 1.2).clip(0, 10).round(2)

    out["latency_s"] = np.round(rng.normal(1.4, 0.4, len(out)).clip(0.3, None), 2)
    out["cost_usd"] = np.round(rng.normal(0.018, 0.004, len(out)).clip(0.004, None), 4)
    return out[EVAL_COLUMNS]


def _synthetic(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Fully synthetic fallback when the CSV isn't available."""
    dates = pd.to_datetime("2024-03-01") + pd.to_timedelta(
        rng.integers(0, 70, n), unit="D")
    df = pd.DataFrame({
        "ticket_id": [f"T{1000+i}" for i in range(n)],
        "submitted_at": dates,
        "category": rng.choice(CATEGORIES, n, p=[0.34, 0.34, 0.20, 0.12]),
    })
    return _simulate(df, rng)


def load_eval(n_min: int = 320) -> pd.DataFrame:
    """Return the evaluation DataFrame (see EVAL_COLUMNS). Deterministic per call."""
    rng = np.random.default_rng(SEED)   # fresh each call → reproducible
    csv = _find_labeled_csv()
    if csv is None:
        return _synthetic(n_min, rng)

    raw = pd.read_csv(csv)
    raw = raw.rename(columns={"_true_category": "category"})
    raw["submitted_at"] = pd.to_datetime(raw["submitted_at"])
    raw["category"] = raw["category"].where(raw["category"].isin(CATEGORIES), "technical")
    df = _simulate(raw[["ticket_id", "submitted_at", "category"]], rng)

    # The shipped CSV is small (~80 rows); upsample with light jitter so the
    # distribution/trend panels read well as a teaching example.
    if len(df) < n_min:
        reps = int(np.ceil(n_min / len(df)))
        boost = pd.concat([df] * reps, ignore_index=True).iloc[:n_min].copy()
        boost["judge_score"] = (boost["judge_score"]
                                + rng.normal(0, 0.4, len(boost))).clip(0, 10).round(2)
        boost["ticket_id"] = [f"T{2000+i}" for i in range(len(boost))]
        df = boost
    return df.reset_index(drop=True)


# --- derived aggregates the panels reuse -------------------------------------
def by_category(df: pd.DataFrame) -> pd.DataFrame:
    g = (df.groupby("category")
           .agg(avg_score=("judge_score", "mean"),
                accuracy=("correct", "mean"),
                n=("ticket_id", "count"))
           .reset_index()
           .sort_values("avg_score"))
    g["avg_score"] = g["avg_score"].round(2)
    g["accuracy"] = (g["accuracy"] * 100).round(1)
    return g


def weekly_trend(df: pd.DataFrame) -> pd.DataFrame:
    g = (df.assign(week=df["submitted_at"].dt.to_period("W").dt.start_time)
           .groupby("week").agg(avg_score=("judge_score", "mean"),
                                n=("ticket_id", "count")).reset_index())
    g["avg_score"] = g["avg_score"].round(2)
    return g


def kpis(df: pd.DataFrame) -> dict:
    return {
        "avg_score": round(df["judge_score"].mean(), 2),
        "accuracy": round(df["correct"].mean() * 100, 1),
        "cost_per_run": round(df["cost_usd"].mean(), 4),
        "p95_latency": round(df["latency_s"].quantile(0.95), 2),
        "n": int(len(df)),
    }


if __name__ == "__main__":
    d = load_eval()
    print(f"rows: {len(d)}  | source: {_find_labeled_csv() or 'synthetic'}")
    print(d.head(6).to_string(index=False))
    print("\nby category:\n", by_category(d).to_string(index=False))
    print("\nKPIs:", kpis(d))
    print("run meta:", RUN_META)
