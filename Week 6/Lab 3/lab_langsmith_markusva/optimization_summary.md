# Optimization summary

Both runs used gpt-5.4-mini, so the cost is identical (~$0.00054 per 15-example run at rough token estimates). The meaningful comparison here is temperature, not model price. Temperature=0 and temperature=0.7 cost the same and scored within ~2 points of each other on correctness across 15 examples — not a statistically meaningful gap. For production use, I'd pick gpt-5.4-mini at temperature=0 as the default: it's deterministic (easier to debug and reproduce), costs $0.75/1M input tokens, and handles the clear grammar errors correctly. If the use case required more natural-sounding explanations rather than strict correctness, temperature=0.3–0.5 would be worth testing. Switching to gpt-5.4 ($2.50/1M input) would cost ~3.3x more per call and likely improve only on the edge cases involving socially acceptable variant forms — a poor trade for a B1 learner tool where those cases are uncommon and the simpler errors matter more.

**Cost comparison table:**

| Model | Input price | Output price | Cost / 15 examples | Notes |
|---|---|---|---|---|
| gpt-5.4-mini (temp=0) | $0.75/1M | $4.50/1M | ~$0.00054 | Used in this lab |
| gpt-5.4-mini (temp=0.7) | $0.75/1M | $4.50/1M | ~$0.00054 | Same cost, slightly more varied output |
| gpt-5.4 | $2.50/1M | $15.00/1M | ~$0.0018 | ~3.3x more expensive |

**Recommendation:** gpt-5.4-mini at temperature=0 for volume grammar correction. Only consider gpt-5.4 if you need the nuanced "both forms acceptable" handling and have evidence from a larger dataset that it actually improves those cases.
