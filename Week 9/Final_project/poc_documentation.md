# POC Documentation: Ravenstack Weekly Churn Risk Digest

Markus von Aschoff · markus@vonaschoff.de · June 2026

This document describes the proof-of-concept built for the Ravenstack churn-prediction use case: what it is, how the workflow runs end to end, and exactly how the scoring works.

---

## 1. What the POC does

Every Monday morning, the system scores all 390 active Ravenstack accounts for churn risk, has Claude write a one-sentence explanation for each of the top 20, and posts a ranked digest to the customer success team's Slack channel. The team reads it in a few minutes and decides who to call.

The whole thing runs as a single n8n workflow. There is no separate server, no database, and no dependency on anyone's laptop. The workflow fetches its data from URLs, scores it inside n8n, calls the Anthropic API, and posts to Slack.

**AI capability demonstrated:** the system pairs a deterministic scoring model (which ranks accounts) with a generative model (Claude, which turns each score into plain-English advice a non-technical manager can act on). The scoring decides *who* is at risk; the LLM explains *why* and *what to do*.

---

## 2. Tools used and why

| Tool | Role | Why |
|---|---|---|
| n8n | Orchestration and scoring | Runs the schedule, fetches the data, scores it in a Code node, calls Claude, posts to Slack. Self-hosted is free. The whole flow imports from one JSON file. |
| n8n Code node (JavaScript) | The scoring model | The scoring logic lives inside n8n, so there is no external API to host or keep running. This is what makes the workflow self-contained. |
| Anthropic API (Claude) | Explanation generation | One API call per weekly run turns the top 20 scored accounts into 20 plain-English sentences. Cost is roughly $0.10 to $0.30 per run. |
| Slack Incoming Webhook | Delivery | The digest lands in the team's existing #customer-success channel. A webhook needs no OAuth or bot setup — just a URL. |

The model used for the explanations is `claude-sonnet-4-6`, set in the body of the Anthropic request. The `anthropic-version` header is `2023-06-01` (the API version, not the model date).

---

## 3. The workflow, node by node

The workflow has 11 nodes in a single line with one branch at the end.

```
Every Monday 8 AM  (schedule trigger)
  -> Fetch Accounts        (HTTP GET, CSV as text)
  -> Fetch Subscriptions   (HTTP GET, CSV as text)
  -> Fetch Usage           (HTTP GET, CSV as text; continues on failure)
  -> Score Accounts        (Code node: parse, join, score, return top 20)
  -> Any Accounts Flagged?  (IF: count > 0)
        true  -> Build LLM Prompt   (Code node)
              -> Generate Alert Text (HTTP POST to Anthropic)
              -> Build Slack Blocks  (Code node)
              -> Post Digest to Slack (HTTP POST to webhook)
        false -> Post All-Clear to Slack (HTTP POST to webhook)
```

**1. Every Monday 8 AM** — a schedule trigger with the cron expression `0 8 * * 1`. It starts the run at 08:00 every Monday.

**2-4. Fetch Accounts / Fetch Subscriptions / Fetch Usage** — three HTTP Request nodes that download the CSV files from their public URLs (the Ravenstack GitHub repo's raw URLs). Each is set to return the response as text. They run in sequence so the next node can read all three. The Fetch Usage node has *continue on fail* turned on, because it pulls the largest file (25,000 rows) and the workflow should still run if that file is slow or unavailable.

**5. Score Accounts** — the heart of the POC. A Code node that parses the three CSVs, joins them, scores every active account, and returns the top 20. Detailed in Section 4.

**6. Any Accounts Flagged?** — an IF node checking whether the score node returned any accounts (`count > 0`). On a normal week this is true. The false branch exists so the team still hears from the workflow on a quiet week.

**7. Build LLM Prompt** — a Code node that formats the 20 accounts into a single prompt for Claude. It lists each account with its score and risk signals, and instructs Claude to write one sentence per account (max 20 words), numbered to match. It builds the full Anthropic request body (`model`, `max_tokens`, `messages`) and passes it downstream.

**8. Generate Alert Text** — an HTTP POST to `https://api.anthropic.com/v1/messages`. Headers: `x-api-key` (your key) and `anthropic-version: 2023-06-01`. The body is the JSON payload built in the previous node. Claude returns a numbered list of 20 sentences.

**9. Build Slack Blocks** — a Code node that reads Claude's response and the account list, then assembles Slack Block Kit blocks. Each account becomes a single section block (a coloured status dot, the account name and score, the plan and seat details, and Claude's sentence). One block per account keeps the message within Slack's 50-block-per-message limit; with the top 20 the digest is 25 blocks. A defensive trim caps it at 50.

**10. Post Digest to Slack** — an HTTP POST of the blocks to the Slack Incoming Webhook. Authentication is None; the webhook URL is the only credential. The digest appears in #customer-success within seconds.

**11. Post All-Clear to Slack** — the false branch. A short text message to the same webhook so the team knows the workflow ran even when nothing was flagged.

---

## 4. How the scoring works

All of the scoring lives in the **Score Accounts** Code node. It is a rule-based model (Phase 1), chosen because the data audit showed the strongest churn signals are simple and explainable, and because a model that shows its reasoning addresses the CEO's concern about AI being a black box.

### 4.1 Reading the data

The node reads the three CSV files from the upstream Fetch nodes. A small built-in CSV parser handles quoted fields and Windows line endings, turning each file into an array of row objects keyed by column name. No external CSV library is needed.

### 4.2 The reference date

Tenure and usage windows are measured against a reference date. Because the demo dataset ends in December 2024, the node anchors "today" to the end of the data:

```javascript
const TODAY = new Date('2024-12-31T00:00:00Z');
```

With live production data this single line changes to `const TODAY = new Date();`. It is clearly commented near the top of the node.

### 4.3 Preparing the inputs

Before scoring, the node builds three things:

- **Latest active subscription per account.** It walks the subscriptions, ignores any with an end date (those are cancelled), and keeps the most recent remaining one per account. This gives each account its current plan, seat count, MRR, and billing frequency.
- **Usage aggregates (if the usage file loaded).** It sums each account's feature-usage counts over the last 30 days and the last 90 days relative to the reference date, and records the most recent usage date. These power the usage-drop and last-login signals.
- **A churn filter.** Accounts already flagged as churned are skipped; only active accounts are scored.

### 4.4 The scoring rubric

Each active account starts at 0 and accumulates points. The weights come directly from the data audit — the size of each weight reflects how strongly that signal separated churned from retained accounts.

| Signal | Points | Why it carries this weight |
|---|---|---|
| Tenure under 30 days | +40 | The strongest signal. 53% of churn happens in the first 90 days; the first month is the most fragile. |
| Tenure 30 to 90 days | +25 | Still inside the high-risk onboarding window, but past the riskiest stretch. |
| Industry is DevTools | +25 | DevTools churns at 31% in the data, about twice the lowest segment. |
| Usage dropped over 50% (last 30 days vs prior baseline) | +15 | A weak signal in this data (only 18% of churned accounts showed it), so it is weighted modestly. |
| Usage dropped 30 to 50% | +8 | A softer version of the same signal. |
| Month-to-month billing | +10 | Annual contracts churn less; monthly contracts have no commitment holding them. |
| Enterprise plan with fewer than 5 seats | +10 | A possible mismatch between plan and actual team size, suggesting buyer's remorse. |

The maximum score is capped at 100. As each rule fires, it also appends a plain-English signal string (for example, "new account — 22 days old" or "product usage down 63% versus the prior period") so the downstream LLM and the CS team can see exactly why an account was flagged.

### 4.5 Ranking and output

Accounts scoring 0 are dropped. The rest are sorted by score, highest first, and the top 20 are returned. The node outputs a JSON object containing the account list (each with name, industry, plan, seats, MRR, score, tenure, and its signal list), the total number of accounts scored, the generation timestamp, the model version, and a flag indicating whether usage data was part of that week's scoring.

### 4.6 Worked example

```
Input account (from the CSVs):
  Company_321 · DevTools · Basic plan · monthly billing · signed up 6 days ago · usage down

Scoring:
  tenure 6 days (< 30)          +40
  industry = DevTools           +25
  usage drop > 50%              +15
  ----------------------------------
  total                         80 / 100

LLM turns it into:
  "Six-day-old DevTools account with no recent activity — call before the
   30-day mark or this account likely churns."
```

### 4.7 Resilience

If the usage file fails to load, the node detects it (`usageAvailable` is false), scores on the remaining signals (tenure, industry, billing, seats), and drops the usage and last-login signal lines rather than showing misleading values. The digest still goes out. This was verified by running the node with the usage input removed: it still scored all 390 accounts and returned a valid top 20.

---

## 5. What the POC proves, and what it does not

**It proves:**

- The data can be scored, explained, and delivered end to end with no manual work.
- The scoring runs on a schedule with no infrastructure beyond n8n.
- The LLM reliably turns scores into readable, account-specific advice.
- The pipeline shows its work: every alert lists the signals behind it.

**It does not prove:**

- That the alerts actually reduce churn. That requires the pilot's control group, measured over 8 weeks.
- That the rule-based model is the best model. Phase 2 tests an ML model against it.
- Anything about live data. The POC runs on the static 2023-2024 dataset with a fixed reference date.

**What a production version would add:**

- A control group and outcome tracking, written back to the CRM.
- A feedback loop that reads the team's Slack reactions to improve the model.
- CRM integration so each alert routes to the account's owner.
- The Phase 2 ML model in place of (or alongside) the rules, if it earns its place.

---

## 6. How to reproduce it

You need an n8n instance (cloud or self-hosted), an Anthropic API key, and a Slack workspace.

1. **Confirm the data URLs resolve.** Paste the accounts CSV URL into a browser; you should see CSV text. The three Fetch nodes already point at the Ravenstack repo's raw URLs.
2. **Create a Slack Incoming Webhook** (api.slack.com/apps -> Incoming Webhooks) for your #customer-success channel and copy the URL.
3. **Get an Anthropic API key** from console.anthropic.com.
4. **Import** `churn_digest_workflow.json` into n8n (Import from file).
5. **Paste your secrets:** the Anthropic key into the `x-api-key` header of *Generate Alert Text*, and the webhook URL into the URL field of both Slack nodes.
6. **Execute the workflow manually** and check Slack for the digest.
7. **Activate** the workflow to enable the Monday 8 AM schedule.

The companion file `workflow_documentation.md` has the full setup and troubleshooting detail.

---

## 7. Files

| File | What it is |
|---|---|
| `churn_digest_workflow.json` | The n8n workflow. Import this. |
| `workflow_documentation.md` | Full setup, configuration, and troubleshooting guide. |
| `poc_documentation.md` | This document. |
