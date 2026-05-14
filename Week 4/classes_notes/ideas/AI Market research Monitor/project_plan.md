# AI Market Research Monitor — Autonomous Agent Project Plan

> **Use Case:** Scheduled agent that monitors a configurable topic (e.g. "AI regulation news"), searches the web daily, grades article relevance, extracts key insights, deduplicates against known content, writes a digest to Notion, and sends a Telegram notification.

---

## 1. Use Case

### Problem Statement
Staying current on fast-moving topics (competitor launches, regulatory changes, emerging research) is manual, slow, and inconsistent. Analysts spend hours per week scanning news feeds and summarising findings — work that is perfectly suited for an autonomous agent.

### Target Users
- AI/product researchers tracking a topic domain
- Strategy and competitive-intelligence teams
- Individual practitioners following a niche (e.g. "EU AI Act developments")

### Success Criteria
- Agent runs daily without manual intervention
- ≥80% of articles classified as relevant are genuinely on-topic (human spot-check)
- Zero duplicate entries in Notion across consecutive runs
- Notion page updated and Telegram message sent within 10 minutes of trigger
- Digest is readable and actionable (3–5 bullet insights per article)

### Current Manual Process
1. Analyst opens Google News / Twitter / newsletters (~15 min)
2. Reads headlines, skims body (~30 min)
3. Copy-pastes relevant content into shared doc (~15 min)
4. Writes summary and shares with team (~20 min)

**Total: ~80 min/day per topic**

---

## 2. Technology Stack

| Layer | Choice | Justification |
|---|---|---|
| **Core LLM** | OpenAI `gpt-4o-mini` (grading) + `gpt-4o` (digest) | Cost-efficient for high-volume grading; quality model for synthesis |
| **Web Search** | Tavily Search API | Structured JSON, date-filtering, 1 000 free calls/month |
| **Embeddings** | `text-embedding-3-small` (OpenAI) | Low cost, strong semantic similarity for deduplication |
| **Vector Store** | Pinecone (serverless) | Persistent across runs, scalable, metadata filtering |
| **Agent Framework** | **LangGraph** | Conditional routing (relevant/not_relevant) is native; stateful graph |
| **Orchestration** | **n8n** | Cron scheduling, Notion + Telegram native nodes, no-code glue |
| **Output** | Notion API via n8n node | Rich formatting, shareable, team-friendly |
| **Notification** | Telegram Bot API via n8n node | Instant delivery, free, easy bot setup |

### Alternatives Considered
- **LangChain ReAct agent** — simpler but lacks explicit conditional routing; harder to inspect mid-run
- **Airflow** — over-engineered for a single daily workflow; n8n is faster to iterate
- **ChromaDB** — great for local dev, no persistence between n8n cloud runs without extra infra

### Trade-offs
- Pinecone free tier is sufficient for MVP but requires an account and network call
- Tavily has a free tier; SerpAPI (~$50/month) is a paid fallback with higher reliability

---

## 3. MVP Scope

### Must-Have (MVP)
- [x] Daily cron trigger via n8n (08:00 UTC)
- [x] Web search for configurable topic (10 results per run)
- [x] LangGraph agent: fetch → grade relevance → deduplicate → extract insights
- [x] Pinecone vector store for deduplication (URL + semantic hash)
- [x] Write digest to a Notion database page
- [x] Send Telegram notification with summary stats on completion
- [x] Error handling: failed runs notify via Telegram with error message

### Should-Have (v2)
- [ ] Multi-topic support (parameterised agent)
- [ ] Configurable search depth and date range
- [ ] Human feedback loop feeding back into relevance prompt
- [ ] Weekly digest rollup email

### Nice-to-Have (v3+)
- [ ] Slack integration alongside Telegram
- [ ] Trend dashboard across weeks
- [ ] Auto-tagging articles by sub-topic
- [ ] Entity extraction for competitor mentions

### Success Metrics (MVP)
| Metric | Target |
|---|---|
| Relevance precision | ≥ 80% |
| Duplicate rate | 0% |
| Agent run time | < 5 minutes |
| Notion update success rate | ≥ 99% |
| Telegram delivery rate | ≥ 99% |

---

## 4. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **LLM hallucination in insight extraction** | Medium | High | Prompt: "extract only facts stated in article"; include source URL |
| **Search API rate limits / downtime** | Low | High | Retry logic (3 attempts, exponential backoff); fallback to secondary API |
| **Pinecone connection failure** | Low | Medium | Skip dedup, log warning; don't block run |
| **Notion API auth expiry** | Medium | Medium | n8n credential management; monitor Notion status page |
| **Telegram bot blocked** | Low | Low | Fallback: log to n8n execution history; email alert |
| **High OpenAI costs from long articles** | Medium | Medium | Truncate article text to 2 000 tokens before LLM call; cache embeddings |
| **Scope creep on topics monitored** | High | Medium | MVP: single topic only; v2 expansion explicitly gated |
| **Irrelevant results poisoning digest** | Medium | High | Relevance grading node filters aggressively; threshold tunable per topic |

---

## 5. Implementation Plan

### Phase 1 — Setup & Infrastructure (Days 1–2)
- [ ] Create Pinecone index (`market-research-seen`, 1536 dims, cosine metric)
- [ ] Set up Notion database: Title, URL, Date, Insights, Relevance Score, Run Date
- [ ] Create Telegram bot via BotFather, obtain chat ID
- [ ] Configure n8n credentials: OpenAI, Pinecone, Notion, Telegram, Tavily
- [ ] Test each credential with a simple n8n node

### Phase 2 — LangGraph Agent (Days 3–5)
- [ ] Implement `AgentState` TypedDict with all shared fields
- [ ] `search_web` node: Tavily API → list of {url, title, snippet}
- [ ] `fetch_article` node: scrape full text, truncate to 2 000 tokens
- [ ] `grade_relevance` node: LLM binary + confidence score
- [ ] `check_duplicate` node: embed URL+title, query Pinecone (threshold 0.95)
- [ ] `extract_insights` node: LLM → 3–5 bullet points
- [ ] `store_seen` node: upsert embedding to Pinecone
- [ ] `compile_digest` node: aggregate insights into markdown
- [ ] Wire conditional edges (see architecture below)
- [ ] Local end-to-end test with 5 hardcoded URLs

### Phase 3 — n8n Workflow (Days 6–7)
- [ ] Cron trigger node (daily 08:00 UTC)
- [ ] HTTP Request node → invoke LangGraph agent endpoint
- [ ] Notion node → create/update digest page
- [ ] Telegram node → send success message (article count + top headline)
- [ ] Error branch → Telegram error alert with execution ID

### Phase 4 — Testing & Tuning (Days 8–9)
- [ ] Run 3 consecutive daily runs on topic "AI regulation news"
- [ ] Spot-check relevance grades (target ≥ 80% precision)
- [ ] Verify zero duplicates across runs
- [ ] Tune relevance prompt if precision < 80%
- [ ] Load test with 20 articles per run

### Phase 5 — Deployment & Monitoring (Day 10)
- [ ] Deploy n8n to cloud (n8n.cloud or Railway)
- [ ] Set up execution history alerts
- [ ] Document runbook: change topic, clear Pinecone index
- [ ] Handoff to end user

### Timeline Summary
| Phase | Duration | Milestone |
|---|---|---|
| Setup | 2 days | All credentials working |
| LangGraph Agent | 3 days | Agent runs locally end-to-end |
| n8n Workflow | 2 days | Full pipeline automated |
| Testing & Tuning | 2 days | Precision ≥ 80%, zero dupes |
| Deployment | 1 day | Running in production |
| **Total** | **10 days** | **MVP live** |

---

## 6. Resources Needed

### Team
| Role | Effort |
|---|---|
| AI Engineer (LangGraph + RAG) | 6 days |
| Workflow Automation (n8n) | 3 days |
| QA / Prompt Tuning | 1 day |

### Services & Costs (Monthly, MVP)
| Service | Cost |
|---|---|
| OpenAI API (gpt-4o-mini + gpt-4o) | ~$10–30 |
| Pinecone Serverless | Free tier |
| Tavily Search API | Free tier (1 000 calls) |
| n8n Cloud Starter | $20 |
| Notion | Free |
| Telegram | Free |
| **Total** | **~$30–50/month** |

---

## 7. LangGraph Agent — Architecture

```
START
  │
  ▼
[search_web]          # Tavily: fetch 10 results for topic
  │
  ▼
[fetch_article]       # Scrape full text, truncate to 2000 tokens
  │
  ▼
[grade_relevance]     # LLM: binary relevant/not_relevant + score
  │
  ├── not_relevant ──► [log_skip] ──► loop to next article
  │
  └── relevant
        │
        ▼
      [check_duplicate]    # Embed URL+title → Pinecone similarity query
        │
        ├── duplicate ──► [log_skip] ──► loop to next article
        │
        └── new
              │
              ▼
            [extract_insights]    # LLM: 3-5 bullet points from article
              │
              ▼
            [store_seen]          # Upsert embedding to Pinecone
              │
              ▼
            [add_to_digest]       # Append to shared digest state
              │
              ▼  (after all articles)
            [compile_digest]      # Format final markdown digest
              │
              ▼
             END → return digest to n8n
```

### State Schema
```python
class AgentState(TypedDict):
    topic: str
    search_results: List[Dict]     # [{url, title, snippet}]
    current_article: Dict          # article being processed
    full_text: str                 # scraped body
    relevance: str                 # "relevant" | "not_relevant"
    relevance_score: float
    is_duplicate: bool
    insights: List[str]            # bullet points for current article
    digest_items: List[Dict]       # accumulated across all articles
    final_digest: str              # final markdown output
    stats: Dict                    # {searched, relevant, new, skipped_irrelevant, skipped_duplicate}
```
