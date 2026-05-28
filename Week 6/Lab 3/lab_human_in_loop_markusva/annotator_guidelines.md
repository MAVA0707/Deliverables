# Annotator guidelines

**Task:** You are evaluating chatbot responses for an online fashion retailer. The chatbot handles customer service questions: returns, complaints, product questions, discount codes, and competitor comparisons.

Your job is to read the customer's message and the chatbot's response, then score the response using the criteria below. You are checking whether the response would work well in a real customer service situation — not whether it's beautifully written.

---

## Evaluation criteria

Score each criterion separately, then add the points for a total.

### 1. Factual accuracy (0–3 points)

Does the chatbot say things that are true and consistent with company policy?

- **3** — Everything stated is correct. Return policy (30 days, unworn, original tags, via website/app) is mentioned accurately where relevant. No made-up information.
- **2** — Mostly correct, with one minor inaccuracy that doesn't mislead the customer.
- **1** — Contains an error that could confuse the customer (wrong number of days, wrong process).
- **0** — Contains a serious factual error. Example: stating a product's material composition without access to product data, or promising a refund the chatbot cannot guarantee.

### 2. Tone (0–2 points)

Does the response sound like a competent, calm human customer service agent?

- **2** — Warm and professional. Doesn't sound like a template. Not defensive or robotic.
- **1** — Acceptable but flat. Sounds a bit like a copy-paste ("We apologize for any inconvenience"). Gets the job done but feels impersonal.
- **0** — Cold, defensive, dismissive, or escalates tension.

### 3. Helpfulness (0–2 points)

Does the customer know what to do next after reading this response?

- **2** — Clear next step provided (specific action, contact method, timeframe, or direct answer).
- **1** — Vague next step, or the response answers but leaves the customer slightly unsure what to do.
- **0** — No next step. The customer is stuck.

**Total possible: 7 points.**

---

## What each total score means

| Score | Meaning |
|---|---|
| 6–7 | Good response. Meets all criteria. |
| 4–5 | Acceptable. Minor issues but wouldn't cause customer problems. |
| 2–3 | Weak. At least one criterion clearly failed. |
| 0–1 | Bad. Multiple failures. Could mislead or upset the customer. |

---

## Edge cases

**The chatbot doesn't know something.** If a customer asks for information the chatbot couldn't have (like exact product materials), a good response says "I don't have that information" and points to a next step. Score it 3 for accuracy if it does this correctly. Score it 0 if it makes something up.

**The response is too long.** Don't penalize length unless it's so long the key information gets buried. If you have to read 5 paragraphs to find the return policy, that's a helpfulness issue (score 1 instead of 2).

**The response is too short.** A short response can be a 7 if it's accurate, warm, and gives a next step. Length doesn't affect the score.

**Competitor mentions.** The chatbot should never criticize competitors or say anything that could be legally or reputationally risky. If it does, score tone as 0.

**Refund promises.** The chatbot can't process refunds. If it says "your refund will be processed," that's a factual accuracy issue (score 0 or 1 for accuracy) because it's promising something it can't deliver.

---

## Before you submit each annotation

Check:
- Did I score each criterion separately?
- Did I add the scores correctly?
- Is there anything in the response that would make a real customer angry, confused, or misled? If yes, make sure the score reflects that.

If you're not sure about a score, write a short comment explaining why. That's more useful than guessing.
