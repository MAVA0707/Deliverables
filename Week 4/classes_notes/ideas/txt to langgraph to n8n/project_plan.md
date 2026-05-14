# Autonomous Agent Project Plan
## Meeting Summary Agent

---

## 1. Use Case

### Problem Statement
After every meeting, the team has no reliable way to quickly understand what was discussed, what was decided, and what needs to happen next — without re-reading the full transcript. Summaries are either skipped or done inconsistently by hand.

### Solution
A LangGraph agent that watches for new meeting transcript files, summarizes them into three structured sections (key takeaways, topics covered, next steps), creates a formatted Notion page, and sends the team a Telegram notification with a preview and a direct link.

### Target Users
- Any team that records and transcribes meetings
- Team leads who need quick post-meeting visibility
- Members who missed the meeting and need a fast catch-up

### Success Criteria
- Summary generated within 60 seconds of transcript file drop
- Notion page created with all three sections populated
- Telegram message delivered with correct link and takeaway preview
- Consistent quality across meeting types (planning, standups, client calls)

### Current Process (Manual)
- Someone reads the transcript and writes a summary: 10–20 minutes per meeting
- Summary emailed or posted in chat — often skipped under time pressure
- No standard format; different people write different things

---

## 2. Technology Stack

| Layer | Technology | Justification |
|---|---|---|
| Agent framework | **LangGraph** | Stateful 4-node linear graph; clean separation of concerns per stage |
| LLM | **GPT-4o-mini** | Strong summarization; fast and cost-effective |
| Knowledge store | **Notion API** | Rich page with structured blocks (headings, bullets, full transcript) |
| Notifications | **Telegram Bot API** | Instant team notification; no extra app |
| Trigger | **n8n** | Watches `/transcripts/` folder; calls agent via HTTP; archives files |

### Graph Design

```
START → parse_input → generate_summary → create_notion → send_telegram → END
```

This is a linear graph — no conditional edges needed. The agent always does all four steps in sequence. This is appropriate because:
- There are no decision points (no "flag for review" branching)
- Every transcript always produces a summary, a page, and a notification
- Simplicity is a feature — easier to debug and extend

### Why LangGraph over a plain Python script?
The state object (`AgentState`) is passed through each node and accumulates results — the meeting title from `parse_input` is available in `send_telegram` without threading it manually. LangGraph also makes it trivial to add nodes later (e.g. translate summary, post to Slack) without rewriting the flow.

---

## 3. MVP Scope

### MVP (v1) — Included
- ✅ Watch folder for new `.txt` / `.md` transcript files
- ✅ Extract meeting title, date, participants from header
- ✅ Generate key takeaways (3–5 bullets)
- ✅ Generate topics covered (3–7 bullets)
- ✅ Generate next steps (3–6 bullets)
- ✅ Create Notion page with all sections + full transcript appended
- ✅ Send Telegram notification with preview and Notion link
- ✅ Archive processed transcript to `/transcripts/processed/`
- ✅ Alert team lead on failure

### v2 — Should Have
- Action item extraction (who owns what, by when) — write to a separate Notion database
- Confidence scoring: flag very short or unclear summaries for human review
- Slack notification alternative

### v3+ — Nice to Have
- Whisper integration: auto-transcribe audio/video recordings
- Multi-language support
- Summary sent as email digest

### Out of Scope (MVP)
- Audio transcription
- Action item tracking
- CRM integration
- Multi-language

---

## 4. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| LLM produces generic/vague summary | Medium | Medium | Few-shot examples in prompt; review first 10 outputs manually |
| Transcript too long for context window | Low | High | Chunk transcript into sections; summarize each, then synthesize |
| Notion API rate limit | Low | Low | One page per transcript; well under limits |
| Telegram message not delivered | Low | Medium | n8n logs failure; agent returns `telegram_sent: false` |
| Duplicate processing (file detected twice) | Low | Low | Archive file immediately after processing |
| Summary quality varies by meeting type | Medium | Medium | Tune prompt with examples from each meeting type |

---

## 5. Implementation Plan

### Phase 1: Setup (Day 1)
- Create Notion parent page to hold all meeting summaries
- Create Telegram bot via @BotFather; get team chat ID
- Set up `.env` with all credentials
- Install dependencies: `langgraph langchain-openai notion-client fastapi uvicorn python-dotenv`

### Phase 2: Agent (Days 2–3)
- Implement and test each node individually with mock LLM
- Wire graph: `parse_input → generate_summary → create_notion → send_telegram`
- Test against 5 real transcripts; refine summarization prompt
- Add dry-run mode for local testing without credentials

### Phase 3: n8n Trigger (Day 4)
- Configure Watch Folder → Read File → HTTP POST → archive + log
- Add error alert branch
- End-to-end test: drop file → Notion page appears → Telegram message received

### Phase 4: Launch (Day 5)
- Deploy FastAPI server (Railway / local)
- Activate n8n workflow
- Run for one week with real meeting transcripts; collect team feedback

### Timeline
| Phase | Duration |
|---|---|
| Setup | 1 day |
| Agent development | 2 days |
| n8n trigger | 1 day |
| Launch | 1 day |
| **Total** | **5 days** |

---

## 6. Success Metrics

| Metric | Target |
|---|---|
| Summary generation time | < 60 seconds end-to-end |
| Notion page creation success | ≥ 99% |
| Telegram delivery | ≥ 99% |
| Team adoption (summaries read) | ≥ 80% of meetings within 1 week |
| Manual summary time saved | 10–20 min per meeting |
