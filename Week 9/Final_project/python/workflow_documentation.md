# n8n Workflow: Weekly Churn Risk Digest

Sends a ranked list of at-risk accounts to Slack every Monday morning, with a plain-English explanation for each account written by Claude.

---

## What it does

```
Every Monday 8AM
    → GET /api/churn/top-accounts?limit=20   (Python scoring API)
    → IF count > 0
        YES → Build prompt → POST Anthropic API → Format Slack blocks → POST Slack webhook
        NO  → POST "all clear" to Slack
```

Each account in the digest gets:
- Company name, plan, seats, MRR
- Risk score out of 100 with a visual bar (🔴 / 🟡 / 🟢)
- One plain-English sentence from Claude explaining what the signal means and what to do

The CS team reacts with ✅ ⏭️ or comments in thread. No dashboard required.

---

## Files

| File | Purpose |
|---|---|
| `churn_digest_workflow.json` | Import this into n8n |
| `scoring_api.py` | Run this to serve the scoring endpoint |

---

## Setup

### Step 1: Start the scoring API

The API loads the Ravenstack CSV files and scores every active account at request time.

```bash
# Install dependencies
pip install flask pandas numpy

# Point DATA_DIR at the folder containing the 5 Ravenstack CSV files
DATA_DIR=/path/to/ravenstack/data python3 scoring_api.py
```

The API runs on port 5678 by default. Test it:

```bash
curl http://localhost:5678/health
curl "http://localhost:5678/api/churn/top-accounts?limit=3"
```

### Step 2: Create a Slack Incoming Webhook

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → Create an app → From scratch
2. Add feature: Incoming Webhooks → Activate
3. Click "Add New Webhook to Workspace" → pick the `#customer-success` channel
4. Copy the webhook URL (starts with `https://hooks.slack.com/services/...`)

### Step 3: Set environment variables in n8n

In your n8n instance, go to **Settings → Environment Variables** and add:

| Variable | Value |
|---|---|
| `SCORING_API_URL` | `http://localhost:5678` (or your deployed API URL) |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `SLACK_WEBHOOK_URL` | The webhook URL from Step 2 |

### Step 4: Import the workflow

1. In n8n, click the **+** button → **Import from file**
2. Select `churn_digest_workflow.json`
3. The workflow imports as inactive. Click **Activate** when ready.

### Step 5: Test it manually

Before activating on a schedule, click **Execute Workflow** manually in n8n and check Slack. If the digest arrives, activate the schedule.

---

## How the risk score is calculated

The model is rule-based (no ML in Phase 1). Every active, non-churned account is scored as follows:

| Signal | Points | Reason |
|---|---|---|
| Tenure under 30 days | +40 | Highest churn concentration — 53% of churn in first 90 days |
| Tenure 30–90 days | +25 | Still within the high-risk onboarding window |
| DevTools industry | +25 | 31% lifetime churn — 2× the next-highest segment |
| Usage drop > 50% (30d vs baseline) | +15 | Weak signal but present in 18% of churned accounts |
| Usage drop 30–50% | +8 | |
| Month-to-month billing | +10 | Annual contracts churn at lower rates |
| Enterprise plan with < 5 seats | +10 | Possible mismatch between plan and actual usage |

Maximum score: 100. Accounts scoring 0 are not flagged.

---

## What to change when the ML model is ready (Phase 2)

In Phase 2, the `compute_risk_scores` function in `scoring_api.py` is replaced with a call to the trained gradient boosting or logistic regression model. The n8n workflow does not change — it still calls `GET /api/churn/top-accounts` and receives the same JSON structure. The API is the abstraction layer.

---

## Interpreting the Slack output

```
🔴 Weekly Churn Risk Digest
Monday, 8 June 2026  ·  12 accounts flagged from 390 active  ·  Model: rule-based v1
────────────────────────────────────────────────────────────
Company_321                                🔴 Score: 80/100
DevTools · Basic · $171/mo · France        ▓▓▓▓▓▓▓▓░░
  New DevTools account signed up 6 days ago with no activity in the past 5 weeks — call before Day 30.
────────────────────────────────────────────────────────────
Company_371                                🔴 Score: 80/100
DevTools · Basic · $285/mo · US            ▓▓▓▓▓▓▓▓░░
  22-day-old DevTools account with usage down 63% — may have stalled on integration.
────────────────────────────────────────────────────────────
```

**Score interpretation:**
- 🔴 65+ — Call this week
- 🟡 40–64 — Monitor; reach out if no change next week
- 🟢 Below 40 — Low priority

---

## Troubleshooting

**The workflow runs but Slack gets nothing.** Check that `SLACK_WEBHOOK_URL` is set in n8n environment variables and that the webhook is connected to the right channel.

**The scoring API returns an empty accounts list.** Check that `DATA_DIR` points to the folder with all 5 CSV files and that none of the files have been renamed.

**The Anthropic call times out.** The default timeout is 30 seconds. If Claude is slow, increase `timeout` in the "Generate Alert Text" node options.

**n8n shows "SCORING_API_URL is not defined".** Environment variables in n8n are accessed via `$env.VAR_NAME`. Make sure the variable name matches exactly, including capitalisation.

**The `$('Build LLM Prompt')` reference fails in the Slack Blocks node.** This uses n8n's inter-node data access. It requires n8n 0.220 or later. If you're on an older version, add a "Set" node after "Build LLM Prompt" that stores the accounts data, and reference that node instead.
