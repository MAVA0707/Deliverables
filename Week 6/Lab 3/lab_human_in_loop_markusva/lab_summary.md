# Lab summary

## Analysis

Human evaluation of the 5 chatbot responses confirmed the main finding from the automated LLM-as-judge run: TC03 (the allergen question) is a clear failure, and the other 4 responses are good. Human scores ranged from 2 to 7 out of 7, with an average of 5.8. Four responses scored 6 or 7 and were labelled "good." TC03 scored 2 and was labelled "weak" — not "bad," because the tone was fine, but the factual accuracy was 0 because the chatbot invented a material composition for a product it had no data on. For an allergy question, that's the kind of error that matters.

---

## Key metrics

| Record | Scenario | Accuracy (0–3) | Tone (0–2) | Helpfulness (0–2) | Total (0–7) | Label | LLM judge score |
|---|---|---|---|---|---|---|---|
| TC01 | Return question | 3 | 2 | 2 | 7 | good | 1 (pass) |
| TC02 | Angry complaint | 3 | 2 | 2 | 7 | good | 1 (pass) |
| TC03 | Allergen question | 0 | 2 | 0 | 2 | weak | 0 (fail) |
| TC04 | Discount code | 3 | 2 | 2 | 7 | good | 1 (pass) |
| TC05 | Competitor comparison | 3 | 2 | 1 | 6 | good | 1 (pass) |

**Average human total score:** 5.8 / 7
**Human pass rate (6–7):** 4 / 5 (80%)
**LLM judge pass rate:** 4 / 5 (80%)

---

## Agreement between human and LLM judge

The human and the automated judge agreed on every case: both flagged TC03 as the only failure. The human score for TC05 was slightly lower (6 instead of a clean pass) because the helpfulness criterion got a 1 — the judge didn't penalize helpfulness in that case, but the human annotator noticed that offering a feedback email to an upset customer is a partial answer at best. That's the kind of nuance automated evaluation tends to miss.

---

## Main findings

TC03 is a system-level problem. The model hallucinated product data in response to a health-relevant question. No amount of prompt tuning will reliably fix this — the chatbot either needs access to verified product data or needs a hard rule blocking it from answering material composition questions entirely.

Tone was consistently strong across all 5 responses (2/2 in every case). The model handles the language part well. The failures are in accuracy and helpfulness, not in sounding human.

TC05 shows a gap the automated judge missed. The response is technically correct but doesn't actually help a frustrated customer. A human notices that. The LLM judge scored it as a pass because it checked the criteria list and all boxes were ticked.

---

## What I'd change if doing this again

The scoring scale works, but I'd add one more criterion specifically for "does the response avoid false promises." Right now that falls under accuracy, but it's different enough to deserve its own 0–2 score. A chatbot that's factually correct but still overpromises (e.g., "we'll make this right for you!") would currently score 3 on accuracy and slip through. Separating it would catch that.

I'd also annotate each record twice with different annotators and calculate inter-annotator agreement. With one annotator, the scores are consistent with each other but there's no way to know if they'd match a second person's judgment. For TC03 any annotator would probably score 0 on accuracy. For TC05's helpfulness score (1 vs 2), a second annotator might disagree.
