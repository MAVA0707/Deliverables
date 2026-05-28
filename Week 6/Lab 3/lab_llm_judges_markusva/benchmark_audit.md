# Benchmark audit

**Client scenario:** A German online fashion retailer wants an LLM-powered chatbot to handle customer service. It answers questions about returns, shipping, product details, and complaints. Failure modes are wrong policy information, rude tone, and making promises the company can't keep.

---

## Benchmark 1: MT-Bench

**Year:** 2023
**Source:** https://arxiv.org/abs/2306.05685

**Why it seemed relevant:**
MT-Bench tests multi-turn conversations across 8 categories including writing and roleplay. A customer service chatbot needs to hold a conversation across multiple turns, so this felt like a natural fit.

**Contamination risk:** High
Many models were evaluated on MT-Bench in papers and blog posts. The 80 questions are public and short, so training data contamination is very likely for any model released after mid-2023.

**Saturation risk:** High
GPT-4 scored near the ceiling (8.99/10) in the original paper. Most major models now score between 8 and 9. The benchmark no longer separates good models from great ones.

**Format:** Free-form text (conversational)

**Verdict:** Reject it. The contamination and saturation problems make scores unreliable. A model scoring 8.5 on MT-Bench tells me nothing about how it handles a specific German return policy question.

---

## Benchmark 2: HellaSwag

**Year:** 2019
**Source:** https://arxiv.org/abs/1905.07830

**Why it seemed relevant:**
HellaSwag tests commonsense reasoning. I thought a chatbot needs commonsense to understand what a customer actually means, even when the question is phrased oddly.

**Contamination risk:** High
HellaSwag is in most LLM pre-training datasets. It is one of the oldest widely-used benchmarks and has been public since 2019. Every major model has almost certainly trained on it.

**Saturation risk:** High
GPT-4 scores above 95%. Several open models also exceed 90%. The benchmark was designed for models from 2019 and is now too easy to be meaningful.

**Format:** Multiple choice

**Verdict:** Reject it. The format (multiple choice) doesn't match the free-form chatbot use case at all. And 95%+ scores mean I can't use it to compare models. Not useful here.

---

## Benchmark 3: IFEval (Instruction Following Evaluation)

**Year:** 2023
**Source:** https://arxiv.org/abs/2311.07911

**Why it seemed relevant:**
IFEval tests whether models follow specific, verifiable instructions like "respond in under 100 words" or "use bullet points." A customer service chatbot often has rules: keep replies short, don't mention competitors, always include the return policy link. IFEval tests exactly that kind of constraint-following.

**Contamination risk:** Medium
IFEval uses programmatic instructions that are generated, not a fixed public list of questions. Still, the evaluation format is well-known and some models may have been tuned to perform well on it.

**Saturation risk:** Low to medium
GPT-4 scores around 77-85% depending on the version and strictness. There is still meaningful separation between models, and some instruction types remain challenging.

**Format:** Free-form text with verifiable constraints

**Verdict:** Adapt it. The core idea is good. I would write custom instructions that match real chatbot constraints (for example: "answer this return question in under 80 words, include the phrase 'within 30 days', and don't mention competitor brands"). This keeps the verifiable structure of IFEval but tests something real for this client.
