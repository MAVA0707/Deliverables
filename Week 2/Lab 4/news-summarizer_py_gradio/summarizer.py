"""News summarizer — orchestrates NewsAPI → OpenAI → Anthropic pipeline."""
import asyncio
from news_api       import NewsAPI
from llm_providers  import LLMProviders


class NewsSummarizer:
    """Summarize news articles using multiple LLM providers."""

    def __init__(self):
        self.news_api      = NewsAPI()
        self.llm_providers = LLMProviders()

    # ------------------------------------------------------------------
    # Single-article pipeline
    # ------------------------------------------------------------------

    def summarize_article(self, article: dict) -> dict:
        """
        Run the full pipeline for one article.

        Steps:
          1. Build a text snippet from the article fields.
          2. Ask OpenAI for a 2–3 sentence summary (Anthropic fallback).
          3. Ask Anthropic for sentiment analysis of the summary.

        Args:
            article: Dict with keys title, description, content,
                     url, source, published_at.

        Returns:
            Dict with title, source, url, summary, sentiment, published_at.
        """
        title = article.get("title") or "(no title)"
        print(f"\nProcessing: {title[:70]}…")

        article_text = (
            f"Title: {article['title']}\n"
            f"Description: {article['description']}\n"
            f"Content: {(article['content'] or '')[:500]}"
        )

        # ---- Step 1: Summarisation (OpenAI primary, Anthropic fallback) ----
        summary_prompt = (
            f"Summarize this news article in 2–3 sentences:\n\n{article_text}"
        )
        try:
            print("  → Summarising with OpenAI…")
            summary = self.llm_providers.ask_openai(summary_prompt)
            print("  ✓ Summary generated")
        except Exception as exc:
            print(f"  ✗ OpenAI failed: {exc} — falling back to Anthropic…")
            summary = self.llm_providers.ask_anthropic(summary_prompt)
            print("  ✓ Summary generated (via fallback)")

        # ---- Step 2: Sentiment (Anthropic — better at nuance) ----
        sentiment_prompt = (
            f'Analyse the sentiment of this text: "{summary}"\n\n'
            "Provide:\n"
            "- Overall sentiment (positive / negative / neutral)\n"
            "- Confidence (0–100 %)\n"
            "- Key emotional tone\n\n"
            "Be concise (2–3 sentences)."
        )
        try:
            print("  → Analysing sentiment with Anthropic…")
            sentiment = self.llm_providers.ask_anthropic(sentiment_prompt)
            print("  ✓ Sentiment analysed")
        except Exception as exc:
            print(f"  ✗ Sentiment failed: {exc}")
            sentiment = "Unable to analyse sentiment."

        return {
            "title":        article["title"],
            "source":       article["source"],
            "url":          article["url"],
            "summary":      summary,
            "sentiment":    sentiment,
            "published_at": article["published_at"],
        }

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def process_articles(self, articles: list[dict]) -> list[dict]:
        """
        Process a list of articles sequentially.

        Args:
            articles: List of article dicts from NewsAPI.

        Returns:
            List of result dicts; failed articles are skipped.
        """
        results = []
        for article in articles:
            try:
                results.append(self.summarize_article(article))
            except Exception as exc:
                print(f"  ✗ Skipping article due to error: {exc}")
        return results

    # ------------------------------------------------------------------
    # Cost report (plain text for CLI; Gradio uses its own formatter)
    # ------------------------------------------------------------------

    def cost_report(self) -> str:
        """Return a plain-text cost summary string."""
        s = self.llm_providers.cost_tracker.get_summary()
        lines = [
            "=" * 60,
            "COST SUMMARY",
            "=" * 60,
            f"  Total requests : {s['total_requests']}",
            f"  Total cost     : ${s['total_cost']:.5f}",
            f"  Total tokens   : {s['total_input_tokens'] + s['total_output_tokens']:,}",
            f"    Input        : {s['total_input_tokens']:,}",
            f"    Output       : {s['total_output_tokens']:,}",
            f"  Avg cost/req   : ${s['average_cost']:.7f}",
            "=" * 60,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Async subclass
# ---------------------------------------------------------------------------

class AsyncNewsSummarizer(NewsSummarizer):
    """Process multiple articles concurrently using asyncio."""

    async def summarize_article_async(self, article: dict) -> dict:
        """Wrap the synchronous pipeline so it runs in a thread pool."""
        return await asyncio.to_thread(self.summarize_article, article)

    async def process_articles_async(
        self,
        articles:       list[dict],
        max_concurrent: int = 3,
    ) -> list[dict]:
        """
        Process articles with a concurrency cap.

        Args:
            articles:       Articles to process.
            max_concurrent: Maximum parallel workers.

        Returns:
            List of successfully processed results.
        """
        sem = asyncio.Semaphore(max_concurrent)

        async def _guarded(art):
            async with sem:
                return await self.summarize_article_async(art)

        raw    = await asyncio.gather(*[_guarded(a) for a in articles],
                                       return_exceptions=True)
        errors = [r for r in raw if isinstance(r, Exception)]
        if errors:
            print(f"⚠️  {len(errors)} article(s) failed during async processing.")
        return [r for r in raw if not isinstance(r, Exception)]


if __name__ == "__main__":
    summarizer = NewsSummarizer()
    print("Fetching articles…")
    articles = summarizer.news_api.fetch_top_headlines(
        category="technology", max_articles=2
    )
    if not articles:
        print("No articles fetched — check your NEWS_API_KEY.")
    else:
        results = summarizer.process_articles(articles)
        for i, r in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(f"{i}. {r['title']}")
            print(f"   Source: {r['source']}")
            print(f"\n   SUMMARY:\n   {r['summary']}")
            print(f"\n   SENTIMENT:\n   {r['sentiment']}")
        print(f"\n{summarizer.cost_report()}")
