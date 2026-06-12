#!/usr/bin/env python3
"""
Ravenstack Churn Risk Scoring API
Serves the top at-risk accounts for the n8n weekly digest workflow.

Setup:
    pip install flask pandas numpy python-dotenv
    DATA_DIR=data python3 scoring_api.py

Endpoints:
    GET /api/churn/top-accounts?limit=20
    GET /health
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR = os.getenv("DATA_DIR", "data")
PORT     = int(os.getenv("PORT", 5678))


# ── Load data once at startup ─────────────────────────────────────────────────
def _load():
    accounts = pd.read_csv(f"{DATA_DIR}/ravenstack_accounts.csv")
    subs     = pd.read_csv(f"{DATA_DIR}/ravenstack_subscriptions.csv")
    usage    = pd.read_csv(f"{DATA_DIR}/ravenstack_feature_usage.csv")

    accounts["signup_date"] = pd.to_datetime(accounts["signup_date"])
    subs["start_date"]      = pd.to_datetime(subs["start_date"])
    subs["end_date"]        = pd.to_datetime(subs["end_date"], errors="coerce")
    usage["usage_date"]     = pd.to_datetime(usage["usage_date"])

    return accounts, subs, usage


accounts_df, subs_df, usage_df = _load()


# ── Scoring logic ─────────────────────────────────────────────────────────────
def compute_risk_scores(limit: int = 20, reference_date: datetime = None) -> list:
    """
    Score every active non-churned account using the rule-based model from Phase 1.

    Scoring rubric (max 100 pts):
      Tenure < 30 days          → +40  (new accounts are highest risk)
      Tenure 30–90 days         → +25
      DevTools industry         → +25  (2× the base churn rate)
      Usage drop > 50% (30d)   → +15  (weak signal, applied where present)
      Usage drop 30–50%         → +8
      Month-to-month billing    → +10  (lower commitment than annual)
      Enterprise + < 5 seats   → +10  (possible buyer's remorse)
    """
    today = reference_date or datetime.utcnow()

    # Active, non-churned accounts
    active = accounts_df[accounts_df["churn_flag"] == False].copy()
    active_subs = subs_df[subs_df["end_date"].isna()].copy()

    # Most recent active subscription per account (rename to avoid column conflicts)
    latest = (
        active_subs.sort_values("start_date")
        .groupby("account_id")
        .last()
        .reset_index()[["account_id", "plan_tier", "seats", "mrr_amount", "billing_frequency"]]
        .rename(columns={"plan_tier": "sub_plan", "seats": "sub_seats"})
    )

    df = active.merge(latest, on="account_id", how="left")
    df["tenure_days"] = (today - df["signup_date"]).dt.days

    # Usage signals
    ua = usage_df.merge(
        subs_df[["subscription_id", "account_id"]], on="subscription_id", how="left"
    )
    u30  = ua[ua["usage_date"] > today - timedelta(days=30)].groupby("account_id")["usage_count"].sum().rename("u30")
    u90  = ua[ua["usage_date"] > today - timedelta(days=90)].groupby("account_id")["usage_count"].sum().rename("u90")
    last = ua.groupby("account_id")["usage_date"].max().rename("last_seen")

    df = df.merge(u30, on="account_id", how="left")
    df = df.merge(u90, on="account_id", how="left")
    df = df.merge(last, on="account_id", how="left")

    df["u30"]         = df["u30"].fillna(0)
    df["u90"]         = df["u90"].fillna(0)
    df["days_since"]  = (today - df["last_seen"]).dt.days.fillna(999).astype(int)
    df["baseline"]    = df["u90"] / 3
    df["drop_ratio"]  = np.where(df["baseline"] > 0, df["u30"] / df["baseline"], 1.0)

    # Score
    df["score"] = 0
    df.loc[df["tenure_days"] < 30, "score"]                                           += 40
    df.loc[(df["tenure_days"] >= 30) & (df["tenure_days"] < 90), "score"]             += 25
    df.loc[df["industry"] == "DevTools", "score"]                                      += 25
    df.loc[df["drop_ratio"] < 0.5, "score"]                                           += 15
    df.loc[(df["drop_ratio"] >= 0.5) & (df["drop_ratio"] < 0.7), "score"]             += 8
    df.loc[df["billing_frequency"] == "monthly", "score"]                              += 10
    df.loc[(df["sub_plan"] == "Enterprise") & (df["sub_seats"] < 5), "score"]         += 10

    def build_signals(row):
        signals = []
        if row["tenure_days"] < 90:
            signals.append(f"new account — only {int(row['tenure_days'])} days old")
        if row["industry"] == "DevTools":
            signals.append("DevTools segment (highest churn rate in the data)")
        if row["baseline"] > 0 and row["drop_ratio"] < 0.7:
            drop_pct = int((1 - row["drop_ratio"]) * 100)
            signals.append(f"product usage down {drop_pct}% versus the prior period")
        if row["billing_frequency"] == "monthly":
            signals.append("month-to-month contract (no annual commitment)")
        if row["days_since"] > 7:
            signals.append(f"last login {int(row['days_since'])} days ago")
        return signals

    top = df.nlargest(limit, "score")

    results = []
    for _, row in top.iterrows():
        results.append({
            "account_id":    str(row["account_id"]),
            "account_name":  str(row.get("account_name", row["account_id"])),
            "industry":      str(row["industry"]),
            "country":       str(row.get("country", "")),
            "sub_plan":      str(row["sub_plan"]) if pd.notna(row["sub_plan"]) else "unknown",
            "seats":         int(row["sub_seats"]) if pd.notna(row["sub_seats"]) else 0,
            "mrr":           round(float(row["mrr_amount"]), 2) if pd.notna(row["mrr_amount"]) else 0.0,
            "risk_score":    int(min(row["score"], 100)),
            "tenure_days":   int(row["tenure_days"]),
            "days_since_last_login": int(row["days_since"]),
            "billing":       str(row["billing_frequency"]) if pd.notna(row["billing_frequency"]) else "unknown",
            "risk_signals":  build_signals(row),
        })

    return results


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/api/churn/top-accounts")
def top_accounts():
    limit = int(request.args.get("limit", 20))
    limit = max(1, min(limit, 50))

    scored = compute_risk_scores(limit)

    return jsonify({
        "accounts":      scored,
        "count":         len(scored),
        "generated_at":  datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_scored":  int(accounts_df[accounts_df["churn_flag"] == False].shape[0]),
        "model_version": "rule-based-v1",
    })


@app.route("/health")
def health():
    return jsonify({
        "status":           "ok",
        "accounts_loaded":  int(len(accounts_df)),
        "active_accounts":  int(accounts_df[accounts_df["churn_flag"] == False].shape[0]),
    })


if __name__ == "__main__":
    print(f"Scoring API running → http://localhost:{PORT}")
    print(f"  GET /api/churn/top-accounts?limit=20")
    print(f"  GET /health")
    app.run(host="0.0.0.0", port=PORT, debug=os.getenv("DEBUG", "false").lower() == "true")
