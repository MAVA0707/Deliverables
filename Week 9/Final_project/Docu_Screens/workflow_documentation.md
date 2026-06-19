# n8n Workflow: Ravenstack — Weekly Churn Risk Digest v3

Posts a ranked list of at-risk Ravenstack accounts to Slack every Monday morning, each with a plain-English reason written by Claude.

The workflow is fully self-contained. The scoring runs inside n8n, the data is read from public URLs, and nothing depends on your local machine. It is built to run on hosted n8n (n8n Cloud) where environment variables and local APIs are not available.

---

## How it works

```
Every Monday 8AM
    -> Fetch Accounts        (GET csv from GitHub raw URL)
    -> Fetch Subscriptions   (GET csv)
    -> Fetch Usage           (GET csv; continues even if this large file fails)
    -> Score Accounts        (Code node: parse, join, score, return top 20)
    -> Any Accounts Flagged? (IF count > 0)
        YES -> Build LLM Prompt -> Generate Alert Text (Claude) -> Build Slack Blocks -> Post Digest to Slack
        NO  -> Post All-Clear to Slack
```

11 nodes. The scoring replaces the old external Python API, so there is no localhost dependency.

---

## What you must fill in after importing

The workflow imports with placeholder values in three places. Replace each one:

| Where | Placeholder | Replace with |
|---|---|---|
| Generate Alert Text node, `x-api-key` header | `YOUR_ANTHROPIC_API_KEY` | Your Anthropic API key |
| Post Digest to Slack node, URL field | `YOUR_SLACK_WEBHOOK_URL` | Your Slack webhook URL |
| Post All-Clear to Slack node, URL field | `YOUR_SLACK_WEBHOOK_URL` | The same Slack webhook URL |

There are no environment variables to set. Everything else is already configured.

---

## Setup

### Step 1: Confirm the data URLs resolve

The three Fetch nodes read the CSVs from your GitHub repo's raw URLs, already hardcoded to:

```
https://raw.githubusercontent.com/MAVA0707/Deliverables/main/Week%209/Final_project/data/
```

Before running, paste this into a browser to confirm it loads CSV text:

```
https://raw.githubusercontent.com/MAVA0707/Deliverables/main/Week%209/Final_project/data/ravenstack_accounts.csv
```

If you see the CSV, the Fetch nodes will work. If you get "404: Not Found", the branch or path is wrong (try `master` instead of `main`, and check the exact folder name). Fix the URL in all three Fetch nodes if needed. The repo must be public.

### Step 2: Create a Slack Incoming Webhook

1. Go to api.slack.com/apps -> Create an app -> From scratch
2. Left sidebar -> Incoming Webhooks -> toggle Activate to On
3. Add New Webhook to Workspace -> pick the #customer-success channel -> Allow
4. Copy the webhook URL (looks like https://hooks.slack.com/services/T.../B.../xxxx)

### Step 3: Get an Anthropic API key

From console.anthropic.com -> API Keys -> create a key. Copy it.

### Step 4: Import the workflow

1. In n8n, click + -> Import from file
2. Select churn_digest_workflow.json
3. It imports inactive.

### Step 5: Paste in your secrets

- Open Generate Alert Text. In the x-api-key header, replace YOUR_ANTHROPIC_API_KEY with your key.
- Open Post Digest to Slack. In the URL field, replace YOUR_SLACK_WEBHOOK_URL with your webhook URL.
- Open Post All-Clear to Slack. Replace YOUR_SLACK_WEBHOOK_URL with the same webhook URL.

### Step 6: Test, then activate

Click Execute Workflow. Watch the nodes turn green left to right and check #customer-success for the digest. When it works, toggle the workflow Active to enable the Monday 8AM schedule.

---

## Important: the Slack nodes use NO authentication

Both Slack nodes are plain HTTP Request nodes posting to an Incoming Webhook. The webhook URL is the only credential, and it lives in the URL field.

In each Slack node, Authentication must be set to **None**. If you see "credentials not found", a node still has Authentication pointing at a credential. Switch it to None.

Each Slack node is configured as:
- Method: POST
- Authentication: None
- Send Body: on
- Body Content Type: JSON
- Specify Body: Using JSON
- JSON: `{{ $json }}` for the digest; a fixed `{ "text": "..." }` for the all-clear

---

## Important: the reference date

The Ravenstack dataset covers January 2023 to December 2024. To produce meaningful scores on this static data, the Score Accounts node anchors "today" to the end of the data:

```javascript
const TODAY = new Date('2024-12-31T00:00:00Z');
```

Leave this as is for the demo data. With live production data, change that one line to:

```javascript
const TODAY = new Date();
```

It is near the top of the Score Accounts Code node, clearly commented.

---

## How the risk score is calculated

Rule-based model (no ML in Phase 1). Every active, non-churned account is scored:

| Signal | Points | Reason |
|---|---|---|
| Tenure under 30 days | +40 | 53% of churn happens in the first 90 days |
| Tenure 30-90 days | +25 | Still inside the high-risk onboarding window |
| DevTools industry | +25 | 31% lifetime churn, 2x the next-highest segment |
| Usage drop over 50% | +15 | Weak signal but present in 18% of churned accounts |
| Usage drop 30-50% | +8 | |
| Month-to-month billing | +10 | Annual contracts churn at lower rates |
| Enterprise plan, under 5 seats | +10 | Possible mismatch between plan and usage |

Maximum 100. Accounts scoring 0 are not flagged. The top 20 by score are returned each week.

---

## Resilience: the usage file is optional

ravenstack_feature_usage.csv is the largest file (25,000 rows). The Fetch Usage node has continueOnFail turned on. If that file is slow or unreachable, the workflow does not crash:

- Score Accounts detects the missing usage data
- It scores on the remaining signals (tenure, industry, billing, seats)
- It drops the usage-drop and last-login lines from the alerts rather than showing wrong values
- The digest still goes out

The scoring output includes a usage_signal_used flag so you can tell whether usage data was part of that week's run.

---

## The Slack message and the 50-block limit

Slack rejects any message with more than 50 Block Kit blocks (error: invalid_blocks). To stay under the cap, each account is rendered as a single section block rather than several. With the top 20 accounts the message is 25 blocks, comfortably within the limit. The Build Slack Blocks node also trims defensively to 50 blocks as a safeguard.

Each account line looks like:

```
:red_circle:  Company_388  —  85/100
Enterprise · 3 seats · $0/mo · FR
Brand-new account, 0 days old — call before the 30-day mark.
```

Score bands: red 65+ call this week, yellow 40-64 monitor, green below 40 low priority.

---

## Troubleshooting

**Fetch node 404.** The data URL is wrong. Test it in a browser. Check main vs master, the folder path, %20 for spaces, and that the repo is public.

**Generate Alert Text 400, "value string is not supported".** The body is set to raw string. It must be Body Content Type: JSON, Specify Body: Using JSON, with `{{ $json.llmPayload }}`.

**Generate Alert Text 400, "... is not a valid version".** The model name landed in the anthropic-version header. That header must be `2023-06-01`. The model string (claude-sonnet-4-6) belongs only in the body, set in the Build LLM Prompt node.

**Slack "credentials not found".** A Slack node has Authentication set to a credential. Set Authentication to None. The webhook needs no auth.

**Slack 400, "invalid_blocks".** The message exceeded 50 blocks, or a block was malformed. The current Build Slack Blocks node keeps it to 25 and trims to 50; if you raised the account limit, lower it again.

**Every account shows a huge "days old" or no recent login.** The reference date is wrong for your data. Check the TODAY line in Score Accounts.

**Anthropic call times out.** Increase the timeout in the Generate Alert Text node (default 30s).

**Workflow is slow.** Fetching and parsing the 25,000-row usage file takes a few seconds. Normal for a weekly job. If it times out on n8n Cloud's execution limit, remove the Fetch Usage node and the workflow falls back to the strong signals automatically.

---

## What changes when the ML model arrives (Phase 3)

The Score Accounts node holds the rule-based logic. In Phase 3 you can either replace that JavaScript with the trained model's output, or move scoring back to a hosted Python API (the scoring_api.py file) and have n8n call it over a real URL. Either way, the downstream half (prompt, Claude, Slack) does not change.
