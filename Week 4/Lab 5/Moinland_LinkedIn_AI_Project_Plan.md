# Moinland LinkedIn AI Content Creator — Project Plan

> **One-liner:** Transform coaching session transcripts into 6–10 thought-leadership LinkedIn posts per month — automatically, on-brand, ready to approve in Notion.

---

## 1. Use Case

**Problem:** Moinland's CEO and CRO are expert startup coaches with genuine insight to share. LinkedIn is their highest-value channel to reach tech founders and nurture new clients. But they have no time to sit down and write consistently.

**Solution:** An AI pipeline that mines their own coaching transcripts for insights, extracts the best topics, writes LinkedIn posts in their voice, and drops polished drafts into Notion for a quick human review before publishing.

**Target users:** CEO & CRO of Moinland (approvers, not writers)  
**Target audience:** Tech startup founders and early-stage CEOs  
**Output goal:** 6–10 "aha moment" LinkedIn posts per month

### How it works — end to end

```
Coaching transcript (.txt)
        ↓
Extract top 5 topics  [LLM + trending signal]
        ↓
CEO/CRO picks 3 topics  [< 2 min human step]
        ↓
Generate content brief per topic  [chain-of-thought prompt]
        ↓
Write 3 LinkedIn post drafts  [few-shot + brand voice]
        ↓
Save to Notion Content Calendar  [status: Draft for Review]
        ↓
Human reviews, edits, publishes
```

---

## 2. Technology Stack

| Layer | Tool | Why |
|---|---|---|
| **Orchestration** | N8N (self-hosted) | Already in stack; visual builder; no-code maintainable; free tier |
| **Knowledge base & output** | Notion | Already used by team; API available; drafts land where they work |
| **LLM** | GPT-4o / Claude Sonnet | GPT-4o for instruction-following; Claude for reasoning. A/B test in Phase 2 |
| **Trending signals** | Tavily or Perplexity API | Lightweight search API to ground posts in real market context; < $2/month |
| **Document input** | .txt upload + Notion pages | Transcripts uploaded directly; brand docs live in Notion |
| **Publishing** | Manual (MVP) | Human clicks publish — non-negotiable for brand safety at this stage |

**Design principle:** No new platforms. N8N + Notion are already the team's tools. The LLM is the only net-new dependency.

---

## 3. MVP Scope

### In scope
- N8N workflow: transcript → topic extraction → topic selection → brief → 3 post drafts → Notion
- Notion knowledge base: brand voice doc, 10 example posts (few-shot library), 3 signature coaching frameworks
- Trending topic injection via search API
- Notion Content Calendar DB with draft status + rating field
- Slack or email notification when drafts are ready

### Out of scope (MVP)
- LinkedIn API auto-publishing
- Image or carousel generation
- Multi-language support
- Performance analytics feedback loop

### MVP success gate
> 3 posts published within 4 weeks of launch, rated **≥ 7/10** by CEO or CRO — requiring only light editing before approval.

---

## 4. Risk Assessment

| Risk | Level | Mitigation |
|---|---|---|
| AI output doesn't sound like the coaches | 🔴 High | Rich few-shot library (10+ real posts); explicit voice rules in system prompt; mandatory human edit |
| Transcript quality too low (unclear audio, jargon) | 🟡 Medium | Pre-processing/summary step before LLM ingestion; minimum length threshold |
| Topics feel generic, miss the ICP | 🟡 Medium | Trending signal injection; ICP definition in system prompt; human confirms topics before generation |
| Coaches don't review drafts consistently | 🟡 Medium | Slack/email notification; Notion review view designed for < 5 min; auto-reminder after 5 days |
| N8N breaks on Notion API changes | 🟢 Low | Pin API version; error-handling nodes; weekly health check |
| LLM costs exceed budget | 🟢 Low | Cheap model for extraction; full model only for final drafts. Estimated < $5/month |

---

## 5. Implementation Plan

### Phase 1 — Foundation (Week 1–2)
- Set up Notion: Knowledge Base DB + Content Calendar DB
- Write brand voice document (tone, vocabulary, forbidden phrases)
- Curate 10 example posts for few-shot library
- Document 3–5 Moinland coaching frameworks
- Define ICP: who reads this, what triggers an "aha" moment
- Connect N8N ↔ Notion integration

### Phase 2 — Build MVP (Week 3–4)
- Build 6-node N8N workflow:
  1. **Ingest** — .txt upload or Notion page URL trigger
  2. **Document** — fetch brand voice + examples from Notion KB
  3. **Monitor** — LLM extracts 5 topics; search API injects trending signals
  4. **Select** — CEO/CRO picks 3 topics via Notion or N8N form
  5. **Brief + Publish** — chain-of-thought brief → few-shot post (3 LLM calls)
  6. **Output** — write 3 drafts to Notion DB with metadata
- Set up Slack/email notification

### Phase 3 — Quality Loop (Week 5–6)
- Run pipeline on 2 real transcripts; collect CEO/CRO ratings and edit notes
- Fix top 3 failure modes in prompt templates
- Add "refine with instruction" step (one-line edit triggers regeneration)
- A/B test GPT-4o vs Claude on same transcript; pick primary model

### Phase 4 — Operationalise (Week 7–8)
- Write SOP: upload → review → publish
- Schedule biweekly pipeline runs
- Publish first 6 posts; record baseline engagement

### Phase 5 — Scale (Month 3+)
- LinkedIn API for auto-draft creation (human still publishes)
- Ingest engagement data back to Notion
- Generate 2 hook variants per topic for A/B testing
- Expand KB with market research (VC reports, founder surveys)

---

## 6. Success Metrics

### Operational
| Metric | Target |
|---|---|
| Posts published per month | 6–10 |
| Draft approval rate | > 80% approved with minor edits |
| Time: transcript → Notion drafts | < 15 minutes |
| Human editing time per post | < 10 minutes |
| Voice quality score (CEO/CRO rating) | ≥ 7 / 10 average |

### Business impact (by Month 3)
| Metric | Target |
|---|---|
| LinkedIn impressions | +30% growth |
| Profile visits from posts | > 100 / month |
| Inbound coaching enquiries from LinkedIn | +2 leads / month |
| Follower growth | +50 net new / month |

### Qualitative signal
> At least **2 posts per month** generate meaningful comments from tech founders or startup CEOs — not just likes. Comments expressing a mindset shift or direct resonance are the primary signal the content is hitting the right nerve.

---

*Reference architecture: [FitByte AI Content Creator](https://github.com/maxxeagleowl/ai-content-creator) — May 2026*
