"""Unit tests for news summarizer — run with: pytest test_summarizer.py -v"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from llm_providers import CostTracker, count_tokens, LLMProviders
from news_api      import NewsAPI
from summarizer    import NewsSummarizer


# ---------------------------------------------------------------------------
# CostTracker
# ---------------------------------------------------------------------------

class TestCostTracker:
    """Tests for cost tracking functionality."""

    def test_track_single_request(self):
        """Cost must be positive and accumulated correctly."""
        tracker = CostTracker()
        cost = tracker.track_request("openai", "gpt-4o-mini", 100, 500)
        assert cost > 0
        assert abs(tracker.total_cost - cost) < 1e-9
        assert len(tracker.requests) == 1

    def test_get_summary_aggregates_correctly(self):
        """Summary must aggregate tokens and cost across requests."""
        tracker = CostTracker()
        tracker.track_request("openai",    "gpt-4o-mini",               100, 200)
        tracker.track_request("anthropic", "claude-opus-4-7", 150, 300)
        s = tracker.get_summary()
        assert s["total_requests"]      == 2
        assert s["total_cost"]          >  0
        assert s["total_input_tokens"]  == 250
        assert s["total_output_tokens"] == 500

    def test_budget_check_passes_within_limit(self):
        """No exception when cost is below daily budget."""
        tracker = CostTracker()
        tracker.track_request("openai", "gpt-4o-mini", 100, 100)
        tracker.check_budget(10.00)  # should not raise

    def test_budget_check_raises_when_exceeded(self):
        """RuntimeError raised when cost exceeds daily budget."""
        tracker = CostTracker()
        tracker.total_cost = 15.00
        with pytest.raises(RuntimeError, match="exceeded"):
            tracker.check_budget(10.00)

    def test_average_cost_calculation(self):
        """Average cost must equal total cost divided by request count."""
        tracker = CostTracker()
        tracker.track_request("openai", "gpt-4o-mini", 100, 100)
        tracker.track_request("openai", "gpt-4o-mini", 200, 200)
        s = tracker.get_summary()
        assert abs(s["average_cost"] - s["total_cost"] / 2) < 1e-9


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

class TestTokenCounting:
    """Tests for the count_tokens helper."""

    def test_returns_positive_integer(self):
        """Token count must be a positive integer."""
        n = count_tokens("Hello, how are you?")
        assert isinstance(n, int)
        assert n > 0

    def test_longer_text_has_more_tokens(self):
        """Longer text should produce a higher token count."""
        short = count_tokens("Hi")
        long  = count_tokens("Hi " * 50)
        assert long > short


# ---------------------------------------------------------------------------
# NewsAPI
# ---------------------------------------------------------------------------

class TestNewsAPI:
    """Tests for NewsAPI integration."""

    def _mock_response(self, articles):
        mock = Mock()
        mock.status_code = 200
        mock.raise_for_status = Mock()
        mock.json.return_value = {"status": "ok", "articles": articles}
        return mock

    def test_fetch_returns_processed_articles(self):
        """Fetched articles should be mapped to the expected dict shape."""
        raw = [{
            "title":       "Test Article",
            "description": "Desc",
            "content":     "Body",
            "url":         "https://example.com",
            "source":      {"name": "Test Source"},
            "publishedAt": "2026-04-30",
        }]
        with patch("requests.get", return_value=self._mock_response(raw)):
            api  = NewsAPI()
            arts = api.fetch_top_headlines(max_articles=1)

        assert len(arts)         == 1
        assert arts[0]["title"]  == "Test Article"
        assert arts[0]["source"] == "Test Source"
        assert arts[0]["url"]    == "https://example.com"

    def test_network_error_returns_empty_list(self):
        """A requests exception should return an empty list, not raise."""
        import requests as req_lib
        with patch("requests.get",
                   side_effect=req_lib.RequestException("timeout")):
            api  = NewsAPI()
            arts = api.fetch_top_headlines(max_articles=1)
        assert arts == []

    def test_api_error_status_returns_empty_list(self):
        """A non-ok API status should return an empty list."""
        mock = Mock()
        mock.raise_for_status = Mock()
        mock.json.return_value = {"status": "error", "message": "bad key"}
        with patch("requests.get", return_value=mock):
            api  = NewsAPI()
            arts = api.fetch_top_headlines(max_articles=1)
        assert arts == []


# ---------------------------------------------------------------------------
# LLMProviders
# ---------------------------------------------------------------------------

class TestLLMProviders:
    """Tests for the multi-provider LLM client."""

    def _openai_mock(self, text="OpenAI response"):
        client = MagicMock()
        resp   = MagicMock()
        resp.choices = [MagicMock(message=MagicMock(content=text))]
        client.chat.completions.create.return_value = resp
        return client

    def _anthropic_mock(self, text="Anthropic response"):
        client = MagicMock()
        resp   = MagicMock()
        resp.content = [MagicMock(text=text)]
        client.messages.create.return_value = resp
        return client

    def test_ask_openai_returns_response(self):
        """ask_openai should return the model's text."""
        p = LLMProviders()
        p.openai_client = self._openai_mock("Python is great!")
        assert p.ask_openai("What is Python?") == "Python is great!"

    def test_ask_anthropic_returns_response(self):
        """ask_anthropic should return the model's text."""
        p = LLMProviders()
        p.anthropic_client = self._anthropic_mock("Very positive.")
        assert p.ask_anthropic("Analyse sentiment.") == "Very positive."

    def test_fallback_triggers_when_openai_fails(self):
        """If OpenAI raises, the fallback should use Anthropic."""
        p = LLMProviders()
        p.openai_client    = MagicMock()
        p.openai_client.chat.completions.create.side_effect = RuntimeError("quota")
        p.anthropic_client = self._anthropic_mock("Fallback response")

        result = p.ask_with_fallback("Some question", primary="openai")
        assert result["provider"] == "anthropic"
        assert result["response"] == "Fallback response"

    def test_fallback_raises_when_all_fail(self):
        """RuntimeError raised when both providers fail."""
        p = LLMProviders()
        p.openai_client    = MagicMock()
        p.anthropic_client = MagicMock()
        p.openai_client.chat.completions.create.side_effect    = RuntimeError("fail")
        p.anthropic_client.messages.create.side_effect         = RuntimeError("fail")

        with pytest.raises(RuntimeError, match="All providers failed"):
            p.ask_with_fallback("question")


# ---------------------------------------------------------------------------
# NewsSummarizer
# ---------------------------------------------------------------------------

class TestNewsSummarizer:
    """Tests for the full summariser pipeline."""

    def _patched_summarizer(self, summary="Great summary", sentiment="Positive."):
        s = NewsSummarizer()
        s.llm_providers.openai_client    = MagicMock()
        s.llm_providers.anthropic_client = MagicMock()

        oa_resp = MagicMock()
        oa_resp.choices = [MagicMock(message=MagicMock(content=summary))]
        s.llm_providers.openai_client.chat.completions.create.return_value = oa_resp

        an_resp = MagicMock()
        an_resp.content = [MagicMock(text=sentiment)]
        s.llm_providers.anthropic_client.messages.create.return_value = an_resp

        return s

    def test_initialization(self):
        """Summarizer must expose news_api and llm_providers."""
        s = NewsSummarizer()
        assert s.news_api      is not None
        assert s.llm_providers is not None

    def test_summarize_article_returns_expected_fields(self):
        """Result dict must contain all required keys with correct values."""
        s = self._patched_summarizer("Great summary", "Positive 90%.")
        article = {
            "title":        "AI Breakthrough",
            "description":  "Scientists announce major AI achievement.",
            "content":      "Details here…",
            "url":          "https://example.com/ai",
            "source":       "Tech Times",
            "published_at": "2026-04-30",
        }
        result = s.summarize_article(article)
        assert result["title"]    == "AI Breakthrough"
        assert result["summary"]  == "Great summary"
        assert "Positive" in result["sentiment"]
        assert result["source"]   == "Tech Times"

    def test_process_articles_skips_failures(self):
        """Failed articles should be skipped; others should still be returned."""
        s = NewsSummarizer()
        # Make summarize_article raise on first call, succeed on second
        call_count = {"n": 0}
        original   = s.summarize_article

        def patched(article):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("simulated failure")
            return {"title": article["title"], "summary": "ok",
                    "sentiment": "neutral", "source": "", "url": "",
                    "published_at": ""}

        s.summarize_article = patched
        articles = [{"title": "A"}, {"title": "B"}]
        results  = s.process_articles(articles)
        assert len(results) == 1
        assert results[0]["title"] == "B"
