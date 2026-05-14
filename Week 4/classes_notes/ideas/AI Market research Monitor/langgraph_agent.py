"""
AI Market Research Monitor — LangGraph Agent
============================================
Implements the RAG-with-relevance-check pattern from the course notebooks.

Graph flow:
  search_web → fetch_article → grade_relevance
    → (not_relevant) → log_skip
    → (relevant) → check_duplicate
      → (duplicate) → log_skip
      → (new) → extract_insights → store_seen → add_to_digest
  After all articles: compile_digest → END

Usage:
    pip install langgraph langchain-openai pinecone-client tavily-python \
                beautifulsoup4 requests python-dotenv
    
    Set environment variables:
        OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX, TAVILY_API_KEY

    python langgraph_agent.py
"""

import os
import hashlib
import json
from datetime import datetime
from typing import TypedDict, List, Dict, Literal, Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ─── Config ────────────────────────────────────────────────────────────────
OPENAI_API_KEY    = os.environ["OPENAI_API_KEY"]
PINECONE_API_KEY  = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX    = os.environ.get("PINECONE_INDEX", "market-research-seen")
TAVILY_API_KEY    = os.environ["TAVILY_API_KEY"]

GRADE_MODEL       = "gpt-4o-mini"   # cheap, fast — used for relevance grading
DIGEST_MODEL      = "gpt-4o"        # higher quality — used for insight extraction & digest
MAX_ARTICLE_TOKENS = 2000           # truncate to keep costs predictable
DEDUP_THRESHOLD   = 0.95            # cosine similarity above which = duplicate

grade_llm   = ChatOpenAI(model=GRADE_MODEL,  api_key=OPENAI_API_KEY)
digest_llm  = ChatOpenAI(model=DIGEST_MODEL, api_key=OPENAI_API_KEY)
embeddings  = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

# ─── Pinecone lazy init ─────────────────────────────────────────────────────
_pinecone_index = None

def get_pinecone_index():
    global _pinecone_index
    if _pinecone_index is None:
        from pinecone import Pinecone, ServerlessSpec
        pc = Pinecone(api_key=PINECONE_API_KEY)
        existing = [idx.name for idx in pc.list_indexes()]
        if PINECONE_INDEX not in existing:
            pc.create_index(
                name=PINECONE_INDEX,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"[Pinecone] Created index: {PINECONE_INDEX}")
        _pinecone_index = pc.Index(PINECONE_INDEX)
    return _pinecone_index


# ─── State ──────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    topic: str
    search_results: List[Dict]      # raw results from Tavily
    articles_queue: List[Dict]      # articles still to process
    current_article: Optional[Dict] # article currently being processed
    full_text: str                  # scraped body text
    relevance: str                  # "relevant" | "not_relevant"
    relevance_score: float
    is_duplicate: bool
    insights: List[str]             # bullets for current article
    digest_items: List[Dict]        # accumulated results
    final_digest: str               # markdown string for Notion
    stats: Dict                     # run statistics


# ─── Node 1: search_web ─────────────────────────────────────────────────────
def search_web(state: AgentState) -> dict:
    """Call Tavily Search API for the configured topic."""
    print(f"\n[search_web] Searching: '{state['topic']}'")

    resp = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": TAVILY_API_KEY,
            "query": state["topic"],
            "search_depth": "basic",
            "max_results": 10,
            "include_raw_content": False,
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    results = [
        {"url": r["url"], "title": r["title"], "snippet": r.get("content", "")}
        for r in data.get("results", [])
    ]
    print(f"[search_web] Found {len(results)} results")
    return {
        "search_results": results,
        "articles_queue": results.copy(),
        "digest_items": [],
        "stats": {
            "searched": len(results),
            "relevant": 0,
            "new": 0,
            "skipped_irrelevant": 0,
            "skipped_duplicate": 0,
        },
    }


# ─── Node 2: pop_article ────────────────────────────────────────────────────
def pop_article(state: AgentState) -> dict:
    """Take the next article from the queue for processing."""
    queue = list(state["articles_queue"])
    article = queue.pop(0)
    print(f"\n[pop_article] Processing: {article['title'][:60]}...")
    return {
        "articles_queue": queue,
        "current_article": article,
        "full_text": "",
        "relevance": "",
        "relevance_score": 0.0,
        "is_duplicate": False,
        "insights": [],
    }


# ─── Node 3: fetch_article ──────────────────────────────────────────────────
def fetch_article(state: AgentState) -> dict:
    """Scrape the article URL and extract main body text."""
    url = state["current_article"]["url"]
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove navigation/footer noise
        for tag in soup(["nav", "footer", "script", "style", "aside"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        # Rough token truncation (~4 chars per token)
        text = text[: MAX_ARTICLE_TOKENS * 4]
    except Exception as exc:
        print(f"[fetch_article] Failed to scrape {url}: {exc}")
        # Fall back to snippet if scraping fails
        text = state["current_article"].get("snippet", "")

    return {"full_text": text}


# ─── Node 4: grade_relevance ────────────────────────────────────────────────
def grade_relevance(state: AgentState) -> dict:
    """
    Use an LLM to determine if the article is relevant to the topic.
    Returns: relevance = "relevant" | "not_relevant", relevance_score ∈ [0, 1]
    
    This is the key autonomous-judgment step — the agent decides what's worth including.
    """
    topic   = state["topic"]
    title   = state["current_article"]["title"]
    snippet = state["current_article"]["snippet"]
    body    = state["full_text"][:800]  # grade on preview, not full text

    prompt = f"""You are a research analyst grading article relevance.

MONITORING TOPIC: "{topic}"

ARTICLE:
Title: {title}
Snippet: {snippet}
Body preview: {body}

TASK: Decide if this article is directly relevant to the monitoring topic.
An article is relevant if it:
- Contains new information or developments about the topic
- Is published within the last 7 days (assume recency from context)
- Is substantive (not just a mention in passing)

Respond ONLY with JSON in this exact format:
{{"relevance": "relevant" or "not_relevant", "score": 0.0-1.0, "reason": "one sentence"}}"""

    response = grade_llm.invoke(prompt)
    raw = response.content.strip()

    try:
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        relevance = parsed.get("relevance", "not_relevant")
        score     = float(parsed.get("score", 0.0))
        reason    = parsed.get("reason", "")
    except Exception:
        relevance = "not_relevant"
        score     = 0.0
        reason    = "parse error"

    print(f"[grade_relevance] {relevance} ({score:.2f}) — {reason}")

    stats = dict(state["stats"])
    if relevance == "relevant":
        stats["relevant"] += 1
    else:
        stats["skipped_irrelevant"] += 1

    return {"relevance": relevance, "relevance_score": score, "stats": stats}


# ─── Node 5: check_duplicate ────────────────────────────────────────────────
def check_duplicate(state: AgentState) -> dict:
    """
    Embed the article URL+title and query Pinecone.
    If cosine similarity ≥ DEDUP_THRESHOLD against any stored vector → duplicate.
    """
    article = state["current_article"]
    text_to_embed = f"{article['url']} {article['title']}"
    vector = embeddings.embed_query(text_to_embed)

    try:
        index = get_pinecone_index()
        result = index.query(vector=vector, top_k=1, include_metadata=False)
        matches = result.get("matches", [])
        is_dup = bool(matches and matches[0]["score"] >= DEDUP_THRESHOLD)
    except Exception as exc:
        print(f"[check_duplicate] Pinecone error (skipping dedup): {exc}")
        is_dup = False

    print(f"[check_duplicate] {'DUPLICATE' if is_dup else 'NEW'}")

    stats = dict(state["stats"])
    if is_dup:
        stats["skipped_duplicate"] += 1

    return {"is_duplicate": is_dup, "stats": stats}


# ─── Node 6: extract_insights ───────────────────────────────────────────────
def extract_insights(state: AgentState) -> dict:
    """Extract 3–5 concise bullet-point insights from the article."""
    prompt = f"""You are a research analyst extracting insights for a market research digest.

ARTICLE:
Title: {state['current_article']['title']}
URL: {state['current_article']['url']}
Content: {state['full_text'][:2000]}

TASK: Extract exactly 3-5 factual, specific insights from this article.
- Each insight must be a complete sentence
- Cite only facts explicitly stated in the article
- Focus on: announcements, data points, regulatory actions, product launches, strategic moves
- Do NOT include vague statements or your own opinions

Respond ONLY with a JSON array of strings:
["insight 1", "insight 2", "insight 3"]"""

    response = digest_llm.invoke(prompt)
    raw = response.content.strip()

    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        insights = json.loads(raw)
        if not isinstance(insights, list):
            insights = [str(insights)]
    except Exception:
        insights = [f"Could not parse insights from: {state['current_article']['title']}"]

    print(f"[extract_insights] Extracted {len(insights)} insights")
    return {"insights": insights}


# ─── Node 7: store_seen ─────────────────────────────────────────────────────
def store_seen(state: AgentState) -> dict:
    """Upsert the article embedding to Pinecone so future runs detect it as duplicate."""
    article = state["current_article"]
    text_to_embed = f"{article['url']} {article['title']}"
    vector = embeddings.embed_query(text_to_embed)

    # Create a stable ID from the URL
    doc_id = hashlib.md5(article["url"].encode()).hexdigest()

    try:
        index = get_pinecone_index()
        index.upsert(vectors=[{
            "id": doc_id,
            "values": vector,
            "metadata": {
                "url": article["url"],
                "title": article["title"],
                "seen_at": datetime.utcnow().isoformat(),
            }
        }])
        print(f"[store_seen] Stored: {doc_id[:8]}...")
    except Exception as exc:
        print(f"[store_seen] Pinecone error (continuing): {exc}")

    return {}


# ─── Node 8: add_to_digest ──────────────────────────────────────────────────
def add_to_digest(state: AgentState) -> dict:
    """Append this article's insights to the accumulated digest list."""
    item = {
        "title": state["current_article"]["title"],
        "url": state["current_article"]["url"],
        "relevance_score": state["relevance_score"],
        "insights": state["insights"],
    }
    digest_items = list(state["digest_items"]) + [item]

    stats = dict(state["stats"])
    stats["new"] += 1

    return {"digest_items": digest_items, "stats": stats}


# ─── Node 9: log_skip ───────────────────────────────────────────────────────
def log_skip(state: AgentState) -> dict:
    """Log that this article was skipped (irrelevant or duplicate)."""
    reason = "irrelevant" if state["relevance"] == "not_relevant" else "duplicate"
    print(f"[log_skip] Skipped ({reason}): {state['current_article']['title'][:50]}")
    return {}


# ─── Node 10: compile_digest ────────────────────────────────────────────────
def compile_digest(state: AgentState) -> dict:
    """
    Format all digest items into a final markdown string ready for Notion.
    Also generates an executive summary using the LLM.
    """
    items = state["digest_items"]
    stats = state["stats"]
    topic = state["topic"]
    run_date = datetime.utcnow().strftime("%Y-%m-%d")

    if not items:
        digest = f"# Market Research Digest — {topic}\n**Date:** {run_date}\n\n*No new relevant articles found today.*"
        return {"final_digest": digest}

    # Build raw digest
    article_sections = []
    for item in items:
        bullets = "\n".join(f"- {ins}" for ins in item["insights"])
        section = f"### [{item['title']}]({item['url']})\n*Relevance score: {item['relevance_score']:.2f}*\n\n{bullets}"
        article_sections.append(section)

    articles_text = "\n\n---\n\n".join(article_sections)

    # Generate executive summary with LLM
    summary_prompt = f"""You are writing an executive summary for a daily market research digest on: "{topic}"

Here are today's key findings:
{chr(10).join(f"- {ins}" for item in items for ins in item["insights"])}

Write a 2-3 sentence executive summary that captures the most important developments.
Be specific, factual, and concise."""

    summary_response = digest_llm.invoke(summary_prompt)
    exec_summary = summary_response.content.strip()

    digest = f"""# 📰 Market Research Digest: {topic}
**Date:** {run_date} | **Articles searched:** {stats['searched']} | **New insights:** {stats['new']} | **Skipped (irrelevant):** {stats['skipped_irrelevant']} | **Skipped (duplicate):** {stats['skipped_duplicate']}

---

## 🔍 Executive Summary

{exec_summary}

---

## 📄 Articles & Insights

{articles_text}

---
*Generated by AI Market Research Monitor · {datetime.utcnow().isoformat()} UTC*"""

    print(f"\n[compile_digest] Digest ready: {len(items)} articles, {sum(len(i['insights']) for i in items)} total insights")
    return {"final_digest": digest}


# ─── Routing functions ───────────────────────────────────────────────────────
def route_relevance(state: AgentState) -> Literal["check_duplicate", "log_skip", "pop_article"]:
    if state["relevance"] == "relevant":
        return "check_duplicate"
    return "log_skip" if state["articles_queue"] else "compile_digest"


def route_after_relevance_skip(state: AgentState) -> Literal["pop_article", "compile_digest"]:
    return "pop_article" if state["articles_queue"] else "compile_digest"


def route_duplicate(state: AgentState) -> Literal["extract_insights", "log_skip"]:
    return "log_skip" if state["is_duplicate"] else "extract_insights"


def route_after_duplicate_skip(state: AgentState) -> Literal["pop_article", "compile_digest"]:
    return "pop_article" if state["articles_queue"] else "compile_digest"


def route_after_add(state: AgentState) -> Literal["pop_article", "compile_digest"]:
    return "pop_article" if state["articles_queue"] else "compile_digest"


# ─── Build LangGraph ─────────────────────────────────────────────────────────
def build_agent() -> StateGraph:
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("search_web",       search_web)
    graph.add_node("pop_article",      pop_article)
    graph.add_node("fetch_article",    fetch_article)
    graph.add_node("grade_relevance",  grade_relevance)
    graph.add_node("log_skip",         log_skip)
    graph.add_node("check_duplicate",  check_duplicate)
    graph.add_node("extract_insights", extract_insights)
    graph.add_node("store_seen",       store_seen)
    graph.add_node("add_to_digest",    add_to_digest)
    graph.add_node("compile_digest",   compile_digest)

    # Linear start
    graph.add_edge(START,          "search_web")
    graph.add_edge("search_web",   "pop_article")
    graph.add_edge("pop_article",  "fetch_article")
    graph.add_edge("fetch_article","grade_relevance")

    # Conditional: relevant → check_duplicate | not_relevant → log_skip
    graph.add_conditional_edges(
        "grade_relevance",
        lambda s: "check_duplicate" if s["relevance"] == "relevant" else "log_skip_irrelevant",
        {"check_duplicate": "check_duplicate", "log_skip_irrelevant": "log_skip"}
    )

    # After irrelevant skip → next article or compile
    graph.add_conditional_edges(
        "log_skip",
        route_after_relevance_skip,
        {"pop_article": "pop_article", "compile_digest": "compile_digest"}
    )

    # Conditional: not duplicate → extract | duplicate → log_skip
    graph.add_conditional_edges(
        "check_duplicate",
        route_duplicate,
        {"extract_insights": "extract_insights", "log_skip": "log_skip"}
    )

    # Happy path: extract → store → add to digest
    graph.add_edge("extract_insights", "store_seen")
    graph.add_edge("store_seen",       "add_to_digest")

    # After adding to digest → next article or compile
    graph.add_conditional_edges(
        "add_to_digest",
        route_after_add,
        {"pop_article": "pop_article", "compile_digest": "compile_digest"}
    )

    graph.add_edge("compile_digest", END)

    return graph.compile()


# ─── Main entry point ────────────────────────────────────────────────────────
def run_monitor(topic: str) -> dict:
    """
    Run the Market Research Monitor for a given topic.
    Returns: {"digest": str, "stats": dict}
    """
    agent = build_agent()

    initial_state = AgentState(
        topic=topic,
        search_results=[],
        articles_queue=[],
        current_article=None,
        full_text="",
        relevance="",
        relevance_score=0.0,
        is_duplicate=False,
        insights=[],
        digest_items=[],
        final_digest="",
        stats={},
    )

    print(f"\n{'='*60}")
    print(f"  AI Market Research Monitor")
    print(f"  Topic: {topic}")
    print(f"  Time:  {datetime.utcnow().isoformat()} UTC")
    print(f"{'='*60}")

    result = agent.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"  Run complete!")
    print(f"  Stats: {result['stats']}")
    print(f"{'='*60}\n")

    return {
        "digest": result["final_digest"],
        "stats": result["stats"],
    }


if __name__ == "__main__":
    topic = os.environ.get("MONITOR_TOPIC", "AI regulation news Europe 2025")
    output = run_monitor(topic)
    print("\n--- FINAL DIGEST ---\n")
    print(output["digest"])
