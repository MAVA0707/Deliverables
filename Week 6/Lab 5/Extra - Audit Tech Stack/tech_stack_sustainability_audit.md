# Audit: Sustainability Disclosures in My AI Stack

## My Tools

I chose 5 tools I use or expect to use in AI/automation projects:
- OpenAI (GPT models)
- Anthropic (Claude)
- Hostinger (self-hosted infrastructure)
- LangSmith (LLM observability)
- Pinecone (managed vector database)
- Notion (workspace documentation)  

---

## Evidence Table

| Tool | What I use it for | Deployment note | What the vendor publicly says | Evidence URL + access date | What is unclear or not disclosed | Why this matters for greener decisions |
|------|------------------|-----------------|-------------------------------|---------------------------|--------------------------------|----------------------------------------|
| **OpenAI** | API calls for GPT-4 and GPT-3.5 completions in production | Cloud-hosted, default regional routing | Commits to 100% renewable energy use for data centers by 2025. Operates data centers for AI training and inference but does not disclose per-request energy consumption or exact PUE (Power Usage Effectiveness) metrics. VentureBeat (2023) and OpenAI climate page mention carbon neutrality goals. | https://openai.com/ (Checked May 2026). Company sustainability commitments not detailed in single consolidated page. | Per-request carbon intensity. Scope and methodology of carbon neutrality claim (offsets vs. renewable energy vs. grid mix). Breakdown by model size or inference vs. training. Whether 2025 deadline will be met. | Choosing GPT-3.5 over GPT-4 might reduce energy use per request, but OpenAI doesn't publish numbers. Without comparative disclosure, I can't measure my carbon tradeoff. Hosting region choice likely matters more than model choice here. |
| **Anthropic (Claude)** | API calls for reasoning and text generation in production | Cloud-hosted, default regional routing | Publicly states commitment to responsible AI. Mentions energy efficiency in training but does not publish per-request energy figures, PUE metrics, or renewable energy percentages. Website focuses on constitutional AI, not infrastructure sustainability. | https://www.anthropic.com/ (Checked May 2026). No dedicated sustainability or climate page found. | Per-request or per-token carbon cost. Data center location. Renewable energy use %. PUE and cooling efficiency. Training energy footprint for Claude models. Scope boundaries (Scope 1, 2, 3 emissions). | Anthropic's silence on infrastructure details makes it hard to choose Claude over GPT based on climate impact alone. I'm defaulting to geographic routing logic (EU = lower emissions grid) but that's my assumption, not vendor data. |
| **Hostinger** | Self-hosted n8n instance and Redis cache for a pilot automation project | EU region (Frankfurt or Amsterdam) selected manually | Marketing claims 100% renewable energy. Sustainability page states all server energy comes from renewable sources. Provides data center region selection (EU, Asia, US) but does not publish PUE, water usage, or third-party efficiency audits. No breakdown by region. | https://www.hostinger.com/sustainability (Checked May 2026) | Regional PUE metrics. Water usage per region. Scope 2 emissions (purchased electricity grid mix). Third-party audit or certification (ISO 50001, ISO 14001). Whether renewable claim includes Scope 2 only or Scope 1+2. Actual supplier contracts. | Choosing EU hosting is sensible if grids are greener (they mostly are), but Hostinger doesn't prove its actual regional footprint. I'm relying on external grid data, not vendor data. Self-hosting adds my infrastructure carbon cost—Hostinger discloses little about shared resource efficiency. |
| **LangSmith** | Observability and debugging for LLM app calls | Langchain Cloud infrastructure, vendor-hosted | No public sustainability page or climate disclosures found. No mention of renewable energy, data center location, PUE, or carbon commitment on main site or docs. Framed as observability tool; sustainability is not mentioned. | https://www.langchain.com/langsmith (Checked May 2026) | Everything. No baseline energy or carbon data. Data center locations. Hosting provider (AWS, Azure, GCP unknown). Renewable energy use. PUE. Scope 1, 2, 3 breakdown. Whether Langchain finances carbon offsets. | LangSmith's complete lack of public sustainability info is the most important unknown. If I want to measure my observability cost, I can't. This is a decision blocker unless I contact sales directly. For a production system, I might shift to open-source tools (Arize, WhyLabs) that publish more. |
| **Pinecone** | Managed vector database for RAG pipelines and similarity search in production | Cloud-hosted, defaults to US region (Iowa) with option for EU | No public sustainability page or climate commitment found on main site or docs. Marketing materials mention "enterprise-grade infrastructure" but no renewable energy, PUE, data center location, or carbon targets published. Pinecone operates on cloud infrastructure but does not disclose provider (AWS, Azure, GCP) or environmental practices. | https://www.pinecone.io/ (Checked May 2026). https://www.pinecone.io/docs/ searched for sustainability or climate info with no results. | Everything. Data center locations (assumed US by default). Which cloud provider (AWS/Azure/GCP). Renewable energy %. PUE metrics. Scope 1, 2, 3 emissions. Whether offsets are used. Regional carbon intensity. Per-vector-stored carbon cost. | Pinecone's silence is risky because it's a core service in my RAG pipeline. Unlike self-hosted databases, Pinecone owns the carbon footprint and won't share numbers. Switching to self-hosted Weaviate or Milvus might be greener, but I'd need to guess. Default US routing could mean higher grid carbon than EU Hostinger. |
| **Notion** | Workspace documentation, project tracking, and shared knowledge base | Cloud-hosted, vendor-managed | No dedicated sustainability page found. Main privacy and security pages do not mention renewable energy, carbon goals, or data center practices. Marketing emphasizes "reliable infrastructure" but provides no environmental detail. Support docs mention data center redundancy but not location or energy source. | https://www.notion.so/ (Checked May 2026). https://www.notion.so/privacy-policy searched; no sustainability info. | Data center locations. Which hosting provider (AWS/Azure/GCP assumption). Renewable energy use %. PUE. Carbon emissions scope and magnitude. Whether energy comes from grid, offsets, or renewable contracts. Regional breakdown (if multi-region). | Notion is a productivity tool, not a compute-heavy service, so its per-request carbon is likely low. But Notion publishes nothing, so I can't compare it to alternatives like Obsidian (self-hosted, zero cloud carbon) or GitHub Wikis (piggybacks on existing AWS footprint). Without data, I default to cloud convenience over climate impact. |

---

## Comparison of Vendor Transparency

**Clearest public information:** Hostinger publishes a sustainability page and region selection. It's still vague (no PUE, no regional breakdown), but it shows intent.

**Most important unknown:** LangSmith discloses nothing. Pinecone and Notion also publish no environmental data. Among the three, Pinecone is riskier because vector DB services are compute-intensive. Notion is low-priority because documentation storage is not resource-heavy. LangSmith remains highest-risk because observability sits on every request.

**Vendors staying at slogan level:** OpenAI and Anthropic both claim sustainability or efficiency but hide per-request carbon numbers. Without those, I can't make a model-choice tradeoff. Both say "renewable" or "efficient" but don't detail scope, grid mix, or audit results.

**SaaS silence pattern:** Pinecone, LangSmith, and Notion all fall silent on infrastructure. They're closed-source, vendor-hosted, and won't disclose. This pattern forces me to either contact sales (slow) or default to carbon-efficient alternatives I can self-host.

---

## One Design Decision I Might Change

If my functional unit R is "carbon per completed user request for a RAG chatbot serving 1,000 users/month," public disclosures help me understand **which vendor has lower grid emissions in my deployment region**, but they do not tell me **whether Pinecone's managed vector DB costs less carbon than self-hosting Weaviate on EU Hostinger**.

For the next project, I would:
1. **Choose Weaviate or Milvus (self-hosted) over Pinecone.** Pinecone won't disclose footprint, defaults to US. Self-hosting on EU infrastructure is likely greener and measurable.
2. **Drop Notion for Obsidian.** Notion publishes zero climate data. Obsidian stores notes locally or on my own git repo—no cloud carbon. For a hackathon, Notion's convenience wins. For a bootcamp project with sustainability as a requirement, Obsidian or GitHub Wiki is the choice.
3. **Publish my own energy estimate for self-hosting vs cloud.** OpenAI, Anthropic, Hostinger, and LangSmith all hide numbers. I'll measure my actual Hostinger usage (CPU, bandwidth, runtime) and compare to cloud vendor defaults.
4. **Cut LangSmith unless Langchain publishes infrastructure carbon.** If I need observability, Arize or open-source logging on my own EU Hostinger instance becomes the default.
5. **Route API calls to EU endpoints by default.** Grid carbon intensity is a measurable proxy when vendor data is missing. EU grids average 300-400 gCO2e/kWh; US averages higher.

---

## Lesson Vocabulary

If my functional unit R is **carbon per completed user request**, public disclosures help me understand **regional grid carbon intensity and hosting location**, but they do not tell me **per-request energy consumption or whether the observability and logging I add costs more carbon than the LLM inference itself**.

---

## README for GitHub

This audit examines 6 tools from my AI stack:
- `tech_stack_sustainability_audit.md` (this file): Evidence table, transparency comparison, and reflection.
- Research method: Official vendor pages and public sustainability docs only. No external rankings or third-party analysis.
- Access dates: All links checked May 2026.
- Next step: Use this table to design a pilot project that measures actual carbon, then compare to vendor claims.
