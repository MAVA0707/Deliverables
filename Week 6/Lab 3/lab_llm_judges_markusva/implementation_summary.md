# Implementation summary

## What was built

The pipeline in `llm_judge_evaluation.py` does 3 things in sequence. First it sends each test prompt to gpt-4o-mini with a system prompt that defines the chatbot's role and return policy. Then it sends the chatbot's response to a second gpt-4o-mini call, the judge, which scores the response against a custom rubric. Finally it saves all scores, reasoning, token counts, and cost estimates to `evaluation_results.json`.

The judge uses `response_format={"type": "json_object"}` to force structured output, which avoids JSON parsing errors. Temperature is set to 0 for the judge and 0.3 for the tested model. Each test case runs sequentially, not in parallel, to keep the code simple and readable.

## Key findings

4 of 5 test cases passed (score 1). The failure was TC03, the allergen question. The model stated "100% linen, no polyester" with no uncertainty and no caveat, despite having no access to product data. This is the most serious finding: hallucination on a health-relevant question is not acceptable in production, and it can't be fixed with prompt tweaks alone. The chatbot needs either (a) access to the actual product database, or (b) a hard rule that blocks it from stating material composition at all.

The angry customer prompt (TC02) was the most interesting success. The response was specific, avoided the template apology phrase, and correctly declined to promise a refund. This is the kind of judgment that's hard to get right with simpler models.

Total estimated cost for 5 test cases: $0.000874, roughly 0.09 cents. At that rate, running 1,000 evaluation cases would cost under $0.20. That's cheap enough to run regularly as part of a CI/CD pipeline if the client wanted ongoing quality monitoring.

## Limitations of the implementation

The biggest limitation is that judge and tested model are the same (gpt-4o-mini). The judge might be biased toward the style of outputs it would itself produce. A stricter setup would use a different model as the judge.

Each prompt was only run once in the sample results. In a real evaluation I'd run 3 times and average, because LLM judge scores can vary by ±1 between runs even at temperature 0. That's why the `reflection.md` recommends reading averages rather than individual scores.
