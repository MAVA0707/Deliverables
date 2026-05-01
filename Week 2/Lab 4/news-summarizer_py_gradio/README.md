# 📰 News Summarizer — Multi-Provider Edition

A production-ready news analysis pipeline with a browser interface built with Gradio.
Fetches live headlines, summarises them with OpenAI, and analyses sentiment with Anthropic Claude —
with automatic fallback, rate limiting, and cost tracking built in.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude%203.5%20Sonnet-purple)

---

## What the Project Does

For every article the pipeline runs three steps:

1. **Fetch** — pulls top headlines from [NewsAPI](https://newsapi.org) by category
2. **Summarise** — sends the article to **GPT-4o-mini** and gets a 2–3 sentence summary
3. **Analyse** — passes the summary to **Claude 3.5 Sonnet** for sentiment analysis (positive / negative / neutral + confidence + emotional tone)

Everything is accessible through a clean browser UI — no terminal required after startup.

### Key features

| Feature | Details |
|---|---|
| **Browser UI** | Gradio interface at `http://localhost:7860` |
| **Fallback logic** | If OpenAI fails, Anthropic handles both steps automatically |
| **Rate limiting** | Each client sleeps between calls to stay within API quotas |
| **Cost tracking** | Every token counted; USD cost displayed after each run |
| **Budget guard** | Raises an error if cumulative cost exceeds `DAILY_BUDGET` |
| **Unit tests** | Full mock-based test suite — run with `pytest` |

---

## Project Structure

```
news-summarizer/
├── app.py              ← Gradio browser interface (start here)
├── config.py           ← Environment variables & model config
├── news_api.py         ← NewsAPI client with rate limiting
├── llm_providers.py    ← OpenAI + Anthropic + fallback + cost tracking
├── summarizer.py       ← Pipeline orchestration (sync + async)
├── test_summarizer.py  ← Unit tests
├── requirements.txt    ← Python dependencies
├── .env.example        ← API key template (safe to commit)
├── .env                ← Your real API keys (never commit!)
├── .gitignore
└── README.md
```

---

## Setup

### 1. Prerequisites

- Python 3.10 or newer
- API keys for:
  - [OpenAI](https://platform.openai.com) — paid, ~$0.15 / 1M input tokens (GPT-4o-mini)
  - [Anthropic](https://console.anthropic.com) — paid, ~$3.00 / 1M input tokens (Claude Opus 4.7)
  - [NewsAPI](https://newsapi.org) — free tier: 100 requests/day

### 2. Clone the repository

```bash
git clone https://github.com/your-username/news-summarizer.git
cd news-summarizer
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
NEWS_API_KEY=abc123...

ENVIRONMENT=development
MAX_RETRIES=3
REQUEST_TIMEOUT=30
DAILY_BUDGET=5.00
```

> ⚠️ `.env` is in `.gitignore` — never commit real API keys.

---

## How to Run

### Browser app (recommended)

```bash
python app.py
```

Then open **http://localhost:7860** in your browser.

The interface has three tabs:

| Tab | What you can do |
|---|---|
| 🚀 **Run** | Pick a category, choose how many articles, click **Fetch & Summarise** |
| 🔑 **API Keys** | Paste your keys directly in the browser — skips the need for a `.env` file |
| ℹ️ **About** | How the pipeline works, cost estimates, file structure |

> **Tip:** you can also set `share=True` in `app.py` to get a public `gradio.live` link
> and share the app with others without deploying a server.

### Command line (individual modules)

Each module can also be run directly:

```bash
python config.py        # validate API keys
python news_api.py      # fetch 3 sample articles
python llm_providers.py # test both LLM providers
python summarizer.py    # run the full pipeline on 2 articles
```

### Unit tests

```bash
pytest test_summarizer.py -v
```

---

## Example Output

**Browser — Run tab:**

```
📰 News Summary — Technology

---
### 1. OpenAI announces new reasoning model for enterprise use
**Source:** The Verge  |  **Published:** 2026-04-30T14:22:00Z
🔗 https://www.theverge.com/...

**📝 Summary**
OpenAI has released a new reasoning-focused model aimed at enterprise customers,
promising improved accuracy on complex multi-step tasks. The model is available
via API starting today with tiered pricing.

**🎭 Sentiment**
Overall sentiment: Positive (85% confidence). The tone is optimistic and
forward-looking, emphasising capability gains and business opportunity
without notable negative framing.
```

**Cost summary (bottom of Run tab):**

```
============================================================
COST SUMMARY
============================================================
  Total requests : 6
  Total cost     : $0.00762
  Total tokens   : 2,847
    Input        : 2,214
    Output       : 633
  Avg cost/req   : $0.0012700
============================================================
```

**Unit tests:**

```
PASSED  TestCostTracker::test_track_single_request
PASSED  TestCostTracker::test_get_summary_aggregates_correctly
PASSED  TestCostTracker::test_budget_check_passes_within_limit
PASSED  TestCostTracker::test_budget_check_raises_when_exceeded
PASSED  TestCostTracker::test_average_cost_calculation
PASSED  TestTokenCounting::test_returns_positive_integer
PASSED  TestTokenCounting::test_longer_text_has_more_tokens
PASSED  TestNewsAPI::test_fetch_returns_processed_articles
PASSED  TestNewsAPI::test_network_error_returns_empty_list
PASSED  TestNewsAPI::test_api_error_status_returns_empty_list
PASSED  TestLLMProviders::test_ask_openai_returns_response
PASSED  TestLLMProviders::test_ask_anthropic_returns_response
PASSED  TestLLMProviders::test_fallback_triggers_when_openai_fails
PASSED  TestLLMProviders::test_fallback_raises_when_all_fail
PASSED  TestNewsSummarizer::test_initialization
PASSED  TestNewsSummarizer::test_summarize_article_returns_expected_fields
PASSED  TestNewsSummarizer::test_process_articles_skips_failures

17 passed in 0.51s
```

---

## Cost Analysis

### Per-article breakdown

| Step | Model | Avg input tokens | Avg output tokens | Cost per article |
|---|---|---|---|---|
| Summarisation | GPT-4o-mini | ~200 | ~70 | ~$0.000072 |
| Sentiment | Claude 3.5 Sonnet | ~120 | ~60 | ~$0.001260 |
| **Total per article** | | | | **~$0.00133** |

### Daily volume projections

| Articles/day | Est. daily cost | Monthly cost |
|---|---|---|
| 50 | $0.07 | $2.00 |
| 200 | $0.27 | $8.00 |
| 500 | $0.67 | $20.00 |
| 1,000 | $1.33 | $40.00 |

All scenarios fit comfortably within the default `DAILY_BUDGET` of **$5.00**.

### Cost optimisation tips

- **Swap sentiment model** — using `claude-haiku` instead of Claude 3.5 Sonnet cuts Anthropic costs by ~15×
- **Truncate content** — the pipeline already caps article content at 500 characters; lowering this reduces input tokens further
- **Cache results** — store summaries in a database and skip articles already processed
- **Batch summarisation** — send multiple article snippets in one OpenAI call to reduce overhead

---

## Notes

- NewsAPI free tier truncates the `content` field at ~200 characters. The pipeline handles this gracefully by falling back to the `description` field.
- API keys entered in the browser **API Keys** tab are applied for the current session only and are never stored to disk.
- If both providers fail for a given article, the pipeline logs the error and continues with the next article rather than crashing.
