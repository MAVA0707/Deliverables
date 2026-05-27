# GDPR peer audit — HYMIND
**Auditor:** Markus
**System audited:** HYMIND 
**Teammate:** Gunter

---

## CFU checkpoints

### 1. Recognize

The brief mentions these personal data categories:
- Incidental names from public articles (spokesperson names, author names)
- User-defined search topics and keywords (could identify a person's role or interests)

No special-category data (Art. 9 GDPR) appears in the brief. I can't infer any from the described inputs either.

No data flow explicitly crosses an EU border, but the system uses OpenAI APIs and Pinecone. Both are US-based services. That's a potential international transfer the brief doesn't address.

### 2. Probe

Three questions I'd need answered before giving a compliance opinion:

**Q1: Where does OpenAI process the data sent to it?**
This matters because any personal data in the scraped content or user prompts goes to OpenAI servers. If those are outside the EU, a transfer mechanism (e.g. Standard Contractual Clauses) is required.
Provisional assumption: Processing happens partly in the US. SCCs may apply but aren't documented.

**Q2: Who is the client organisation using this system?**
The brief says "internal business users" but doesn't name the company or confirm it's an EU-based entity. If it's EU-based, GDPR applies fully. If non-EU, scope changes.
Provisional assumption: EU-based company, so GDPR applies.

**Q3: Are user-defined keywords stored, and if so for how long?**
User search topics count as personal data if they can identify someone (e.g. "news about CEO X"). The brief doesn't mention retention rules.
Provisional assumption: Keywords are stored at least temporarily. No retention policy exists.

### 3. Map roles

| Entity | Role | Processing activity | DPA needed? |
|---|---|---|---|
| Client company | Controller | Defines purpose, receives reports | No (internal) |
| Project team / builder | Processor (likely) | Builds and operates the system | Yes, if separate entity |
| OpenAI | Sub-processor | LLM inference, embeddings | Yes |
| Pinecone | Sub-processor | Vector storage | Yes |
| n8n | Sub-processor | Workflow automation, report distribution | Yes |
| RSS/news API providers | Independent controllers | Public content sources | No |

The brief doesn't mention Data Processing Agreements (DPAs) for OpenAI, Pinecone, or n8n.

---

## Phase 2: Personal data summary

| Data category | Source | Purpose | Crosses EU border? | Special category? |
|---|---|---|---|---|
| Incidental names in articles | Public RSS/web | Market intelligence | Possibly (OpenAI/Pinecone) | No |
| User search keywords | Internal users | System operation | Possibly (stored in Pinecone) | No |
| Author/byline names | News APIs | Source attribution | Possibly | No |

---

## Phase 3: Clarifying questions log

| # | Question | Why it matters | Provisional assumption |
|---|---|---|---|
| 1 | Where does OpenAI process inputs? | International transfer mechanism needed if outside EU | US processing, no SCCs documented |
| 2 | Who is the controller organisation? | Determines GDPR territorial scope | EU-based company |
| 3 | Are user keywords retained after a session? | Triggers data minimisation and retention obligations | Yes, temporarily retained |
| 4 | Does any report distribution go outside the company? | External distribution of AI-generated content with incidental names changes risk profile | Assumed internal only |
| 5 | Is there a privacy notice for internal users? | Art. 13 GDPR requires notice when collecting data from data subjects | No notice mentioned |

---

## Phase 4: Audit report

### Section 1: System summary

HYMIND collects public content from RSS feeds, news APIs, and web crawling, then uses LLMs to generate executive market intelligence reports. The system targets the hydrogen and fuel cell industry. Outputs go to internal staff: product managers, analysts, and strategy teams. Personal data enters the system incidentally, mostly as names in public articles, and also through user-defined search keywords. The system doesn't make automated decisions.

### Section 2: Data and role map

Personal data is low-volume and mostly incidental. The main categories are names from public articles and user search keywords. The controller is the client company. The builder's team is likely a processor. OpenAI, Pinecone, and n8n are sub-processors. No DPAs are mentioned in the brief for any of them. Data likely crosses EU borders through OpenAI and Pinecone, both US-based. No transfer mechanism is documented.

### Section 3: Compliance findings

**Finding 1 — International transfer mechanism**
Severity: **Blocking**

OpenAI and Pinecone are US-based. Any personal data sent to them (names in scraped content, user keywords) is an international transfer under Art. 44 GDPR. The brief provides no evidence of Standard Contractual Clauses or another valid transfer mechanism. Processing cannot legally continue without this.

Recommended action: Confirm whether OpenAI and Pinecone offer SCCs in their terms. Sign and document them. Check if Pinecone's EU region can be used to keep data inside the EU.
Escalation needed: Yes. Legal or DPO review required before production deployment.

---

**Finding 2 — DPAs missing for sub-processors**
Severity: **Blocking**

Art. 28 GDPR requires written Data Processing Agreements between the controller and every processor. OpenAI, Pinecone, and n8n all process personal data on behalf of the controller. The brief mentions none. Without DPAs, processing is not lawful.

Recommended action: Check existing vendor terms for Art. 28 clauses. Many vendors (including OpenAI) provide standard DPA documents. Sign and store them.
Escalation needed: Yes. Controller must execute these before go-live.

---

**Finding 3 — Lawful basis not documented**
Severity: **Significant**

The brief doesn't state which lawful basis under Art. 6 GDPR applies to the processing of incidental personal data. For internal business use, legitimate interest (Art. 6(1)(f)) is plausible, but a Legitimate Interest Assessment (LIA) needs to be documented. Without it, the lawful basis is unconfirmed.

Recommended action: Document an LIA. The argument is straightforward: the data is incidental, public, and not used to profile individuals. The LIA should still exist in writing.
Escalation needed: No, but DPO input is helpful.

---

**Finding 4 — No retention policy**
Severity: **Significant**

The brief doesn't mention how long scraped content, LLM outputs, or user keywords are stored. Art. 5(1)(e) GDPR requires personal data to be kept no longer than necessary. Without a defined retention period, the system can't demonstrate compliance.

Recommended action: Define retention periods for each data category. For incidental names in reports, a short period (e.g. 90 days) after report delivery is reasonable. Automate deletion where possible.
Escalation needed: No.

---

**Finding 5 — No privacy notice for internal users**
Severity: **Minor**

Users who enter search keywords are data subjects if those keywords can identify them. Art. 13 GDPR requires a privacy notice at the point of collection. The brief mentions no notice.

Recommended action: Add a brief internal privacy notice to the system UI or onboarding documentation. It doesn't need to be long.
Escalation needed: No.

### Section 4: GDPR obligations checklist

| Obligation | Assessment | Note |
|---|---|---|
| Lawful basis identified for each processing purpose | Gap identified | No lawful basis stated; LIA not documented |
| Purpose limitation respected | Appears met | Outputs are informational only, internal use |
| Data minimisation | Cannot determine | Unclear what data is retained after processing |
| Controller/processor roles mapped and DPAs in place | Gap identified | No DPAs mentioned for OpenAI, Pinecone, n8n |
| International transfer mechanism documented | Gap identified | US-based vendors used; no SCCs mentioned |
| DPIA conducted if required | Cannot determine | Likely not required given low personal data volume, but not confirmed |
| Article 22 safeguard in place | Appears met | Brief explicitly states no automated decisions |
| Privacy notice covers AI processing | Gap identified | No notice mentioned for internal users |
| Data subject rights can be operationalised | Cannot determine | No process described for access or erasure requests |

### Section 5: Overall recommendation

**Do not proceed** (for production deployment).

The system has 2 blocking findings: no documented international transfer mechanism for US-based sub-processors, and no DPAs in place. These are not documentation gaps that can be fixed later. Under Art. 44 and Art. 28 GDPR, processing without them is unlawful. Both findings are fixable, and the system's actual personal data risk is low. But the paperwork must come first. Once DPAs and SCCs are signed, the path to "proceed with conditions" is short.

### Section 6: What this report is not

This report is not a legal opinion. It's not a DPIA. It's not a certification of compliance. The controller should get proper legal review before relying on this assessment for any production decision.

---

## Phase 5: Debrief notes

*(To be completed after debrief conversation with teammate)*

**Where audits agreed:**

**Where audits diverged:**

**Joint closing note:**

*(To be written together with teammate after the debrief)*

---

## Stretch: Remediation plan for Finding 1 (international transfer mechanism)

**What closes the gap:** A signed Data Processing Agreement with OpenAI that includes Standard Contractual Clauses (EU Commission 2021 SCCs, Module 2: controller to processor). OpenAI already provides this document — it needs to be formally executed and stored. For Pinecone, the same applies; Pinecone also offers EU region hosting which would eliminate the transfer issue entirely.

**Who owns it:** The controller's legal team or DPO executes the DPA. If no DPO exists, the project owner escalates to legal counsel.

**Realistic timeline:** 1 to 2 weeks. OpenAI's DPA is available in their platform settings and can be signed online. Pinecone's DPA requires a written request but is standard.

**Evidence for a regulator:** Signed DPA documents with date stamps. Records of which EU SCC module was selected and why. If Pinecone's EU region is used, a configuration screenshot showing the data region setting.
