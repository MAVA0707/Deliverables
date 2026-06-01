# Green Tech Assessment — Path A
**AI Customer Support Assistant**
*Audience: CTO / Head of Engineering* 

---

## Use Case (50 words)

A B2B SaaS company handles 50,000 support tickets per month using an AI assistant currently routing every query to GPT-4o. No caching, no model tiering, synchronous calls only. The client wants to understand where their compute footprint concentrates and how to reduce it without degrading customer satisfaction (CSAT).

---

## R — One Unit of Value

> **"One unit of value for this system is: one fully resolved customer support ticket."**

Tickets are the atomic business unit the client tracks. Everything in this assessment — cost, carbon, measurement — is expressed per resolved ticket so comparisons remain apples-to-apples regardless of volume growth.

---

## Three-Row Lever Table (First 10-Minute Win)

| Lever | Current assumption (honest guess) | Better alternative to explore |
|---|---|---|
| **Model / size** | GPT-4o on 100% of tickets; no quality tiering | Route tier-1 (FAQ, billing) to GPT-4o-mini or Claude Haiku; escalate to GPT-4o only for complex/edge cases after sample eval confirms quality parity |
| **Call pattern (batch, cache, sync)** | 100% synchronous; no caching; no batching | Semantic cache for FAQ repeats (est. 25–35% hit rate); overnight batch queue for ~15% non-urgent tickets |
| **Infra / region / retention** | US-East-1 (AWS) ~400 gCO₂eq/kWh; full prompt history passed each call | Evaluate EU-West (Ireland, ~220 g) or Norway (Azure, ~20 g) for batch jobs; trim conversation history to last 3 turns |

---

## Slide-by-Slide Speaker Notes

### Title Slide
Path A — Forward-Looking Assessment. Audience is CTO / Head of Engineering. This is not a technical teardown; it's a business case with environmental integrity built in.

### Slide 1 — Hook (Why Green Software Matters Here)
Three business angles: **Cost** (GPT-4o at scale = $0.018/ticket → right-sized routing ~$0.005/ticket), **Risk** (procurement RFPs now require carbon disclosures), **Reputation** (greenwashing allegations backfire). The sustainability story is also the cost story — same actions, both outcomes.

### Slide 2 — One Unit of Value
R = one fully resolved ticket. Everything — tokens consumed, LLM calls, cost — is expressed per R. SCI = (O + M) / R; reducing calls per ticket directly lowers SCI. Keep this slide simple; stakeholders need to internalize R before the numbers land.

### Slide 3 — Assessment Defense: Hotspots
Five components in the per-ticket call chain. The GPT-4o call dominates at 100% relative weight. The system prompt (2,400 tokens avg) is the second-largest lever — visible directly from cost receipts. Skeptic challenge answered: "We have no per-request energy meter. Cost is our proxy — GPT-4o input pricing is public. At 50K tickets/mo, 2,400-token system prompt = 120M tokens/month. That is the measurable lever." Caching candidate flagged: ~30% of tickets are FAQ/billing repeats.

### Slide 4 — Assessment Defense: Assumptions
Five honest guesses with explicit unknowns. Nothing is presented as fact without a source. The right column (orange) is the validation backlog — these are the measurement sprint targets.

### Slide 5 — Pillars Map
All four GSF pillars touched:
- **Carbon**: regional routing, time-shifted batch jobs
- **Energy**: prompt trimming, model right-sizing
- **Hardware**: autoscaling, overnight batching
- **Measurement**: tokens/ticket weekly, cost as SCI proxy

### Slide 6 — Solution 1: Model Right-Sizing
Pillar: Energy · Carbon. Route by complexity. Quality gate is mandatory — 500-ticket sample eval before production cutover. API cost reduction ~65–75%; carbon reduction proportional. Haiku is ~20× cheaper per token than Opus; GPT-4o-mini is similarly positioned vs GPT-4o. Pattern: energy-proportional-computing (GSF Patterns catalog).

### Slide 7 — Solution 2: Semantic Caching
Pillar: Energy · Hardware. Embed queries, check cosine similarity > 0.92, return cached answer on hit. Cache hits have near-zero LLM cost. Expected 25–35% hit rate → 700 LLM calls per 1K tickets instead of 1,000. Embedding cost is ~1/200th of a GPT-4o call.

### Slide 8 — Solution 3: Prompt Efficiency
Pillar: Energy. System prompt audit: current 2,400 tokens contains ~35% redundant examples and ~20% stale policy boilerplate. Removing these + compressing RAG chunks → ~950 tokens avg. That is a 60% input token reduction for that component. Before/after instrumentation is a simple average of usage logs — no new tooling required.

### Slide 9 — Solution 4: Regional Routing & Batching
Pillar: Carbon · Hardware. Grid intensity varies 5–10× by region. Regional shift applies primarily to batch and eval workloads (latency constraints limit user-facing shifts). 15% of tickets are non-urgent; queueing them overnight reduces peak concurrency and enables low-carbon scheduling.

### Slide 10 — Measurement Plan
Four metrics tracked weekly for 2 weeks post-deploy:
1. Tokens/ticket < 1,200 (from 2,400)
2. LLM calls/ticket < 0.75 (25%+ cache hit)
3. Cost/ticket < $0.004 (from ~$0.018)
4. CSAT ≥ 94% (no degradation from 96%)

All are already available from existing API logs and support dashboard. Zero new instrumentation required for the first sprint.

### Slide 11 — Caveats / No Greenwashing
Four hard limits:
1. No "carbon neutral" claims — no verified methodology yet
2. Carbon offsets ≠ SCI reduction (SCI spec is explicit)
3. Quality gate is non-negotiable before model downgrade
4. Repeat-query rate of 30% is industry benchmark, not client data — validate in sprint 1

### Slide 12 — Before / After Hypothesis
Stretch slide. Quantified hypotheses for each lever. CSAT tripwire: if CSAT dips > 2%, pause rollout immediately.

### Slide 13 — The Case in One Slide
Summary for executives who only read the last slide. Problem → Solution → Impact → Trust → Next. All claims are defensible; no unverifiable assertions.

---

## GSF Checklist (Self-Verification)

- [x] Named primary audience: CTO / Head of Engineering (slide 1 and title)
- [x] Every proposed solution maps to at least one GSF pillar (labeled on each solution slide)
- [x] No unverifiable "carbon neutral" claims (caveats slide)
- [x] Recommendations tied to business outcomes: cost (-75%), procurement, reputational risk
- [x] Deck is 13 content slides + title (within 8–14 range)
- [x] R defined in one sentence on slide 2
- [x] Stakeholder "why believe this?" challenge answered explicitly on hotspots slide
- [x] Honest uncertainty named; next validation steps specified

---

## SCI Framing

**SCI = (O + M) / R**

- **R** = one resolved support ticket
- **O** (operational) = energy cost of LLM calls + embeddings + retrieval per ticket × grid carbon intensity (~400 gCO₂eq/kWh US-East-1, assumption)
- **M** (embodied) = share of hardware lifecycle allocated to this workload per ticket (not quantified — would require vendor data)
- **Boundary**: LLM API calls, embedding calls, retrieval. Excludes user devices, CI/CD, monitoring (out of scope for this sprint).
- **What lowers SCI**: fewer tokens/ticket (Energy), smaller model (Energy + Carbon), cleaner grid (Carbon), autoscaling (Hardware)
- **What does NOT lower SCI**: carbon offsets, RECs, PPAs — explicitly excluded by GSF spec

---

## Repository Structure (Suggested)

```
green-tech-assessment-path-a/
├── README.md                          ← this file
├── green-tech-assessment-path-a.pptx  ← slide deck
└── green-assessment-path-a.md         ← lever table + speaker notes
```

---

## Additional Resources

- [Green Software Foundation](https://greensoftware.foundation/)
- [SCI Specification v1.1.0](https://sci.greensoftware.foundation/)
- [Green Software Patterns catalog](https://patterns.greensoftware.foundation/)
- [Electricity Maps](https://app.electricitymaps.com/) — grid carbon intensity by region
- [WattTime](https://watttime.org/) — marginal emissions API
