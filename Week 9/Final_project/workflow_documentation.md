# n8n Workflow: Weekly Churn Risk Digest (self-contained)

Sends a ranked list of at-risk accounts to Slack every Monday morning, with a plain-English explanation for each account written by Claude.

**This version runs entirely inside n8n.** There is no external scoring API and no localhost dependency. The scoring logic lives in a Code node, and the account data is read from URLs. This is the right setup when n8n is hosted on a remote server that cannot reach your local machine.

---

## What changed from the API version

The earlier version called a Python scoring API at `http://localhost:5678`. That only works when n8n runs on the same machine as the API. When n8n is on a remote server, `localhost` points at the n8n server itself, not at your laptop, so the call fails.

This version removes that dependency entirely:

| Old (API version) | New (self-contained) |
|---|---|
| n8n calls `http://localhost:5678/api/churn/top-accounts` | n8n fetches the CSV files from URLs |
| Python Flask API does the scoring | A Code node does the scoring in JavaScript |
| Needs your laptop running the API | Needs nothing but n8n and the data URLs |

The downstream half (Claude explanation, Slack formatting, post) is unchanged.

---

## What it does

```
Every Monday 8AM
    -> Fetch accounts CSV      (HTTP, from DATA_BASE_URL)
    -> Fetch subscriptions CSV
    -> Fetch usage CSV         (continues even if this large file fails)
    -> Score Accounts          (Code node: parse, join, score top 20)
    -> IF count > 0
        YES -> Build prompt -> Claude -> Format Slack blocks -> Post digest
        NO  -> Post "all clear" to Slack
```

---

## Setup

### Step 1: Put the CSV data somewhere n8n can reach

The Code node needs three files: `ravenstack_accounts.csv`, `ravenstack_subscriptions.csv`, and `ravenstack_feature_usage.csv`.

The simplest option is your GitHub repo. GitHub serves raw file URLs that any server can fetch. For a repo at `github.com/USER/REPO` with the CSVs in a folder, the raw URL base looks like:

```
https://raw.githubusercontent.com/USER/REPO/main/path/to/folder
```

For example, if the files sit in `Week 8/Project 5`:

```
https://raw.githubusercontent.com/MAVA0707/Deliverables/main/Week%208/Project%205
```

(Spaces in the path become `%20`.)

Test a URL by pasting it plus `/ravenstack_accounts.csv` into a browser. If you see the CSV text, n8n can reach it too.

The repo must be public for raw URLs to work without authentication. If it is private, host the CSVs somewhere else n8n can reach (an S3 bucket with public read, a small web server, or a cloud storage public link).

### Step 2: Set environment variables in n8n

In n8n, go to **Settings -> Environment Variables** and add:

| Variable | Value |
|---|---|
| `DATA_BASE_URL` | The folder URL from Step 1, with no trailing slash |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `SLACK_WEBHOOK_URL` | Your Slack incoming webhook URL |

`SCORING_API_URL` is no longer needed. You can remove it.

### Step 3: Create a Slack Incoming Webhook

1. Go to api.slack.com/apps -> Create an app -> From scratch
2. Add feature: Incoming Webhooks -> Activate
3. Click "Add New Webhook to Workspace" -> pick the `#customer-success` channel
4. Copy the webhook URL into `SLACK_WEBHOOK_URL`

### Step 4: Import the workflow

1. In n8n, click **+** -> **Import from file**
2. Select `churn_digest_workflow.json`
3. It imports as inactive. Click **Activate** when ready.

### Step 5: Test it manually

Click **Execute Workflow**. Watch each node turn green. Check Slack for the digest. If it arrives, activate the schedule.

---

## The reference date (important for the demo)

The Ravenstack dataset covers January 2023 to December 2024. To produce meaningful scores, the Code node anchors "today" to the end of the data:

```javascript
const TODAY = new Date('2024-12-31T00:00:00Z');
```

If you run the workflow with this static dataset, leave this as is. **With live production data, change that line to:**

```javascript
const TODAY = new Date();
```

You will find it near the top of the "Score Accounts" Code node, clearly commented.

---

## How the risk score is calculated

The model is rule-based (no ML in Phase 1). Every active, non-churned account is scored:

| Signal | Points | Reason |
|---|---|---|
| Tenure under 30 days | +40 | Highest churn concentration: 53% of churn in first 90 days |
| Tenure 30-90 days | +25 | Still within the high-risk onboarding window |
| DevTools industry | +25 | 31% lifetime churn, 2x the next-highest segment |
| Usage drop over 50% | +15 | Weak signal but present in 18% of churned accounts |
| Usage drop 30-50% | +8 | |
| Month-to-month billing | +10 | Annual contracts churn at lower rates |
| Enterprise plan with under 5 seats | +10 | Possible mismatch between plan and usage |

Maximum score: 100. Accounts scoring 0 are not flagged.

---

## Resilience: the usage file is optional

`ravenstack_feature_usage.csv` is the largest file (25,000 rows). The "Fetch Usage" node has **continueOnFail** turned on. If that file is slow or unreachable, the workflow does not crash:

- The Code node detects the missing usage data
- It scores on the remaining signals (tenure, industry, billing, seats)
- It drops the usage-drop and last-login signals from the alerts rather than showing wrong values
- The digest still goes out

The output includes a `usage_signal_used` flag so you can tell whether usage data was part of that week's scoring.

---

## Interpreting the Slack output

```
Weekly Churn Risk Digest
Monday, 8 June 2026  -  12 accounts flagged from 390 active  -  Model: rule-based v1
------------------------------------------------------------
Company_321                                Score: 80/100
DevTools - Basic - $171/mo - France        filled-bar
  New DevTools account, 6 days old, no login in 36 days. Call before Day 30.
------------------------------------------------------------
```

**Score bands:** 65+ call this week, 40-64 monitor, below 40 low priority.

---

## Troubleshooting

**A fetch node fails with 404.** The URL is wrong. Test `DATA_BASE_URL` + `/ravenstack_accounts.csv` in a browser. Check for `%20` in place of spaces and that the repo is public.

**"Score Accounts" returns 0 accounts.** Either all fetches failed (check the fetch nodes' output) or the CSV column names do not match. The code expects the original Ravenstack column names.

**Every account shows a huge "days old" or no recent login.** The reference date is wrong for your data. Check the `TODAY` line in the Score Accounts node.

**The Anthropic call times out.** Increase the `timeout` in the "Generate Alert Text" node. Default is 30 seconds.

**Slack gets nothing.** Check `SLACK_WEBHOOK_URL` is set and the webhook still points at the right channel.

**The workflow is slow.** Fetching and parsing the 25,000-row usage file takes a few seconds. This is normal for a weekly job. If it consistently times out on n8n Cloud's execution limit, host a pre-aggregated smaller usage file, or remove the "Fetch Usage" node entirely. The workflow falls back to the strong signals automatically.
