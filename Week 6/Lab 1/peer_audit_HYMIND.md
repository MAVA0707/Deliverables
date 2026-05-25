# Peer audit report — HYMIND
**Auditor:** Student peer reviewer (novice, EU AI Act course)
**System audited:** HYMIND — AI-assisted market intelligence for hydrogen and fuel cell industry
**Date:** May 2026

---

## Section 1: System summary

HYMIND collects public information from RSS feeds, news APIs, web crawling, and search engines. It processes this content through large language models and produces executive-style reports, trend summaries, and market intelligence updates. The outputs go to internal staff — product managers, engineers, and strategy teams. The system does not make automated decisions. Users are expected to review findings before acting on them.

---

## Section 2: Risk classification

| Question | Answer |
|---|---|
| Does this system fall under any prohibited category (Article 5)? | No |
| Does this system operate in any of the eight Annex III areas? | No |
| If Annex III: does it significantly influence decisions in that area? | Not applicable |
| Does this system interact with end users or generate content requiring disclosure (Article 50)? | Possibly — AI-generated summaries distributed to internal users |
| **First-pass risk tier** | **Minimal risk / possibly limited risk (transparency)** |
| One-sentence justification | HYMIND does not fall under any Annex III category and does not make automated decisions, but Article 50 may apply if AI-generated reports are distributed to users without disclosure that they were AI-generated. |

I'm fairly confident this is minimal risk. The one uncertainty is whether Article 50 transparency requirements apply to internal report distribution.

---

## Section 3: Role map

**Provider:** The project team that built HYMIND using Python, LangGraph, n8n, Pinecone, and OpenAI APIs. They are responsible for the overall system design and for complying with any applicable AI Act obligations.

**Deployer:** Also likely the same team or the company using HYMIND internally. Since the system is used by internal staff only (not the general public), the deployer context is an organization using AI for its own business processes.

**Third-party vendors:** OpenAI (language model and embeddings), Pinecone (vector database), n8n (workflow automation). These vendors are upstream providers of AI components. Their models are integrated into HYMIND, which means HYMIND depends on their compliance posture for the underlying model layer.

Key obligations from each role:
- The provider/deployer must check if Article 50 transparency obligations apply.
- If Article 50 applies, the deployer must ensure internal users know they're reading AI-generated content.
- Third-party AI models (OpenAI) should already comply with their own EU AI Act obligations as general-purpose AI providers, but the HYMIND team should verify this.

---

## Section 4: Compliance findings

**Finding 1 — Article 50 transparency disclosure**
Severity: Minor

The brief says the system generates "AI generated summaries" and distributes them via automation workflows. Article 50(1) of the EU AI Act requires that AI systems interacting with natural persons must disclose they are AI. For internal report distribution, this probably counts. The brief does not mention any disclosure mechanism. Users receiving AI-generated reports may not know the content was machine-generated.

Recommended action: Add a clear label to all distributed reports — something like "This report was generated with AI assistance." A single line in the report header is enough.

Escalation needed: No. This is a minor addition, not a redesign.

---

**Finding 2 — Human review is informal, not enforced**
Severity: Minor

The brief says "human review exists" but also notes the system "does not enforce mandatory review workflows technically." This is fine for minimal-risk AI, but it means the team relies on user behavior rather than process controls. If the system's risk tier were ever reassessed upward, this gap would become significant.

Recommended action: Document the expected review process in an internal policy, even informally. This protects the team if questions arise later.

Escalation needed: No.

---

**Finding 3 — Third-party AI vendor dependency not documented**
Severity: Minor

HYMIND uses OpenAI for language generation and embeddings. The brief does not mention whether the team has reviewed OpenAI's EU AI Act compliance status or whether there is a data processing agreement in place. Incidental personal data (author names, spokesperson names) passes through OpenAI's API.

Recommended action: Check if a data processing agreement with OpenAI is in place. Confirm that personal data in processed articles is handled correctly under GDPR Article 28.

Escalation needed: Possibly — if no DPA is in place, this should go to legal or a data protection officer.

---

**Finding 4 — GDPR: incidental personal data**
Severity: Minor

The brief acknowledges that personal data may "incidentally appear in public articles" such as author names. This data is processed by the system and sent to third-party APIs. Even if incidental, this is personal data under GDPR. The brief does not mention a legal basis for processing or a privacy notice.

Recommended action: Document the legal basis (likely legitimate interest) and check whether the company's existing privacy documentation covers this processing activity. Update the internal data register if needed.

Escalation needed: Possibly — route to the data protection officer for a quick review.

---

## Section 5: Overall recommendation

**Proceed with conditions.**

HYMIND looks like a minimal-risk system under the EU AI Act. There are no prohibited practices and no Annex III activity. The 4 findings are all minor, but 2 of them touch GDPR (third-party vendor DPA and incidental personal data), which should be confirmed with legal or a DPO before production deployment. The Article 50 transparency disclosure is a simple fix. None of these findings require a redesign.

---

## Section 6: What this report is not

This report is not a legal opinion, not a conformity assessment, and not a certification. The findings and recommendations here are based only on the system brief provided and represent a student-level independent review. The conclusions must be verified with qualified legal counsel before any EU market placement or commercial deployment.

---

## Clarifying questions log (Phase 3)

**Q1: Who receives the distributed reports — only internal employees, or also external clients or partners?**
Why it matters: If reports go outside the organization, Article 50 transparency and potentially other obligations become more relevant.
Provisional assumption: Reports stay internal. This supports the minimal-risk classification.

**Q2: Does the system produce outputs that influence any employment, credit, insurance, or other decisions covered by Annex III?**
Why it matters: If a product manager uses market intelligence to, for example, evaluate partnership suitability, there could be an argument for a higher tier — though a weak one.
Provisional assumption: The outputs are informational only and do not feed into any Annex III decision process. Minimal risk holds.

**Q3: Is there a data processing agreement with OpenAI, and does the company have a DPO?**
Why it matters: GDPR compliance depends on this. Personal data in processed articles flows to OpenAI.
Provisional assumption: No DPA has been confirmed. This is a gap to check.

---

## Joint closing note (to be completed after debrief with teammate)

*To be filled in after the Phase 5 debrief conversation.*

Auditing your own system means you already know what every part does and why you made each choice. That familiarity makes it easy to assume things are fine without checking them. An external reviewer has no assumptions — everything unclear in the brief becomes a question or a gap. The debrief showed that [teammate's specific finding/agreement to be added here].
