# Documentation

## Context

Moinland is a coaching boutique for early-stage tech founders and startup CEOs. The CEO and CRO are expert coaches — but they do not have time to research and write LinkedIn content consistently. LinkedIn is their most important channel to reach new clients.

These three agents automate the research and first draft. A human still reviews and publishes.

---

## Agent Ian – Idea to Notion

### What it does

Ian takes a raw topic idea from Telegram, researches it on the web, writes a LinkedIn post draft in Moinland's brand voice, and saves it to Notion.

### Workflow (step by step)

```
Telegram message
  → Acknowledge ("Got it!")
  → Fetch Brand Voice from Notion Knowledge Base
  → Research topic (OpenAI GPT-4o-mini + Tavily web search)
     → Produces a content brief with data points and ICP-fit framing
  → Fetch Example Posts from Notion Knowledge Base
  → Write LinkedIn post (OpenAI GPT-4o-mini, following brand voice + brief)
  → Save draft to Notion (status: Draft, created date, requested by)
  → Send Telegram confirmation with Notion link
```

**Error path:** If any step fails → Error Trigger → Telegram alert to admin with error message, node name, and timestamp.

### Tools & APIs

| Tool | Used for | Auth |
|---|---|---|
| Telegram Bot | Receive idea, send confirmation | Bot Token |
| Notion | Read Knowledge Base, save draft | Integration Token |
| OpenAI GPT-4o-mini | Research brief + LinkedIn post | API Key |
| Tavily | Web search during research | API Key |

### Notion Knowledge Base Setup

You need a Notion database with a `Type` select property. Create pages with:
- `Type = Brand Voice` — paste in the brand voice guidelines
- `Type = Example Posts` — pastes strong past LinkedIn posts

### Known Limitations

- If Tavily finds no good results, the brief might be thin.
- OpenAI rate limits could cause failures on high-volume usage. Retry is set to 2 attempts.

---

## Agent Rea – Research & Analysis

### What it does

Rea reads multiple RSS feeds every day, stores articles in Pinecone, and sends a weekly AI-written email briefing about funding trends and startup news.

### Workflow (step by step)

**Daily ingestion (scheduled trigger):**
```
Schedule (daily)
  → Define RSS feed URLs
  → Split into individual feeds
  → Read each RSS feed
  → Filter out failed feeds
  → Normalize article fields
  → Embed articles (OpenAI Embeddings)
  → Store in Pinecone vector database
```

**Weekly briefing (scheduled trigger):**
```
Schedule (weekly)
  → Define topics of interest
  → AI Agent (GPT-4o-mini) queries Pinecone for relevant articles
  → Guard: check AI output is not empty
  → Convert to email-friendly HTML
  → Send email via SMTP
```

**Error alerts:** Separate email alerts for Pinecone failures, total RSS failure, and briefing failures.

### Tools & APIs

| Tool | Used for | Auth |
|---|---|---|
| RSS Feeds | News sources | None (public feeds) |
| OpenAI Embeddings | Turn articles into vectors | API Key |
| Pinecone | Store and search articles | API Key |
| OpenAI GPT-4o-mini | Write briefing | API Key |
| SMTP / Email | Send weekly briefing | SMTP credentials |

### Known Limitations

- RSS feeds must be configured manually in the workflow (Set node).
- Pinecone index must be created in advance with the right dimensions (1536 for OpenAI embeddings).
- If all feeds fail on the same day, no new articles are stored that day.
- Duplicate articles may be stored if the same item appears in multiple feeds.

---

## Agent Cal – Coaching to LinkedIn

### What it does

Cal watches a Google Drive folder for new Granola coaching session transcripts. When a new file appears, it extracts the key topics, researches them, and writes a LinkedIn draft in Moinland's brand voice — then saves it to Notion and notifies via Telegram.

### Workflow (step by step)

```
Google Drive trigger (new file in folder)
  → Download transcript file
  → Extract text from file
  → Telegram: "New session detected"
  → Normalize session fields
  → Embed session text (OpenAI Embeddings)
  → Store session in Pinecone
  → AI Agent: extract key topics from session
  → Query Pinecone for relevant past sessions (context)
  → Parse topics from JSON
  → Fetch Brand Voice from Notion
  → Fetch Example Post from Notion
  → Research topics (OpenAI + Tavily web search) → Content Brief
  → Write LinkedIn Post (OpenAI, brand voice + brief)
  → Guard: check post output is not empty
  → Save to Notion (status: Draft)
  → Telegram: success notification
```

**Error path:** Telegram alert on Google Drive error or any workflow failure.

### Tools & APIs

| Tool | Used for | Auth |
|---|---|---|
| Google Drive | Watch for new transcripts | OAuth |
| Telegram Bot | Notifications | Bot Token |
| OpenAI Embeddings | Embed session text | API Key |
| Pinecone | Store sessions, semantic search | API Key |
| OpenAI GPT-4o-mini | Topic extraction + LinkedIn post | API Key |
| Tavily | Web research | API Key |
| Notion | Brand voice, example posts, save draft | Integration Token |

### Known Limitations

- Cal only creates one LinkedIn post per session, even if a session had multiple strong topics.
- Pinecone index for Cal must be separate from Rea's index.
- Google Drive OAuth can expire and needs to be re-authorized.

---

## General Notes

### Cost Estimate (rough)

- OpenAI GPT-4o-mini is cheap (~$0.15 per 1M input tokens). Each post generation costs well under $0.01.
- Pinecone free tier (Starter) is enough for testing (30k docs, 660 document updates & 15k searches per day). Paid tier needed for large volumes.
- Tavily free tier: 1000 searches/month. Should be enough unless Ian/Cal are used very heavily.

### Testing

- All three agents were tested manually by triggering the workflows in n8n and as published workflows.
- Error handling was tested by temporarily breaking credentials and checking that alerts were sent.
- Output quality was reviewed against the Moinland brand voice guidelines.

### What could be better (backlog)

- Track costs per run using n8n execution metadata
- Cal: handle multiple topics per session and create multiple drafts
- Rea: let the CEO reply to the briefing email to trigger Ian for any interesting topic
