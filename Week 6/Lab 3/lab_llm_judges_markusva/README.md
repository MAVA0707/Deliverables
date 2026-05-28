# Lab: LLMs grading LLMs

**Scenario chosen:** Option C, retail customer service chatbot.

A German online fashion retailer wants a chatbot that handles returns, product questions, and complaints. The model must stay helpful under pressure, give accurate policy answers, and not say anything that creates legal or reputational problems.

## Files

| File | What it is |
|---|---|
| `benchmark_audit.md` | 3 benchmark evaluation cards (Step 2) |
| `evaluation_design.md` | 5 evaluation prompts + 1 LLM-as-judge prompt with bias analysis (Steps 3-4) |
| `evaluation_memo.md` | 1-page client memo (Step 5) |
| `reflection.md` | Answers to the 3 reflection questions (Step 6) |
| `llm_judge_evaluation.py` | Python evaluation pipeline (Steps 7-11) |
| `evaluation_results.json` | Output from running the pipeline |
| `implementation_summary.md` | What was built and what was found (Steps 7-11) |

## How to run

1. Install dependencies: `pip install openai python-dotenv`
2. Create a `.env` file with `OPENAI_API_KEY=your_key_here`
3. Run: `python llm_judge_evaluation.py`

Results are written to `evaluation_results.json`.
