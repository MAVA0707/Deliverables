# Moinland LinkedIn AI Content Creator — N8N Setup Guide

Import `Moinland_LinkedIn_N8N_Workflow.json` into your N8N instance and configure the steps below.

---

## 1. Prerequisites

| Credential | Where used | How to get it |
|---|---|---|
| **OpenAI API key** | Nodes 3, 5a, 5b | platform.openai.com → API keys |
| **Notion integration token** | Nodes 2a/2b/2c, 6 | notion.so/my-integrations → New integration |
| **Slack OAuth (optional)** | Final node | api.slack.com/apps → Bot Token Scopes: `chat:write` |

In N8N: **Credentials → New** → add each one. Note the credential IDs.

---

## 2. Notion Setup

### A. Knowledge Base DB

Create a Notion database called **`Moinland Knowledge Base`** with these properties:

| Property | Type | Values |
|---|---|---|
| `Name` | Title | (free text) |
| `Type` | Select | `Brand Voice`, `Example Post`, `Framework` |
| `Content` | Text / Rich text | (the actual content goes here) |

**Populate with at minimum:**
- 1 page of type **Brand Voice** — tone rules, vocabulary, forbidden phrases
- 5–10 pages of type **Example Post** — your best historical LinkedIn posts pasted in full
- 3–5 pages of type **Framework** — Moinland's signature coaching frameworks

### B. Content Calendar DB

Create a database called **`Moinland Content Calendar`** with these properties:

| Property | Type |
|---|---|
| `Name` (title) | Title |
| `Status` | Select: `Draft for Review`, `Approved`, `Published`, `Archived` |
| `Hook Angle` | Select: `contrarian`, `story`, `data`, `question` |
| `Word Count` | Number |
| `Char Count` | Number |
| `Read Time (sec)` | Number |
| `Generated At` | Date (with time) |
| `Aha Insight` | Text |
| `Post Draft` | Text |
| `Rating` | Number (1-10) — *added by reviewer* |

### C. Share both databases with your Notion integration

Open each DB → `⋯` menu → **Connections** → add your Moinland integration.

---

## 3. Replace Placeholders in the Workflow

Open the imported workflow and find/replace these placeholder strings:

| Placeholder | Replace with |
|---|---|
| `YOUR_KNOWLEDGE_BASE_DB_ID` | Notion KB database ID (from URL, the 32-char hash) |
| `YOUR_CONTENT_CALENDAR_DB_ID` | Notion Content Calendar database ID |
| `YOUR_OPENAI_CREDENTIAL_ID` | OpenAI credential ID from N8N |
| `YOUR_NOTION_CREDENTIAL_ID` | Notion credential ID from N8N |
| `YOUR_SLACK_CREDENTIAL_ID` | Slack credential ID (or delete the last node) |
| `YOUR_SLACK_CHANNEL_ID` | Slack channel ID (e.g. `C0123456789`) |

> **Tip:** instead of manual JSON edits, just open each node in the N8N editor — the credentials and DBs are dropdown-selectable once credentials are saved.

---

## 4. Workflow Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│  STAGE 1 — INGEST                                                        │
│  Form Trigger (upload .txt)  →  Extract text                             │
└──────────────────────────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│  STAGE 2 — DOCUMENT (parallel fetch from Notion KB)                      │
│   ├─ Fetch Brand Voice                                                   │
│   ├─ Fetch Example Posts          →  Merge  →  Build Knowledge Context   │
│   └─ Fetch Coaching Frameworks                                           │
└──────────────────────────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│  STAGE 3 — MONITOR                                                       │
│  OpenAI (gpt-4o-mini) — extract top 5 topics as JSON                     │
└──────────────────────────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│  STAGE 4 — SELECT (human-in-the-loop)                                    │
│  Form Trigger — CEO/CRO picks 3 of 5 topics + optional angle             │
└──────────────────────────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│  STAGE 5 — BRIEF + PUBLISH (runs 3x, once per topic)                     │
│  OpenAI (gpt-4o) — Chain-of-thought BRIEF                                │
│        ↓                                                                 │
│  OpenAI (gpt-4o) — Few-shot LinkedIn POST                                │
└──────────────────────────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│  STAGE 6 — OUTPUT                                                        │
│  Notion — create 3 draft pages in Content Calendar                       │
│  Slack — notify reviewers                                                │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Model Choices

| Stage | Model | Why |
|---|---|---|
| Topic extraction | `gpt-4o-mini` | Cheap, fast, structured JSON output. Good enough for ranking. |
| Brief generation | `gpt-4o` | Needs reasoning; cost is acceptable at 3 calls per run. |
| Post writing | `gpt-4o` | Quality matters most here. Temperature 0.75 for voice variety. |

**Estimated cost per run (3 posts):**
- 1× gpt-4o-mini call: ~$0.01
- 3× gpt-4o brief calls: ~$0.06
- 3× gpt-4o post calls: ~$0.09
- **Total: ~$0.16 per 3-post batch → ~$0.50/month** at target volume.

---

## 6. How to Run It

### First-time test
1. Activate the workflow.
2. Open the **`1. Ingest Transcript`** form URL (shown in the node panel).
3. Upload a sample .txt transcript.
4. Wait ~30s for topic extraction.
5. The **`4. Human Topic Selection`** form URL appears in the next execution — open it, pick 3 topics, submit.
6. Wait ~60s for 3 posts to generate.
7. Check the Notion Content Calendar for 3 new drafts.

### Production
- Bookmark the Stage 1 form URL.
- After each coaching session, upload the transcript.
- A Slack message lands when drafts are ready.
- Open Notion → filter by `Status = Draft for Review` → edit inline → switch to `Approved`.

---

## 7. Customisation Points

| Want to change | Edit this node |
|---|---|
| Topic extraction criteria | `3. Monitor — Extract 5 Topics` — system prompt |
| ICP definition | `Build Knowledge Context` — `icp` field |
| Brand voice fallback (when Notion KB is empty) | `Build Knowledge Context` — `brandVoice` default |
| Brief structure (add/remove fields) | `5a. Brief — Chain of Thought` — system prompt + JSON schema |
| Post style rules | `5b. Publish — Write LinkedIn Post` — system prompt |
| Post length | `5a. Brief` — `target_length_words` default |
| Temperature (creativity) | Any OpenAI node — options.temperature |

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| "Topics" field empty in Stage 4 form | Stage 3 returned malformed JSON. Check `Parse Topics` node output; lower temperature on Stage 3. |
| Notion fetch returns nothing | Did you share the DB with the integration? Is the `Type` Select property populated? |
| Posts all sound the same | Add more variety to your Example Posts in Notion. Increase temperature on Stage 5b to 0.85. |
| Posts ignore brand voice | The Build Knowledge Context node may be returning the fallback string. Check Notion KB has at least one `Brand Voice` page. |

---

## 9. Next Iterations (Post-MVP)

- **Phase 3:** Add a "Refine with instruction" sub-workflow — webhook that takes a Notion page ID + instruction, regenerates the post, updates the page.
- **Phase 4:** Schedule trigger replacing manual upload — Cron + Notion query for new transcripts.
- **Phase 5:** LinkedIn API node to auto-create drafts in LinkedIn (humans still publish).
- Add a `Rating` rollup: monthly average voice quality score in a Notion dashboard.

---

*Reference architecture: [FitByte AI Content Creator](https://github.com/maxxeagleowl/ai-content-creator) — May 2026*
