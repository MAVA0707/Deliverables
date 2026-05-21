# Moinland AI Agents

Three AI agents that help the Moinland CEO and CRO create LinkedIn content and stay on top of industry news — without spending hours on research.

Built with n8n. Week 5 project, Ironhack AI Consulting Bootcamp.

---

## What are the agents?

| Agent | What it does |
|---|---|
| **Ian** – Idea to Notion | You send a topic via Telegram. Ian researches it, writes a LinkedIn draft, saves it to Notion. |
| **Rea** – Research & Analysis | Reads RSS feeds every day. Sends a weekly email briefing about funding news and startup trends. |
| **Cal** – Coaching to LinkedIn | When a Granola coaching transcript lands in Google Drive, Cal turns the key insights into a LinkedIn draft in Notion. |

---

## Repo Structure

```
Project-3/
├── 1-Ian-Idea-to-Notion/
│   └── IAN_-_Idea_to_Notion.json
├── 2-Rea-Research-Analysis/
│   └── V2_0_Rea_v2_-_Research___Analysis.json
├── 3-Cal-Coaching-to-LinkedIn/
│   └── V1_0_Cal_v1_-_Coaching_to_LinkedIn.json
├── docs/
│   ├── README.md
│   ├── stories.md
│   └── documentation.md
└── resources/
    └── (brand voice, example posts, transcript samples)
```

---

## Required Tools & APIs

You need accounts and API keys for:

- **n8n** (self-hosted or cloud) — the automation platform
- **OpenAI** — GPT-4o-mini for all writing and reasoning
- **Telegram Bot** — for sending ideas (Ian) and getting notifications (Cal)
- **Notion** — to store drafts and the Moinland Knowledge Base
- **Tavily** — web search for research (Ian and Cal)
- **Pinecone** — vector database for storing articles (Rea) and coaching sessions (Cal)
- **Google Drive** — watches for new Granola transcripts (Cal)
- **SMTP / Email** — for sending the weekly briefing (Rea)
- **RSS Feeds** — startup and funding news sources (Rea)

---

## Environment Variables

Set these in your n8n credentials:

```
OPENAI_API_KEY
TELEGRAM_BOT_TOKEN
NOTION_API_KEY
TAVILY_API_KEY
PINECONE_API_KEY
GOOGLE_DRIVE_OAUTH
SMTP_HOST / SMTP_USER / SMTP_PASSWORD
```

---

## How to Run

1. Import the `.json` workflow files into n8n (Settings → Import Workflow)
2. Add your credentials in n8n for each service
3. In Notion, create a Knowledge Base database with `Type` property (values: `Brand Voice`, `Example Post`)
4. In Pinecone, create an index for Rea and one for Cal
5. Activate the workflows

**Ian:** Send a message to your Telegram bot → wait ~30 seconds → check Notion.

**Rea:** Runs automatically every day (RSS) and every week (email briefing). You can also trigger manually in n8n.

**Cal:** Upload a Granola transcript to the watched Google Drive folder → check Notion + Telegram.

---

## Notes

- All agents have error handling. If something breaks, you get a Telegram or email alert.
- Costs are mainly from OpenAI API calls (GPT-4o-mini is cheap). Pinecone free tier is enough to start.
- See `docs/documentation.md` for architecture details.
- See `docs/stories.md` for user stories and sprint plan.
