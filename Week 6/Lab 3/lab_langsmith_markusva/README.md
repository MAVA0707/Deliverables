# lab_langsmith

LangSmith evaluation lab — German grammar correction domain, using gpt-5.4-mini.

## Domain

15 German learner sentences, each with one grammar error (or none). The task: identify whether the sentence is correct, and if not, fix it with a short explanation. Errors cover verb-second rule, dative/accusative mix-ups, auxiliary selection (sein vs. haben), adjective endings, and separable verbs.

## Model

**gpt-5.4-mini** — OpenAI's current high-volume mini model (released March 17, 2026).  
Pricing: $0.75/1M input tokens, $4.50/1M output tokens. 400K context window. Knowledge cutoff: Aug 31, 2025.

A/B comparison: temperature=0 (deterministic) vs temperature=0.7 (more varied phrasing), same model and dataset.

## Files

| File | Purpose |
|---|---|
| `lab_langsmith_evaluation.ipynb` | Main notebook: dataset creation, target functions, evaluators, A/B temperature comparison, analysis |
| `evaluation_summary.md` | One-paragraph eval summary with metrics table |
| `optimization_summary.md` | One-paragraph cost/performance recommendation |

## How to run

1. Create a `.env` file with:
   ```
   LANGSMITH_API_KEY=your_key
   OPENAI_API_KEY=your_key
   ANTHROPIC_API_KEY=your_key
   ```
2. Install dependencies:
   ```
   pip install langsmith openai openevals python-dotenv
   ```
3. Run `lab_langsmith_evaluation.ipynb` top to bottom.

The notebook creates the dataset on first run (skips if it already exists), runs both temperature experiments, and prints a summary table with cost estimates.

## LangSmith

- **Project:** `german-grammar-eval`
- **Dataset:** `german-grammar-correction-v1`
- **Experiments:** `gpt-5.4-mini-temp0-*` and `gpt-5.4-mini-temp07-*`
- **Endpoint:** EU (`https://eu.api.smith.langchain.com`)
