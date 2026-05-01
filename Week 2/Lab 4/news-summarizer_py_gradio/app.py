"""
app.py — Gradio browser interface for the News Summarizer.

Run with:
    python app.py

Then open http://localhost:7860 in your browser.
"""
import gradio as gr
from summarizer import NewsSummarizer

# ---------------------------------------------------------------------------
# One shared summarizer instance per server session
# ---------------------------------------------------------------------------
summarizer = NewsSummarizer()

CATEGORIES = ["technology", "business", "health", "general", "science", "sports"]


# ---------------------------------------------------------------------------
# Core processing function called by Gradio
# ---------------------------------------------------------------------------

def run_summarizer(
    category:     str,
    num_articles: int,
    openai_key:   str,
    anthropic_key: str,
    news_key:     str,
) -> tuple[str, str]:
    """
    Fetch and process articles, returning (results_markdown, cost_text).

    Args:
        category:      News category to fetch.
        num_articles:  Number of articles to process (1–10).
        openai_key:    OpenAI API key (overrides .env if provided).
        anthropic_key: Anthropic API key (overrides .env if provided).
        news_key:      NewsAPI key (overrides .env if provided).

    Returns:
        Tuple of (formatted results markdown string, cost summary string).
    """
    import os

    # Allow users to supply keys directly in the UI (override .env)
    if openai_key.strip():
        os.environ["OPENAI_API_KEY"] = openai_key.strip()
    if anthropic_key.strip():
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key.strip()
    if news_key.strip():
        os.environ["NEWS_API_KEY"] = news_key.strip()

    # Re-initialise so the new keys are picked up
    global summarizer
    from config import Config
    Config.OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY")
    Config.ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    Config.NEWS_API_KEY      = os.environ.get("NEWS_API_KEY")
    summarizer = NewsSummarizer()

    # Validate keys are present
    missing = [
        name for name, val in [
            ("OPENAI_API_KEY",    Config.OPENAI_API_KEY),
            ("ANTHROPIC_API_KEY", Config.ANTHROPIC_API_KEY),
            ("NEWS_API_KEY",      Config.NEWS_API_KEY),
        ] if not val
    ]
    if missing:
        return (
            f"❌ Missing API keys: {', '.join(missing)}\n\n"
            "Please fill in your API keys in the **API Keys** tab.",
            "",
        )

    # Fetch articles
    articles = summarizer.news_api.fetch_top_headlines(
        category=category,
        max_articles=int(num_articles),
    )

    if not articles:
        return (
            "❌ No articles returned. Check your NewsAPI key or try a different category.",
            "",
        )

    # Process articles
    results = summarizer.process_articles(articles)

    if not results:
        return "❌ All articles failed to process.", ""

    # Format results as Markdown
    md_parts = [f"# 📰 News Summary — {category.capitalize()}\n"]
    for i, r in enumerate(results, 1):
        md_parts.append(f"---\n### {i}. {r['title']}")
        md_parts.append(f"**Source:** {r['source']}  |  **Published:** {r['published_at']}")
        md_parts.append(f"🔗 [{r['url']}]({r['url']})\n")
        md_parts.append(f"**📝 Summary**\n\n{r['summary']}\n")
        md_parts.append(f"**🎭 Sentiment**\n\n{r['sentiment']}\n")

    results_md = "\n".join(md_parts)
    cost_text  = summarizer.cost_report()

    return results_md, cost_text


# ---------------------------------------------------------------------------
# Build the Gradio interface
# ---------------------------------------------------------------------------

def build_ui() -> gr.Blocks:
    """Construct and return the Gradio Blocks UI."""

    with gr.Blocks(
        title="📰 News Summarizer",
        theme=gr.themes.Soft(),
        css="""
            .header  { text-align: center; padding: 1rem 0; }
            .cost-box { font-family: monospace; font-size: 0.85rem; }
        """,
    ) as demo:

        # ── Header ──────────────────────────────────────────────────────
        gr.Markdown(
            """
            <div class="header">
                <h1>📰 News Summarizer</h1>
                <p>Fetch live headlines → summarise with <b>OpenAI</b>
                → analyse sentiment with <b>Anthropic Claude</b></p>
            </div>
            """,
            elem_classes="header",
        )

        with gr.Tabs():

            # ── Tab 1: Run ───────────────────────────────────────────────
            with gr.Tab("🚀 Run"):
                with gr.Row():
                    with gr.Column(scale=1):
                        category = gr.Dropdown(
                            choices=CATEGORIES,
                            value="technology",
                            label="News Category",
                        )
                        num_articles = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=3,
                            step=1,
                            label="Number of Articles",
                        )
                        run_btn = gr.Button(
                            "▶ Fetch & Summarise",
                            variant="primary",
                            size="lg",
                        )
                        gr.Markdown(
                            "_Articles are fetched live from NewsAPI, "
                            "summarised by GPT-4o-mini, and analysed "
                            "by Claude Opus 4.7._"
                        )

                    with gr.Column(scale=3):
                        results_output = gr.Markdown(
                            value="Results will appear here after you click **Fetch & Summarise**.",
                            label="Results",
                        )

                cost_output = gr.Textbox(
                    label="💰 Cost Summary",
                    lines=10,
                    interactive=False,
                    elem_classes="cost-box",
                )

            # ── Tab 2: API Keys ──────────────────────────────────────────
            with gr.Tab("🔑 API Keys"):
                gr.Markdown(
                    "Enter your API keys here. They are used only for this "
                    "session and are **never stored**. Alternatively, set them "
                    "in a `.env` file before starting the app."
                )
                openai_key = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="sk-…",
                    type="password",
                )
                anthropic_key = gr.Textbox(
                    label="Anthropic API Key",
                    placeholder="sk-ant-…",
                    type="password",
                )
                news_key = gr.Textbox(
                    label="NewsAPI Key",
                    placeholder="abc123…",
                    type="password",
                )
                gr.Markdown(
                    "Get your keys at: "
                    "[OpenAI](https://platform.openai.com) · "
                    "[Anthropic](https://console.anthropic.com) · "
                    "[NewsAPI](https://newsapi.org)"
                )

            # ── Tab 3: About ─────────────────────────────────────────────
            with gr.Tab("ℹ️ About"):
                gr.Markdown(
                    """
                    ## How it works

                    1. **Fetch** — pulls top headlines from [NewsAPI](https://newsapi.org)
                    2. **Summarise** — sends each article to **GPT-4o-mini** for a 2–3 sentence summary
                    3. **Sentiment** — passes the summary to **Claude Opus 4.7** for nuanced sentiment analysis
                    4. **Fallback** — if OpenAI fails, Anthropic handles both steps automatically
                    5. **Cost tracking** — every token is counted and displayed in the cost summary

                    ## Estimated costs

                    | Articles | Est. cost |
                    |---|---|
                    | 3  | ~$0.004 |
                    | 5  | ~$0.007 |
                    | 10 | ~$0.013 |

                    ## File structure

                    ```
                    news-summarizer/
                    ├── app.py            ← this Gradio interface
                    ├── config.py         ← environment & model config
                    ├── news_api.py       ← NewsAPI client
                    ├── llm_providers.py  ← OpenAI + Anthropic + fallback
                    ├── summarizer.py     ← pipeline orchestration
                    ├── test_summarizer.py← unit tests
                    ├── requirements.txt
                    └── .env              ← your API keys (never commit!)
                    ```
                    """
                )

        # ── Wire up the button ───────────────────────────────────────────
        run_btn.click(
            fn=run_summarizer,
            inputs=[category, num_articles, openai_key, anthropic_key, news_key],
            outputs=[results_output, cost_output],
        )

    return demo


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ui = build_ui()
    ui.launch(
        server_name="0.0.0.0",   # accessible on the local network
        server_port=7860,
        share=False,              # set True to get a public gradio.live link
        show_error=True,
    )
