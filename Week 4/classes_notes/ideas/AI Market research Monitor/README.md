# AI Market Research Monitor
### Autonomous Agent Lab — Deliverables

An autonomous daily agent that monitors a configurable topic, grades article relevance, deduplicates against what it already knows, writes a digest to Notion, and notifies via Telegram.

## Files

| File | Purpose |
|---|---|
| `project_plan.md` | Full project plan: use case, tech stack, MVP scope, risks, phases |
| `langgraph_agent.py` | LangGraph RAG agent (Python — runnable locally) |
| `n8n_workflow.json` | Complete n8n workflow — import directly into n8n |
| `lab_summary.md` | Reflection paragraph required by lab |
| `README.md` | This file |

## How to Run the Python Prototype

```bash
pip install langgraph langchain-openai pinecone-client tavily-python \
            beautifulsoup4 requests python-dotenv

# .env:
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX=market-research-seen
TAVILY_API_KEY=...
MONITOR_TOPIC=AI regulation news Europe 2025

python langgraph_agent.py
```

## How to Import the n8n Workflow

1. n8n → Settings → Import Workflow → paste `n8n_workflow.json`
2. Add credentials: OpenAI, Notion, Telegram Bot
3. Set n8n Variables: `TAVILY_API_KEY`, `PINECONE_API_KEY`, `PINECONE_HOST`, `NOTION_DATABASE_ID`, `TELEGRAM_CHAT_ID`
4. Create Notion DB with fields: Title, Topic, Run Date, Articles Found, Top Headline, Status
5. Activate — runs at 08:00 UTC. Change topic in the Set Config node.
