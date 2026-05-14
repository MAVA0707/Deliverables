# lab_summary.md

## Reflection

The hardest part of planning this agent was **not the architecture — it was the deduplication boundary**. Deciding exactly where "I've seen this before" lives (URL hash vs. semantic embedding vs. both) forced a real trade-off: a pure URL hash is fast but misses near-identical stories from different outlets, while a pure semantic check is expensive and can over-suppress genuinely new articles on the same ongoing topic. The chosen approach — embedding `url + title` together with a 0.95 cosine threshold — balances both concerns, but tuning that threshold empirically will be the first thing to revisit after MVP.

**What I would do differently**: I would build the relevance-grading prompt before designing anything else and iterate it against 20–30 real articles. The quality of autonomous judgment lives entirely in that prompt, and it's the cheapest thing to iterate — yet it's typically designed last. Prompt-first, infrastructure-second.

**Biggest open question**: How does the agent handle a topic that gradually shifts meaning over time (e.g., "AI regulation" in early 2025 vs. late 2025 as legislation evolves)? The Pinecone index will retain embeddings anchored to old semantic space, potentially suppressing new articles that are semantically similar to old ones but substantively different. A rolling TTL on stored embeddings (e.g., expire after 30 days) may be necessary — but that's a v2 problem.

---

*Detailed project plan: `project_plan.md` | Agent code: `langgraph_agent.py` | n8n workflow: `n8n_workflow.json`*
