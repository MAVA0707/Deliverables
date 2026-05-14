"""
Meeting Summary Agent
=====================
LangGraph agent that reads a meeting transcript and:
1. Parses meeting metadata (date, participants)
2. Generates a structured summary: key takeaways, topics covered, next steps
3. Creates a Notion page with the full summary
4. Sends a Telegram notification that a new summary is available

Usage:
    python agent.py sample_transcript.txt      # CLI mode
    python agent.py --server                   # API server (for n8n)

Requirements:
    pip install langgraph langchain-openai notion-client fastapi uvicorn python-dotenv

Environment variables (.env):
    OPENAI_API_KEY=...
    NOTION_API_KEY=...
    NOTION_PARENT_PAGE_ID=...   # Notion page under which summaries are created
    TELEGRAM_BOT_TOKEN=...
    TELEGRAM_CHAT_ID=...        # Channel or group chat to notify (e.g. your team group)
"""

import os
import json
import urllib.request
from datetime import datetime
from typing import TypedDict, List, Annotated
import operator

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY", "")
NOTION_API_KEY       = os.getenv("NOTION_API_KEY", "")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "")
TELEGRAM_BOT_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID     = os.getenv("TELEGRAM_CHAT_ID", "")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0,
                 api_key=OPENAI_API_KEY or "placeholder")

# ─────────────────────────────────────────────
# AGENT STATE
# ─────────────────────────────────────────────

class AgentState(TypedDict):
    # Input
    transcript: str
    filename: str

    # Extracted metadata
    meeting_date: str
    meeting_title: str
    participants: List[str]

    # Generated summary sections
    key_takeaways: List[str]
    topics_covered: List[str]
    next_steps: List[str]

    # Outputs
    notion_page_url: str
    notion_page_id: str
    telegram_sent: bool
    errors: Annotated[List[str], operator.add]


# ─────────────────────────────────────────────
# NODE 1: PARSE INPUT
# ─────────────────────────────────────────────

def parse_input(state: AgentState) -> dict:
    """Extract meeting metadata from the transcript header."""
    print("\n[Node 1] Parsing transcript metadata...")

    prompt = f"""Extract the meeting title, date, and participant names from this transcript.

Return ONLY valid JSON — no markdown fences, no explanation:
{{
  "title": "Meeting title or topic (infer from context if not explicit)",
  "meeting_date": "YYYY-MM-DD (use today if not found)",
  "participants": ["Full Name 1", "Full Name 2"]
}}

Today's date: {datetime.now().strftime('%Y-%m-%d')}

Transcript (first 600 characters):
{state['transcript'][:600]}
"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip().strip("```json").strip("```").strip()
        data = json.loads(raw)
        title        = data.get("title", "Team Meeting")
        meeting_date = data.get("meeting_date", datetime.now().strftime('%Y-%m-%d'))
        participants = data.get("participants", [])
    except Exception as e:
        print(f"  Warning: metadata parse failed ({e}), using defaults")
        title        = state.get("filename", "Meeting").replace(".txt", "").replace("_", " ").title()
        meeting_date = datetime.now().strftime('%Y-%m-%d')
        participants = []

    print(f"  Title:        {title}")
    print(f"  Date:         {meeting_date}")
    print(f"  Participants: {', '.join(participants) or 'not found'}")

    return {
        "meeting_title": title,
        "meeting_date": meeting_date,
        "participants": participants,
    }


# ─────────────────────────────────────────────
# NODE 2: GENERATE SUMMARY
# ─────────────────────────────────────────────

def generate_summary(state: AgentState) -> dict:
    """Use LLM to produce key takeaways, topics covered, and next steps."""
    print("\n[Node 2] Generating meeting summary...")

    system = """You are an expert meeting analyst. Summarize meeting transcripts into three sections.
Be concise and specific. Use active language. Do not invent information not in the transcript."""

    user = f"""Meeting: {state['meeting_title']}
Date: {state['meeting_date']}
Participants: {', '.join(state['participants'])}

Transcript:
{state['transcript']}

Return ONLY valid JSON — no markdown fences, no explanation:
{{
  "key_takeaways": [
    "Concise statement of the most important outcomes or decisions (3-5 bullets)"
  ],
  "topics_covered": [
    "Topic discussed in the meeting (3-7 bullets)"
  ],
  "next_steps": [
    "Specific action or follow-up that was agreed (3-6 bullets, include owner if clear)"
  ]
}}"""

    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        raw = response.content.strip().strip("```json").strip("```").strip()
        data = json.loads(raw)
        key_takeaways  = data.get("key_takeaways", [])
        topics_covered = data.get("topics_covered", [])
        next_steps     = data.get("next_steps", [])
    except Exception as e:
        print(f"  Error generating summary: {e}")
        return {
            "key_takeaways": ["Summary generation failed — see raw transcript"],
            "topics_covered": [],
            "next_steps": [],
            "errors": [f"Summary generation error: {e}"],
        }

    print(f"  Key takeaways:  {len(key_takeaways)} items")
    print(f"  Topics covered: {len(topics_covered)} items")
    print(f"  Next steps:     {len(next_steps)} items")

    return {
        "key_takeaways": key_takeaways,
        "topics_covered": topics_covered,
        "next_steps": next_steps,
    }


# ─────────────────────────────────────────────
# NODE 3: CREATE NOTION PAGE
# ─────────────────────────────────────────────

def create_notion_page(state: AgentState) -> dict:
    """Create a richly formatted Notion page with the meeting summary."""
    print("\n[Node 3] Creating Notion page...")

    if not NOTION_API_KEY or not NOTION_PARENT_PAGE_ID:
        print("  ⚠️  Notion credentials not set — DRY RUN")
        _print_summary(state)
        return {
            "notion_page_id": "dry-run-page-id",
            "notion_page_url": "https://notion.so/dry-run",
        }

    try:
        from notion_client import Client
        notion = Client(auth=NOTION_API_KEY)
    except ImportError:
        msg = "notion-client not installed. Run: pip install notion-client"
        print(f"  Error: {msg}")
        return {"notion_page_id": "", "notion_page_url": "", "errors": [msg]}

    def bullet_blocks(items: List[str]) -> list:
        return [
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": item}}]
                },
            }
            for item in items
        ]

    def heading(text: str, level: int = 2) -> dict:
        h = f"heading_{level}"
        return {
            "object": "block",
            "type": h,
            h: {"rich_text": [{"type": "text", "text": {"content": text}}]},
        }

    def divider() -> dict:
        return {"object": "block", "type": "divider", "divider": {}}

    def paragraph(text: str) -> dict:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }

    participants_str = ", ".join(state["participants"]) or "See transcript"
    page_title = f"{state['meeting_date']} — {state['meeting_title']}"

    children = [
        paragraph(f"📅 {state['meeting_date']}  |  👥 {participants_str}"),
        divider(),
        heading("🎯 Key Takeaways"),
        *bullet_blocks(state["key_takeaways"]),
        divider(),
        heading("📋 Topics Covered"),
        *bullet_blocks(state["topics_covered"]),
        divider(),
        heading("➡️ Next Steps"),
        *bullet_blocks(state["next_steps"]),
        divider(),
        heading("📄 Full Transcript", level=3),
        paragraph(state["transcript"]),
    ]

    try:
        page = notion.pages.create(
            parent={"type": "page_id", "page_id": NOTION_PARENT_PAGE_ID},
            properties={
                "title": {
                    "title": [{"type": "text", "text": {"content": page_title}}]
                }
            },
            children=children,
        )
        page_id  = page["id"]
        page_url = page.get("url", f"https://notion.so/{page_id.replace('-', '')}")
        print(f"  ✅ Notion page created: {page_url}")
        return {"notion_page_id": page_id, "notion_page_url": page_url}

    except Exception as e:
        msg = f"Notion page creation failed: {e}"
        print(f"  ❌ {msg}")
        return {"notion_page_id": "", "notion_page_url": "", "errors": [msg]}


# ─────────────────────────────────────────────
# NODE 4: SEND TELEGRAM NOTIFICATION
# ─────────────────────────────────────────────

def send_telegram(state: AgentState) -> dict:
    """Send a Telegram message linking to the new Notion summary."""
    print("\n[Node 4] Sending Telegram notification...")

    takeaways_preview = "\n".join(
        f"  • {t}" for t in state["key_takeaways"][:3]
    )
    if len(state["key_takeaways"]) > 3:
        takeaways_preview += f"\n  _...and {len(state['key_takeaways']) - 3} more_"

    notion_link = state.get("notion_page_url", "")
    link_line = f"\n📎 [Open in Notion]({notion_link})" if notion_link and "dry-run" not in notion_link else ""

    message = (
        f"📋 *New Meeting Summary Available*\n\n"
        f"*{state['meeting_title']}*\n"
        f"📅 {state['meeting_date']}  |  "
        f"👥 {len(state['participants'])} participants\n\n"
        f"*Key Takeaways:*\n{takeaways_preview}"
        f"{link_line}"
    )

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  ⚠️  Telegram not configured — DRY RUN")
        print(f"\n--- Would send to chat {TELEGRAM_CHAT_ID or '<unset>'}: ---")
        print(message)
        print("---")
        return {"telegram_sent": False}

    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }).encode()

    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
        print(f"  ✅ Telegram notification sent to chat {TELEGRAM_CHAT_ID}")
        return {"telegram_sent": True}
    except Exception as e:
        msg = f"Telegram send failed: {e}"
        print(f"  ❌ {msg}")
        return {"telegram_sent": False, "errors": [msg]}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _print_summary(state: AgentState):
    print(f"\n  {'─'*50}")
    print(f"  SUMMARY: {state['meeting_title']} ({state['meeting_date']})")
    print(f"  Participants: {', '.join(state['participants'])}")
    print(f"\n  KEY TAKEAWAYS:")
    for t in state["key_takeaways"]:
        print(f"    • {t}")
    print(f"\n  TOPICS COVERED:")
    for t in state["topics_covered"]:
        print(f"    • {t}")
    print(f"\n  NEXT STEPS:")
    for t in state["next_steps"]:
        print(f"    • {t}")
    print(f"  {'─'*50}")


# ─────────────────────────────────────────────
# BUILD THE GRAPH
# ─────────────────────────────────────────────

def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("parse_input",      parse_input)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("create_notion",    create_notion_page)
    graph.add_node("send_telegram",    send_telegram)

    graph.add_edge(START,             "parse_input")
    graph.add_edge("parse_input",     "generate_summary")
    graph.add_edge("generate_summary","create_notion")
    graph.add_edge("create_notion",   "send_telegram")
    graph.add_edge("send_telegram",   END)

    return graph.compile()


# ─────────────────────────────────────────────
# FASTAPI ENDPOINT (called by n8n)
# ─────────────────────────────────────────────

def create_api():
    from fastapi import FastAPI
    from pydantic import BaseModel

    app   = FastAPI(title="Meeting Summary Agent")
    agent = build_agent()

    class TranscriptRequest(BaseModel):
        transcript: str
        filename: str = "transcript.txt"

    @app.post("/process-transcript")
    def process_transcript(req: TranscriptRequest):
        result = agent.invoke({
            "transcript": req.transcript,
            "filename":   req.filename,
            "meeting_date": "", "meeting_title": "", "participants": [],
            "key_takeaways": [], "topics_covered": [], "next_steps": [],
            "notion_page_url": "", "notion_page_id": "",
            "telegram_sent": False, "errors": [],
        })
        return {
            "meeting_title":    result["meeting_title"],
            "meeting_date":     result["meeting_date"],
            "notion_page_url":  result["notion_page_url"],
            "telegram_sent":    result["telegram_sent"],
            "key_takeaways":    result["key_takeaways"],
            "topics_covered":   result["topics_covered"],
            "next_steps":       result["next_steps"],
            "errors":           result["errors"],
        }

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


# ─────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────

def run_cli(transcript_path: str):
    import os
    with open(transcript_path, "r") as f:
        transcript = f.read()

    filename = os.path.basename(transcript_path)
    agent    = build_agent()

    print("=" * 60)
    print("MEETING SUMMARY AGENT")
    print("=" * 60)

    result = agent.invoke({
        "transcript":    transcript,
        "filename":      filename,
        "meeting_date":  "", "meeting_title": "", "participants": [],
        "key_takeaways": [], "topics_covered": [], "next_steps": [],
        "notion_page_url": "", "notion_page_id": "",
        "telegram_sent": False, "errors": [],
    })

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    print(f"Meeting:       {result['meeting_title']} ({result['meeting_date']})")
    print(f"Participants:  {', '.join(result['participants'])}")
    print(f"Notion page:   {result['notion_page_url'] or 'not created'}")
    print(f"Telegram sent: {result['telegram_sent']}")
    if result["errors"]:
        print(f"Errors:        {result['errors']}")

    _print_summary(result)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        import uvicorn
        uvicorn.run(create_api(), host="0.0.0.0", port=8000)
    elif len(sys.argv) > 1:
        run_cli(sys.argv[1])
    else:
        print("Usage:")
        print("  python agent.py sample_transcript.txt   # CLI mode")
        print("  python agent.py --server                # API server for n8n")
