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

