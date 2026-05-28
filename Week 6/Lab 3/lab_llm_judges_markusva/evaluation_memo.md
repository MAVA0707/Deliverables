# Evaluation memo

**TO:** Fashion Retail GmbH, Customer Experience Team
**FROM:** LLM Consulting Student
**DATE:** May 25, 2025
**SUBJECT:** LLM Evaluation Results, Customer Service Chatbot

---

## Executive summary

We tested 2 models (gpt-4o-mini and a smaller baseline) on 5 custom evaluation prompts covering the main scenarios your chatbot will face: return questions, angry complaints, product detail queries, discount code issues, and competitor comparisons. Under these test conditions, gpt-4o-mini handled 4 of the 5 scenarios reliably. The product detail question (allergen scenario) was a consistent weak point for both models.

---

## Methodology

We did not use general-purpose benchmarks like MT-Bench or HellaSwag. After reviewing these, we found them either saturated (most models score 90%+) or too generic for your use case. Instead, we wrote 5 custom prompts based on real customer service scenarios. Each prompt was evaluated by a second LLM acting as a judge, using a scoring rubric with 3-4 criteria per prompt.

We used gpt-4o-mini as both the tested model and the judge model. Temperature was set to 0 for the judge to reduce variability. Each prompt was run 3 times and scores were averaged to account for judge inconsistency.

Models tested: gpt-4o-mini (primary), gpt-3.5-turbo (baseline comparison).

---

## Results

gpt-4o-mini scored above the pass threshold (score 1 out of 1) on 4 of the 5 prompts. It handled the angry customer prompt well: the response was calm, included a specific apology, and offered a concrete escalation path. The return question and competitor comparison were handled correctly in all 3 runs.

The baseline (gpt-3.5-turbo) passed 3 of the 5. It struggled with the angry customer prompt, producing a response that included "we apologize for any inconvenience" (flagged as a template phrase by the judge) and no concrete next step.

Both models failed the allergen prompt at least once by stating a specific material composition without access to product data. gpt-4o-mini failed it in 1 of 3 runs; gpt-3.5-turbo failed in 2 of 3.

---

## Caveats and limitations

These results apply only to these 5 prompts, run on these 2 models, in this test setup. Five prompts is not a representative sample. Real production traffic will include questions we didn't anticipate, non-standard phrasing, multilingual inputs, and multi-turn conversations. Our evaluation was single-turn only.

The judge model (gpt-4o-mini) may have biases toward informal English phrasing. Responses with more formal or German-influenced tone may be scored lower even if they'd be appropriate for your brand. We noticed some score variance across runs (sometimes 0, sometimes 1 for the same response), which means individual scores should be read with caution. Averages are more reliable.

We can't rule out that these models were trained on similar customer service dialogues, which could inflate their apparent skill.

---

## Recommendation

Under these test conditions, for this task, gpt-4o-mini is the stronger choice. It passed 4 of 5 prompts consistently and showed better tone control on the complaint scenario. We'd suggest moving forward with gpt-4o-mini as the base model, with one hard constraint: the chatbot must never answer allergen or material composition questions without verified product data from your database. This is not a model failure we can prompt-engineer away. It needs a system-level fix (either block the model from answering these questions, or give it access to accurate product data at inference time).

---

## Additional metrics

Average response time: ~1.2 seconds per call with gpt-4o-mini. Total token cost for this 5-prompt evaluation (3 runs each): approximately $0.003. At production scale (assume 10,000 conversations/day, average 4 turns), monthly token cost is roughly $150-200 at current gpt-4o-mini pricing. That estimate is rough and depends heavily on average message length. Environmental cost is not something we measured here, but Anthropic and OpenAI both publish emissions estimates per token if you need that for ESG reporting.
