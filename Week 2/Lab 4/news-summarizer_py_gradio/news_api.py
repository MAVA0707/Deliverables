"""News API integration module with rate limiting."""
import time
import requests
from config import Config


class NewsAPI:
    """Fetch news articles from NewsAPI with built-in rate limiting."""

    def __init__(self):
        self.api_key      = Config.NEWS_API_KEY
        self.base_url     = "https://newsapi.org/v2"
        self.last_call    = 0.0
        self.min_interval = 60.0 / Config.NEWS_API_RPM  # seconds between calls

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _wait_if_needed(self):
        """Sleep if necessary to respect the NewsAPI rate limit."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            wait = self.min_interval - elapsed
            print(f"  ⏳ Rate-limiting NewsAPI — waiting {wait:.2f}s…")
            time.sleep(wait)
        self.last_call = time.time()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_top_headlines(
        self,
        category:     str = "technology",
        country:      str = "us",
        max_articles: int = 5,
    ) -> list[dict]:
        """
        Fetch top headlines from NewsAPI.

        Args:
            category:     News category (technology, business, health, general).
            country:      Two-letter country code (us, gb, de …).
            max_articles: Maximum number of articles to return.

        Returns:
            List of article dicts with keys:
            title, description, content, url, source, published_at.
        """
        self._wait_if_needed()

        params = {
            "apiKey":   self.api_key,
            "category": category,
            "country":  country,
            "pageSize": max_articles,
        }

        try:
            resp = requests.get(
                f"{self.base_url}/top-headlines",
                params=params,
                timeout=Config.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "ok":
                raise RuntimeError(f"NewsAPI error: {data.get('message')}")

            articles = [
                {
                    "title":        a.get("title", ""),
                    "description":  a.get("description", ""),
                    "content":      a.get("content", ""),
                    "url":          a.get("url", ""),
                    "source":       a.get("source", {}).get("name", "Unknown"),
                    "published_at": a.get("publishedAt", ""),
                }
                for a in data.get("articles", [])
            ]

            print(f"✓ Fetched {len(articles)} article(s) from NewsAPI")
            return articles

        except requests.RequestException as exc:
            print(f"✗ Error fetching news: {exc}")
            return []


if __name__ == "__main__":
    api = NewsAPI()
    articles = api.fetch_top_headlines(category="technology", max_articles=3)
    for i, art in enumerate(articles, 1):
        print(f"\n{i}. {art['title']}")
        print(f"   Source: {art['source']}")
        print(f"   URL:    {art['url']}")
