# 📰 News Summarizer — Multi-Provider API Lab

A production-ready news analysis pipeline that fetches live articles, generates
summaries with OpenAI, and runs sentiment analysis with Anthropic Claude — with
automatic fallback, rate limiting, and cost tracking built in.

---

## What the Project Does

The pipeline runs three steps for every article:

1. **Fetch** — pulls top headlines from [NewsAPI](https://newsapi.org) by category (technology, business, health, etc.)
2. **Summarise** — sends the article to **OpenAI GPT-4o-mini** and gets a 2–3 sentence summary
3. **Analyse** — passes the summary to **Anthropic Claude** for nuanced sentiment analysis (positive / negative / neutral + confidence + emotional tone)

Additional production features:

| Feature | How it works |
|---|---|
| **Fallback logic** | If OpenAI fails, Anthropic handles both summarisation and sentiment automatically |
| **Rate limiting** | Each client sleeps between calls to stay within API quotas |
| **Cost tracking** | Every token is counted; total USD cost is reported after each run |
| **Budget guard** | Raises an error if cumulative cost exceeds `DAILY_BUDGET` (default $5.00) |
| **Async mode** | `AsyncNewsSummarizer` processes up to N articles concurrently using `asyncio` |
| **Unit tests** | Full mock-based test suite covering all major classes |

---

## Project Structure

```
news-summarizer/
├── news_summarizer_lab.ipynb   # Complete lab — all parts in one notebook
├── .env                        # Your API keys (never commit this)
├── .env.example                # Safe template to commit
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── lab_summary.md              # Reflection paragraph
```

> All source code lives inside `news_summarizer_lab.ipynb` as clearly labelled
> cells (Parts 1–7). Each part maps to a standalone module that could be
> extracted to its own `.py` file for production use.

---

## Setup

### 1. Prerequisites

- Python 3.10 or newer
- API keys for:
  - [OpenAI](https://platform.openai.com) (paid, ~$0.15 / 1M input tokens for GPT-4o-mini)
  - [Anthropic](https://console.anthropic.com) (paid, ~$3.00 / 1M input tokens for Claude 3.5 Sonnet)
  - [NewsAPI](https://newsapi.org) (free tier: 100 requests/day)

### 2. Clone or download the repository

```bash
git clone https://github.com/your-username/news-summarizer.git
cd news-summarizer
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` contents:

```
openai>=1.12.0
anthropic>=0.18.0
requests>=2.31.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
tiktoken>=0.5.0
pytest>=7.4.0
```

### 4. Configure environment variables

Copy the example file and fill in your real keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
NEWS_API_KEY=abc123...

ENVIRONMENT=development
MAX_RETRIES=3
REQUEST_TIMEOUT=30
DAILY_BUDGET=5.00
```

> ⚠️ `.env` is listed in `.gitignore` — never commit real API keys.

---

## How to Run

Open the notebook and run cells top-to-bottom:

```bash
jupyter notebook news_summarizer_lab.ipynb
```

### Checkpoints

| Cell | What to expect |
|---|---|
| **Part 1 — Config** | `✓ Configuration validated for 'development' environment` |
| **Part 2 — NewsAPI** | 3 article titles printed with source and URL |
| **Part 3 — LLM Providers** | Short responses from both OpenAI and Anthropic + cost line |
| **Part 4 — Summariser** | Full pipeline on 2 articles with summary, sentiment, and cost table |
| **Part 5 — Async** | Uncomment `await demo_async()` to process 5 articles concurrently |
| **Part 6 — Tests** | All tests pass: `Results: 12/12 passed, 0 failed` |
| **Part 7 — Main app** | Edit `CATEGORY`, `NUM_ARTICLES`, `USE_ASYNC` at the top of the cell and run |

### Quick configuration (Part 7 cell)

```python
CATEGORY     = "technology"   # technology | business | health | general
NUM_ARTICLES = 3              # 1 – 10
USE_ASYNC    = False          # True → concurrent processing
```

---

## Example Output

```
================================================================================
NEWS SUMMARIZER — Multi-Provider Edition
================================================================================
Category : technology
Articles : 3

✓ Fetched 3 article(s) from NewsAPI

Processing: OpenAI announces new reasoning model for enterprise use…
  → Summarising with OpenAI…
    [OpenAI] 187→64 tokens | $0.000067
  ✓ Summary generated
  → Analysing sentiment with Anthropic…
    [Anthropic] 112→58 tokens | $0.001206
  ✓ Sentiment analysed

Processing: Apple unveils redesigned MacBook lineup at spring event…
  → Summarising with OpenAI…
    [OpenAI] 201→71 tokens | $0.000073
  ✓ Summary generated
  → Analysing sentiment with Anthropic…
    [Anthropic] 119→62 tokens | $0.001284
  ✓ Sentiment analysed

================================================================================
NEWS SUMMARY REPORT
================================================================================

1. OpenAI announces new reasoning model for enterprise use
   Source: The Verge  |  Published: 2026-04-30T14:22:00Z
   URL: https://www.theverge.com/...

   SUMMARY:
   OpenAI has released a new reasoning-focused model aimed at enterprise
   customers, promising improved accuracy on complex multi-step tasks.
   The model is available via API starting today with tiered pricing.

   SENTIMENT:
   Overall sentiment: Positive (85% confidence). The tone is optimistic
   and forward-looking, emphasising capability gains and business
   opportunity without notable negative framing.

   ----------------------------------------------------------------------------

================================================================================
COST SUMMARY
================================================================================
  Total requests : 6
  Total cost     : $0.00762
  Total tokens   : 2,847
    Input        : 2,214
    Output       : 633
  Avg cost/req   : $0.0012700
================================================================================

✓ Processing complete!
```

---

## Cost Analysis

### Per-request breakdown

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

All scenarios comfortably fit within the default `DAILY_BUDGET` of **$5.00**.

### Cost optimisation tips

- **Truncate content** — the pipeline already caps article content at 500 characters; lowering this further reduces input tokens.
- **Swap sentiment model** — using `claude-haiku` instead of `claude-3-5-sonnet` cuts Anthropic costs by ~15×.
- **Batch summarisation** — sending multiple article snippets in one OpenAI call reduces per-token overhead.
- **Cache results** — store summaries in a database; re-fetch only new articles.

---

## Running the Tests

```bash
# Option 1: run the test cell inside the notebook (Part 6)
# Option 2: extract and run with pytest
pytest test_summarizer.py -v
```

Expected output:

```
PASSED  TestCostTracker::test_track_single_request
PASSED  TestCostTracker::test_get_summary
PASSED  TestCostTracker::test_budget_ok
PASSED  TestCostTracker::test_budget_exceeded
PASSED  TestTokenCounting::test_count_tokens_basic
PASSED  TestNewsAPI::test_fetch_top_headlines_success
PASSED  TestNewsAPI::test_fetch_top_headlines_network_error
PASSED  TestLLMProviders::test_ask_openai
PASSED  TestLLMProviders::test_ask_anthropic
PASSED  TestLLMProviders::test_fallback_triggers_on_openai_failure
PASSED  TestNewsSummarizer::test_initialization
PASSED  TestNewsSummarizer::test_summarize_article

12 passed in 0.43s
```

---

## Notes

- NewsAPI free tier only returns full article content for headlines; the `content` field is truncated at 200 characters by the provider. The pipeline handles this gracefully.
- The async mode (`USE_ASYNC = True`) is useful when processing 10+ articles; for smaller batches the overhead is negligible.
- If both providers fail (e.g., both keys are invalid), the pipeline logs the error and skips that article rather than crashing.
