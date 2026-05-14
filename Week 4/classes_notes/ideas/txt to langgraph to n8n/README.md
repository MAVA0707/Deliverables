# Meeting Summary Agent

**Autonomous Agent Challenge Lab — Module 3**

A LangGraph agent that watches for meeting transcript files, summarizes them into key takeaways, topics covered, and next steps, creates a Notion page, and sends the team a Telegram notification with a preview and direct link.

## Files

| File | Description |
|---|---|
| `agent.py` | LangGraph agent — 4 nodes: parse, summarize, Notion, Telegram |
| `sample_transcript.txt` | Example transcript for testing |
| `n8n_trigger_workflow.json` | n8n: watches `/transcripts/`, calls agent, archives file |
| `project_plan.md` | Full project plan |
| `lab_summary.md` | Reflection paragraph |

## How It Works

```
[.txt dropped in /transcripts/]
       │
  [n8n Watch Folder] ──► [Read File] ──► [POST /process-transcript]
                                                    │
                                          [LangGraph Agent]
                                            │
                                       parse_input
                                       (date, title, participants)
                                            │
                                       generate_summary
                                       (key takeaways, topics, next steps)
                                            │
                                       create_notion
                                       (formatted page with all sections)
                                            │
                                       send_telegram
                                       (preview + Notion link)
```

## Setup

### 1. Install
```bash
pip install langgraph langchain-openai notion-client fastapi uvicorn python-dotenv
```

### 2. Configure `.env`
```
OPENAI_API_KEY=sk-...
NOTION_API_KEY=secret_...
NOTION_PARENT_PAGE_ID=the-id-of-the-parent-page-for-summaries
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-team-chat-id
```

**Getting your Telegram chat ID:** Add your bot to the team group, then send a message and call `https://api.telegram.org/bot<TOKEN>/getUpdates` — the `chat.id` field is what you need.

### 3. Test locally (dry run — no credentials needed)
```bash
python agent.py sample_transcript.txt
```
Without credentials the agent prints what it *would* write to Notion and Telegram.

### 4. Run as API server (for n8n)
```bash
python agent.py --server
# Listens on http://localhost:8000
# POST /process-transcript  { "transcript": "...", "filename": "..." }
```

### 5. Import n8n workflow
Import `n8n_trigger_workflow.json`. It watches `/transcripts/` for new files, reads them, calls the agent, and archives processed files to `/transcripts/processed/`.

## Notion Page Structure

Each created page looks like this:

```
📅 2026-05-14  |  👥 Alice Johnson, Bob Smith, Carol White

─────────────────────────────────
🎯 Key Takeaways
  • API migration is 70% complete; auth refactor is the remaining blocker
  • Client dashboard design approved; filter components are next
  ...

─────────────────────────────────
📋 Topics Covered
  • API migration progress and auth module blocker
  • Client dashboard design approval
  ...

─────────────────────────────────
➡️ Next Steps
  • Bob: finish auth refactor by May 20
  • Carol: build filter components, prototype by May 20
  ...

─────────────────────────────────
📄 Full Transcript
[full transcript text]
```

## Telegram Message Format

```
📋 New Meeting Summary Available

Q2 Planning Sync
📅 2026-05-14  |  👥 3 participants

Key Takeaways:
  • API migration is 70% complete; auth refactor is the blocker
  • Client dashboard design approved
  • Stakeholder review scheduled for May 28

📎 [Open in Notion](https://notion.so/...)
```
