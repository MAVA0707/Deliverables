# NormalObjects Lab 2 — Bloyce's Protocol (LangGraph + Streamlit UI)

Structured, rule-based complaint processor for the Downside Up Complaint Bureau, built with **LangGraph**.

---

## File Map

```
.
├── normalobjects_langgraph.ipynb   # Main notebook — full LangGraph implementation
├── app.py                          # Streamlit graphical interface
├── README.md                       # This file
└── lab_summary.md                  # LangGraph vs LangChain comparison  
```

---

## How to Run

### 1. Prerequisites

- Python 3.10+
- An OpenAI API key

### 2. Install dependencies

```bash
pip install langgraph langchain langchain-openai python-dotenv streamlit
```

### 3. Configure your API key

Create a `.env` file in the same directory as the notebook:

```
OPENAI_API_KEY=sk-...
```

### 4a. Run the Streamlit UI (recommended)

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Enter your OpenAI API key in the sidebar (or set it in `.env`), then submit a complaint.

### 4b. Open the notebook

```bash
jupyter notebook normalobjects_langgraph.ipynb
```

Run all cells from top to bottom (`Cell → Run All`).

---

## Workflow

The system enforces this strict linear pipeline — no step can be skipped:

```
intake → validate → investigate → resolve → close
                ↘
              rejected  (invalid complaints exit here)
```

| Node | What it does |
|------|-------------|
| `intake` | Categorises complaint; flags missing details (who/what/when/where) |
| `validate` | Applies category-specific rules; rejects if insufficient detail |
| `investigate` | Produces documented evidence report before any resolution |
| `resolve` | Generates specific resolution + HIGH/MEDIUM/LOW effectiveness rating |
| `close` | Logs outcome; schedules 30-day follow-up for LOW-rated resolutions |
| `rejected` | Terminal node; surfaces rejection reason to the operator |

---

## Categories supported

| Category | Trigger |
|----------|---------|
| `portal` | Portal timing, location, or behaviour issues |
| `monster` | Creature behaviour or interactions |
| `psychic` | Psychic ability limitations or malfunctions |
| `environmental` | Electricity, weather, or physical environment |
| `other` | Anything else — auto-escalated for manual review |

---

## Test complaints included

The notebook ships with five test cases:

1. **Portal** — valid, rich detail → full happy path
2. **Monster** — valid, rich detail → full happy path (escalated to specialist team)
3. **Psychic** — valid, rich detail → full happy path
4. **Environmental** — valid → full happy path (escalated to specialist team)
5. **Invalid** — missing who/when/where → rejected at validate

---

## Extension ideas (optional)

- Add retry logic to re-run failed LLM calls
- Persist `ComplaintState` to SQLite between sessions
- Add a human-in-the-loop approval gate before `resolve`
- Build a Gradio or Streamlit front-end for complaint submission
