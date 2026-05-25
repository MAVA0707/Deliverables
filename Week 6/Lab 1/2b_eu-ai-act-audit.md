# EU AI Act Compliance Audit
## Moinland AI Agents (Ian, Rea, Colin)

**Prepared by:** Ironhack AI Consulting Bootcamp, Week 5  
**Date:** May 2026  
**Note:** This is a student exercise. Not a legal opinion.

---

## Phase 1: System Brief

**What does the system do?**

Moinland is a coaching firm for startup founders. The CEO and CRO are experts but have no time to write LinkedIn posts or follow funding news. We built three AI agents that help them create content and stay informed:

- **Ian** takes a topic idea sent via Telegram, searches the web, writes a LinkedIn post draft, and saves it to Notion.
- **Rea** reads startup and funding RSS feeds every day and sends a weekly email briefing summarizing the news.
- **Colin** watches for new coaching session transcripts in Google Drive, extracts key topics, and writes a LinkedIn post draft saved to Notion.

All three agents use OpenAI (GPT-4o-mini) for language generation. Ian and Colin also use Tavily for web search. Rea and Colin use Pinecone to store and retrieve content.

**What inputs does it take?**

- Ian: A short text message (topic idea) sent by the CEO via Telegram. No personal data of third parties.
- Rea: Public RSS feed articles. No personal data.
- Colin: Coaching session transcripts from Granola (uploaded to Google Drive). These may contain personal data — names or quotes from coaching clients could appear in transcripts.

**What does it output?**

All three agents output text — a LinkedIn post draft (Ian, Colin) or a news briefing email (Rea). These are drafts. Nothing is published automatically.

**Who is affected by the output?**

The CEO and CRO of Moinland are the only direct users. LinkedIn readers may eventually see a published post, but the agent does not decide what gets published — a human does.

**Does a human review the output before action?**

Yes. Drafts land in Notion (Ian, Colin) or an email inbox (Rea). The CEO or CRO decides whether to publish, edit, or ignore. There is no automated publishing step.

**Who built it?**

A team of Ironhack AI Consulting students (us). We used n8n as the automation platform and connected it to existing services via APIs.

**Who uses it in production?**

Moinland CEO and CRO use it. They are also the people who receive and review the outputs.

---

## Phase 2: Risk Tier Classification

| Question | Answer |
|---|---|
| Does this system fall under any prohibited category (Article 5)? | No. It does not manipulate, deceive, or exploit users. It does not score people or make consequential decisions about them. |
| Does this system operate in any of the eight Annex III areas? | No. Annex III covers employment decisions, education, credit, law enforcement, border control, etc. Content generation for a coaching firm's social media does not fit any of these. |
| If Annex III: does it "significantly influence" decisions in that area? | Not applicable. |
| Does this system interact with end users or generate content requiring disclosure (Article 50)? | Partially. The system generates text. But the CEO/CRO know they are using AI — there is no deception. LinkedIn posts are reviewed and edited before publishing. No chatbot or real-time AI interaction with external users. |
| **First-pass risk tier** | **Minimal risk** |
| One-sentence justification | The system generates draft content for internal review and does not make decisions about natural persons, does not operate in an Annex III domain, and is not a prohibited practice under Article 5. |

**Ambiguity note:** Colin stores coaching transcripts that might contain client data. If transcripts include identifiable personal data of coaching clients, GDPR applies separately from the AI Act. This should be confirmed with a legal professional.

---

## Phase 3: Role Map

| Role | Entity | Key AI Act obligations |
|---|---|---|
| Provider | Ironhack student team (us) | We built and delivered the system. As a minimal-risk system, no mandatory obligations apply under the AI Act. We should still follow voluntary codes of conduct and good practice. |
| Deployer | Moinland (CEO/CRO) | Uses the system in a professional context. For minimal risk, no specific deployer obligations under the AI Act. Responsible for how the output is used (e.g., what they publish on LinkedIn). |
| Vendor — OpenAI | OpenAI (GPT-4o-mini via API) | OpenAI is a provider of a general-purpose AI model. Under the AI Act, GPAI providers have transparency and documentation obligations toward downstream deployers. |
| Vendor — Tavily | Tavily (web search API) | A tool service, not an AI model in the regulated sense. No AI Act obligations specific to Tavily. |
| Vendor — Pinecone | Pinecone (vector database) | A data storage service, not an AI model. No AI Act obligations specific to Pinecone. |
| Vendor — n8n | n8n (automation platform) | An infrastructure tool. Not itself an AI system under the AI Act. |

---

## Phase 4: Obligation Checklist

**Not applicable.** The system is minimal risk and does not trigger the high-risk obligation checklist from Article 9–15 or the conformity assessment process.

---

## Phase 5: Gap Analysis and Remediation

The system is minimal risk, so there are no mandatory AI Act obligations. However, there are three areas worth addressing.

---

**Gap 1 — Colin: Personal data in transcripts**

- **Obligation:** GDPR (not AI Act), but still important. Coaching session transcripts may include personal data of third parties (coaching clients).
- **Current state:** Transcripts are uploaded to Google Drive and processed by OpenAI. It is not clear if clients have consented to this or if Moinland has a data processing agreement with OpenAI.
- **Required state:** Personal data must be processed lawfully. If client names or quotes are in transcripts, processing them via OpenAI requires a legal basis (e.g., consent or legitimate interest) and a data processing agreement with OpenAI.
- **Remediation:** Moinland should review what data is in Granola transcripts. If personal data is present, anonymize transcripts before processing, or get legal advice on the right basis. Check if an OpenAI DPA is in place.
- **Escalation needed?** Yes — to a data protection officer or lawyer.

---

**Gap 2 — No transparency notice for LinkedIn readers**

- **Obligation:** Article 50 of the AI Act says AI-generated content that could be mistaken for human-written text should be labeled (this requirement has nuances and thresholds). Even if not strictly required today, best practice for AI-assisted LinkedIn posts is to disclose AI involvement.
- **Current state:** No disclosure is built into the workflow. The CEO/CRO decides individually whether to mention AI assistance.
- **Required state:** At minimum, awareness of when and whether disclosure is needed. LinkedIn posts written substantially by AI may fall under Article 50 in the future.
- **Remediation:** Moinland should decide on a clear policy: do they disclose AI assistance on posts? A simple note like "drafted with AI" is enough. This is a business decision, but we recommend they make it explicitly.
- **Escalation needed?** No. But worth revisiting as Article 50 implementation develops.

---

**Gap 3 — No logging or audit trail**

- **Obligation:** Not mandatory for minimal risk, but good practice for any AI system used professionally.
- **Current state:** n8n logs execution history by default, but there is no formal record of what inputs were used, what outputs were generated, and what a human decided to do with the output.
- **Required state:** If Moinland ever faces questions about a published post (factual errors, compliance, etc.), having a record helps.
- **Remediation:** Keep Notion drafts with "Requested by" and "Created" fields (already in place for Ian). Make sure drafts are not deleted. Consider adding a "Published / Not published" field so there is a record of what was actually used.
- **Escalation needed?** No.

---

## Phase 6: Compliance Memo

**TO:** Head of Product, Moinland  
**FROM:** Ironhack AI Consulting Team  
**RE:** EU AI Act Compliance — Moinland AI Agents  
**DATE:** May 2026

---

**System Classification**

The three Moinland AI agents (Ian, Rea, Colin) are classified as **minimal risk** under the EU AI Act. They generate draft content for internal review by the CEO and CRO. They do not make decisions about people, do not operate in a regulated domain, and are not a prohibited practice.

**Role Map**

We (the student team) acted as the **provider** — we built the system. Moinland is the **deployer** — you use it in your work. OpenAI is a vendor providing the underlying AI model.

**Key Findings**

1. **Colin may process personal data.** Granola coaching transcripts could contain client names or identifying information. Before using Colin in production, Moinland should check whether this data processing is compliant with GDPR. This is the most important issue to resolve.

2. **No disclosure policy for LinkedIn posts.** There is currently no standard process for deciding whether to label AI-drafted posts as AI-assisted. As Article 50 of the AI Act develops, this gap may become relevant. We recommend deciding on a policy now.

3. **No formal output audit trail.** Notion stores drafts, but there is no record of what was published vs. rejected. This is low risk today but worth improving.

**Recommended Next Steps**

1. (Urgent) Review what personal data appears in Granola transcripts. If client data is present, consult a lawyer or DPO before using Colin in production.
2. (Soon) Agree on an internal policy for AI disclosure on LinkedIn posts.
3. (Later) Add a simple "Status" update in Notion to track which drafts were published.

**Caveats**

This memo is a student exercise produced as part of an Ironhack bootcamp. It is not a legal opinion, a conformity assessment, or a certification. It should not be used as a substitute for qualified legal advice. The classification and gap analysis reflect our understanding of the EU AI Act as of May 2026.

---

## Stretch: Transparency Notice Draft

If Moinland decides to disclose AI assistance on LinkedIn posts, here is a short notice they could add to posts (or use as an internal policy):

> *This post was drafted with the help of an AI writing assistant and reviewed and edited by a human before publishing.*

Or shorter:

> *AI-assisted draft, human-reviewed.*

This covers the spirit of Article 50 without being disruptive to the post format. It is honest and simple. We recommend adding it as a standard footer in the Notion draft template so the CEO/CRO is reminded to decide on it for each post.
