# Autonomous Agent Project Plan
## FitByte Lead Qualification Agent

---

## 1. Use Case

### Problem Statement
FitByte is launching a social media campaign targeting fitness enthusiasts. Currently, leads who respond to ads have no automated way to be screened and routed to the appropriate sales team. A human would need to manually assess each lead's fitness goals and forward them — introducing delay, inconsistency, and missed opportunities.

### Solution
A Telegram bot that acts as an AI-powered lead qualification agent. When a user clicks the campaign CTA, the bot opens a conversation, asks 3 targeted questions about their fitness goals, collects their contact info, and automatically routes them to the correct Notion database (sales team table) based on the product match:

- **Fitness Watch** → Watch Sales Team
- **Fitness Ring** → Ring Sales Team
- **Chest Band (Pro)** → Chestband Sales Team

### Target Users
- **End users (leads):** Fitness enthusiasts who respond to FitByte's social media ads
- **Internal users:** Sales team members who receive qualified leads in Notion

### Success Criteria
- Bot completes qualification in under 2 minutes per lead
- ≥ 85% of leads are routed to the correct product team
- Zero leads lost due to routing errors
- Lead data (name, email, answers) stored correctly in Notion
- Sales team receives leads within 60 seconds of conversation completion

### Current Process (Manual)
1. User sees ad, clicks link, lands on a contact form
2. Sales rep manually reviews form submission
3. Rep emails or calls lead to ask qualification questions
4. Rep forwards lead to appropriate product team
5. Average time from submission to routing: 24–48 hours

---

## 2. Technology Stack

### Selected Technologies

| Layer | Technology | Justification |
|---|---|---|
| Bot Interface | **Telegram Bot API** | Native mobile UX, free, widely used by fitness communities; no app install required |
| Orchestration | **n8n** | Visual workflow builder; native Telegram + Notion nodes; easy scheduling and error handling |
| AI Qualification | **OpenAI GPT-4o-mini** | Fast, cost-effective for short conversation flows; strong instruction-following |
| Lead Storage | **Notion API** | Structured databases; FitByte sales teams likely already use Notion |
| Memory/State | **n8n workflow state** | Session tracking within conversation flow; lightweight for this use case |

### Why NOT LangChain/LangGraph?
This use case is a **structured, deterministic conversation flow** — not an open-ended agent requiring tool-calling loops or complex reasoning. n8n's visual workflow with branching logic handles this more reliably and with less overhead than a full LangGraph state machine. RAG is also not needed since the bot doesn't query a knowledge base — it collects data.

### Why NOT RAG?
The bot is asking questions and collecting answers, not retrieving knowledge. A simple classification prompt at the end of the conversation suffices to route leads.

### Alternatives Considered
- **WhatsApp Business API** — Higher setup cost, approval required
- **Custom web chat** — Higher development cost, lower mobile reach
- **LangGraph** — Overpowered for a 3-question deterministic flow
- **Airtable** — Notion preferred by FitByte teams

---

## 3. MVP Scope

### Brainstormed Feature List (All Possible)
- 3-question Telegram qualification flow
- AI-powered product classification
- Notion routing to 3 team tables
- Name + email collection
- Input validation (email format check)
- Conversation retry on invalid input
- Multi-language support (DE, EN, ES)
- CRM integration (Salesforce, HubSpot)
- Lead scoring (1–10)
- Sales rep Slack notifications
- Analytics dashboard
- Duplicate lead detection
- Follow-up scheduling
- A/B testing question variants
- Opt-in/opt-out management
- GDPR consent checkbox

### MVP (v1) — Must Have
- ✅ 3 qualifying questions about fitness goals
- ✅ Name and email collection
- ✅ AI classification into Watch / Ring / Chestband
- ✅ Automatic routing to 3 Notion tables
- ✅ English language only
- ✅ Basic error handling (retry on invalid email)
- ✅ Timestamp and source tagging in Notion

### v2 — Should Have
- Email format validation with retry
- Duplicate detection (check existing Notion records)
- Slack notification to sales rep when lead arrives
- Lead scoring (0–10 based on engagement quality)

### v3+ — Nice to Have
- Multi-language (DE, ES, FR)
- CRM sync (HubSpot/Salesforce)
- Analytics dashboard (Metabase or Notion charts)
- A/B question variant testing
- GDPR consent flow

### MVP Success Metrics
| Metric | Target |
|---|---|
| Conversation completion rate | ≥ 70% of started conversations |
| Routing accuracy | ≥ 85% correct team assignment |
| Lead-to-Notion latency | < 60 seconds |
| Bot uptime | ≥ 99% |
| Cost per lead | < €0.05 (LLM call cost) |

---

## 4. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **User drops off mid-conversation** | High | Medium | Keep questions short and engaging; add progress indicator ("Question 1 of 3") |
| **LLM misclassifies product** | Medium | High | Use few-shot examples in system prompt; add confidence threshold; default to human review on ambiguity |
| **Telegram bot goes offline** | Low | High | n8n hosted on reliable cloud (Railway/Render); set up uptime monitor (UptimeRobot) |
| **Notion API rate limits** | Low | Medium | n8n retries on failure; Notion free tier allows 3 req/sec — more than enough for campaign scale |
| **Spam/bot submissions** | Medium | Medium | Add CAPTCHA-style challenge or rate limit per Telegram user ID |
| **Invalid email collected** | High | Low | Regex validation with friendly retry prompt |
| **GDPR compliance gap** | Medium | High | Add explicit consent message before email collection; log consent timestamp in Notion |
| **Campaign surge overloads bot** | Low | High | n8n handles concurrent workflows; stress test before launch |
| **Scope creep from sales team** | Medium | Medium | Lock MVP features; use v2 backlog for new requests |

---

## 5. Implementation Plan

### Phase 1: Setup & Configuration (Days 1–2)
- [ ] Create Telegram bot via @BotFather, get API token
- [ ] Set up n8n instance (cloud or self-hosted)
- [ ] Create 3 Notion databases (Watch / Ring / Chestband Sales Teams) with schema:
  - Name, Email, Goal Answer 1, Goal Answer 2, Goal Answer 3, Product Match, Timestamp, Source
- [ ] Configure n8n Notion credentials
- [ ] Configure n8n Telegram credentials

### Phase 2: Bot Conversation Flow (Days 3–4)
- [ ] Build n8n Telegram trigger node
- [ ] Implement session/state tracking (using static data or a simple key-value store)
- [ ] Code the 3-question conversation flow with branching logic
- [ ] Add name and email collection steps
- [ ] Implement email validation with retry

### Phase 3: AI Classification & Routing (Day 5)
- [ ] Build OpenAI classification prompt (system prompt with product descriptions + few-shot examples)
- [ ] Parse LLM output to extract product recommendation
- [ ] Add routing logic: Switch node → 3 Notion write nodes
- [ ] Test classification accuracy with 20+ sample answer sets

### Phase 4: Testing & QA (Days 6–7)
- [ ] End-to-end testing: complete 10+ full conversations
- [ ] Verify Notion records are written correctly for all 3 routes
- [ ] Test edge cases: invalid email, one-word answers, emoji-only inputs
- [ ] Load test with simulated concurrent users
- [ ] Get sign-off from one member of each sales team

### Phase 5: Launch & Monitoring (Day 8)
- [ ] Connect bot to campaign CTA link (t.me/FitByteBotLink)
- [ ] Set up n8n error alert (email on workflow failure)
- [ ] Monitor first 50 leads manually for routing accuracy
- [ ] Document handoff for sales teams

### Timeline Summary
| Phase | Duration | Owner |
|---|---|---|
| Setup & Config | 2 days | Dev |
| Bot Flow | 2 days | Dev |
| AI Classification & Routing | 1 day | Dev |
| Testing & QA | 2 days | Dev + Sales |
| Launch | 1 day | Dev + Marketing |
| **Total** | **8 days** | |

### Resources Needed
- **Team:** 1 developer (full-stack or no-code), sales team leads for sign-off
- **Tools:** n8n (cloud ~$20/mo or self-hosted free), Telegram (free), Notion (free tier), OpenAI API (~$5 budget for MVP)
- **Budget:** ~$25–50 total for MVP phase

---

## 6. Success Metrics (Recap)

### Quantitative
- Conversation completion rate ≥ 70%
- Routing accuracy ≥ 85%
- Lead latency < 60 seconds
- Cost per lead < €0.05

### Qualitative
- Sales reps confirm lead quality is higher than manual process
- Leads report positive bot experience (no confusion, quick)
- Marketing team can launch campaign on Day 8

---

## 7. Conversation Flow Design

```
[User clicks CTA] 
      ↓
[Bot: "Hi! 👋 I'm FitByte's fitness advisor. I'll help match you to the right gear in 3 quick questions!"]
      ↓
Q1: "What's your main fitness goal?"
    → Lose weight / Build muscle / Track performance / General wellness
      ↓
Q2: "How do you prefer to track your workouts?"
    → Wrist wearable / Minimal/discreet device / Chest strap for precision
      ↓
Q3: "How seriously do you train?"
    → Casual (1-2x/week) / Regular (3-4x/week) / Athlete (5+/week or competition)
      ↓
[Bot: "Almost there! What's your name?"] → [Collect name]
      ↓
[Bot: "And your email so our team can reach you?"] → [Collect + validate email]
      ↓
[LLM classifies → Watch / Ring / Chestband]
      ↓
[Route to correct Notion table]
      ↓
[Bot: "Thanks {name}! A FitByte specialist will be in touch soon. 🏋️"]
```

### Product Classification Logic
- **Fitness Watch:** Users who want performance tracking on wrist, train regularly, goal = performance or weight loss
- **Fitness Ring:** Users who want minimal/discreet tracking, casual to regular training, general wellness
- **Chestband (Pro):** Users who train seriously (athlete level), want chest-strap precision, competition or high-performance context
