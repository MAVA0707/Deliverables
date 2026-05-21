# User Stories & Sprint Plan

## User Stories

---

### Agent Ian – Idea to Notion

**As a** CEO,
**I want to** send a topic idea via Telegram and get a researched LinkedIn draft saved to Notion,
**so that** I spend less time writing and more time talking to clients.

**Acceptance Criteria:**
- Telegram message triggers the workflow
- Draft includes real data points from the web
- Draft follows Moinland brand voice
- Draft is saved to Notion with status "Draft"
- I get a Telegram confirmation with the Notion link

---

### Agent Rea – Research & Analysis

**As a** CEO,
**I want to** get a weekly email with a summary of funding news and startup trends,
**so that** I always have fresh insights without reading 10 RSS feeds myself.

**Acceptance Criteria:**
- RSS feeds are read automatically every day
- Articles are stored in Pinecone vector database
- Every week an AI-written briefing is emailed to me
- I get an alert if anything fails

---

### Agent Cal – Coaching to LinkedIn

**As a** CEO,
**I want to** have my coaching session transcripts (from Granola) automatically turned into LinkedIn post drafts,
**so that** valuable conversations become content without extra work.

**Acceptance Criteria:**
- New transcript file in Google Drive triggers the workflow
- Key topics are extracted and researched
- Draft follows Moinland brand voice
- Draft is saved to Notion with status "Draft"
- I get a Telegram notification when done

---

## Sprint Plan

| Day | Task | Agent | Estimate | Depends on | Done when |
|---|---|---|---|---|---|
| Mon | Briefing document | — | S | — | Document complete |
| Mon | Build Ian prototype | Ian | M | Briefing, Notion KB set up | Workflow runs end-to-end |
| Tue | Ian: improve output quality | Ian | S | Prototype running | Output reviewed and approved |
| Tue | Ian: documentation + cost analysis | Ian | S | Output quality passed | Uploaded to GitHub |
| Tue | Build Rea prototype | Rea | M | Pinecone index created | Workflow runs end-to-end |
| Wed | Rea: improve output quality | Rea | S | Prototype running | Email received and reviewed |
| Wed | Rea: documentation + cost analysis | Rea | S | Output quality passed | Uploaded to GitHub |
| Wed | Midpoint review | — | S | Rea done | Review notes written |
| Wed | Build Cal prototype | Cal | L | Google Drive access, Pinecone | Workflow runs end-to-end |
| Thu | Cal: improve output quality | Cal | S | Prototype running | Output reviewed and approved |
| Thu | Cal: documentation + cost analysis | Cal | S | Output quality passed | Uploaded to GitHub |
| Thu | All agents: testing + samples | All | M | All prototypes done | Sample outputs in repo |
| Fri | Final testing and demo prep | All | S | All agents stable | Demo flow rehearsed |
| Fri | Presentation | — | M | Everything uploaded | Presented to class |

**Estimates:** XS = ~30 min, S = ~1–2h, M = ~3–4h, L = ~5–6h

---

## Definition of Done (general)

- Workflow runs without errors from trigger to output
- Output reviewed by a human and judged "good enough to edit"
- Error handling tested (what happens when a step fails?)
- Workflow JSON exported and uploaded to GitHub
- Documentation written
