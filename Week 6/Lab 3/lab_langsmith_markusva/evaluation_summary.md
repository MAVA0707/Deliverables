# Evaluation summary

I evaluated gpt-5.4-mini ($0.75/1M input, $4.50/1M output) on a custom dataset of 15 German learner sentences using two LangSmith experiments: one at temperature=0 and one at temperature=0.7. Each example contains one grammar error (or none), and the task is to identify it and provide a corrected sentence. Two evaluators ran on every example: a correctness judge (Claude Haiku via openevals) and a custom "correction completeness" evaluator that checks whether the model actually writes the corrected German sentence when one is needed. Both temperature settings scored well on unambiguous errors like verb-second violations and sein/haben selection, but struggled on 3 nuanced cases where the reference answer says "technically correct, but..." — the model gave a flat "Correct" without the qualifying remark. Temperature=0 missed those cases cleanly; temperature=0.7 occasionally added unsolicited caveats that the judge rewarded, giving it a slight edge on those examples but at the cost of one extra hallucinated correction elsewhere. Correction completeness was 14/15 for both runs, with the failure on example 3 (separable verb negation) where the model described the rule without writing the corrected sentence explicitly.

**Key metrics (estimated from run):**

| Run | Correctness (mean) | Correction completeness | Cost per 15 examples |
|---|---|---|---|
| gpt-5.4-mini temp=0 | ~0.80 | ~0.93 | ~$0.00054 |
| gpt-5.4-mini temp=0.7 | ~0.82 | ~0.93 | ~$0.00054 |

**Main failure pattern:** Nuanced "both forms acceptable" cases (examples 5, 10, 13). The judge scores 0 when the model says "Correct" without the qualifier, because the reference answer always includes the caveat.

**Limitations:** 15 examples written by a learner (me), so the reference answers carry my own gaps. The judge uses Claude Haiku, which may also have imperfect German grammar knowledge. Two temperature runs on the same model don't test different capabilities, just output variance.

**One recommendation:** For a B1 tutoring product, temperature=0 is the safer default — more predictable, same cost, and the correctness gap vs. temp=0.7 is within noise at n=15. Run a larger test (100+ examples) before adjusting temperature.
