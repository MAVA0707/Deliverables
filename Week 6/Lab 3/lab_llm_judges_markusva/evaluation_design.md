# Evaluation design

**Client scenario:** German online fashion retailer, customer service chatbot. Handles returns, product questions, complaints.

---

## Evaluation prompt 1: Basic return question

**Prompt:**
"I bought a pair of jeans 2 weeks ago and they don't fit. Can I return them?"

**Ground truth:** Yes. The correct answer is that the customer can return the item. The chatbot must mention the 30-day return window, say the item must be unworn with original tags, and tell the customer to start the return via the website or app. It should not promise a refund before confirming the item's condition.

**Verification method:** Rule-based. Check that the response contains: (1) confirmation that a return is possible, (2) the 30-day policy, (3) a next step (website or app). Missing any of these is a failure.

**Primary failure mode:** The chatbot gives wrong policy info, for example saying "60 days" instead of 30, or promising a refund unconditionally.

**Why this matters:** This is probably the most common customer question. A wrong answer creates real problems: customers who get refused at the warehouse because they misunderstood the policy will complain, and some will leave reviews.

---

## Evaluation prompt 2: Angry customer complaint

**Prompt:**
"This is ridiculous. I've been waiting 3 weeks for my order and nobody responds to my emails. I want a refund NOW."

**Ground truth:** No single correct answer. The response must: stay calm and not escalate, acknowledge the frustration, apologize, offer a concrete next step (check order status, escalate to a human agent), and not make promises about refunds it can't keep.

**Verification method:** LLM-as-judge. A human or judge model checks tone (not defensive, not dismissive), checks that there's an apology, and checks that the chatbot offers something actionable.

**Primary failure mode:** Tone. The chatbot either sounds robotic ("We apologize for any inconvenience") or overpromises ("Your refund will be processed immediately").

**Why this matters:** Angry customers post reviews. A bad response here creates public damage. This is where the chatbot needs judgment, not just correct information.

---

## Evaluation prompt 3: Product detail question

**Prompt:**
"Does the blue linen shirt (item #SH-4421) contain any polyester? I'm allergic."

**Ground truth:** The chatbot should not make up material composition. If it can look up product data, it should give the exact composition. If it can't, it should tell the customer it doesn't have that info and direct them to the product page or customer service email. Making up a fabric composition for an allergy question is a safety risk.

**Verification method:** LLM-as-judge + rule-based. Rule: response must not state a specific composition unless the data is available. Judge: did the chatbot handle uncertainty correctly without just saying "I don't know" and leaving?

**Primary failure mode:** Hallucination. The model makes up "100% linen, no polyester" when it has no product data. This is a health risk.

**Why this matters:** Allergen questions are high-stakes. A wrong answer could hurt someone. The chatbot must know when to say it doesn't know.

---

## Evaluation prompt 4: Discount code not working

**Prompt:**
"I have a 20% discount code SUMMER20 but the checkout won't accept it. It keeps saying 'invalid code'."

**Ground truth:** No single correct answer. Response must: ask for clarification (is the code expired? is the cart value above the minimum?), give the most likely reasons the code doesn't work, and offer a path forward (contact support, check email for code validity). Must not promise the discount will be applied.

**Verification method:** LLM-as-judge. Judge checks: did the chatbot ask or address likely causes? Did it give a next step? Did it overpromise?

**Primary failure mode:** The chatbot says "I'll apply the code for you" when it has no ability to do that. Or it just says "contact support" without any useful troubleshooting.

**Why this matters:** Failed discounts create friction at checkout. Customers abandon carts. A chatbot that gives a useful troubleshooting path can recover the sale.

---

## Evaluation prompt 5: Edge case, competitor mention

**Prompt:**
"Zalando has free returns forever. Why is your return window only 30 days? That's terrible."

**Ground truth:** No single correct answer. The chatbot must not: badmouth the competitor, make false claims about Zalando's policy, or change the return policy to match. It should acknowledge the feedback politely, stick to the company's own policy, and maybe offer something (like the ease of the return process).

**Verification method:** LLM-as-judge. Judge checks: did the chatbot mention competitors negatively? Did it stay factually accurate about its own policy? Did it handle the comparison without being defensive?

**Primary failure mode:** The chatbot says something negative about Zalando (legal/PR risk) or claims "our returns are actually free too" (factually wrong).

**Why this matters:** Competitor comparisons are a trap. A chatbot that handles them badly creates legal exposure or brand damage.

---

## LLM-as-judge prompt (for Prompt 2: angry customer)

### Task description

The model was acting as a customer service chatbot for a German online fashion retailer. A customer sent an angry message complaining about a 3-week delivery delay and demanding an immediate refund. The model's job was to respond in a way that de-escalates the situation, acknowledges the problem, apologizes, and offers a concrete next step.

### Evaluation criteria

1. **Tone:** The response must be calm and empathetic. It must not sound robotic, defensive, or dismissive. It must not escalate the situation.
2. **Apology:** The response must include a genuine-sounding apology, not a template phrase like "we apologize for any inconvenience."
3. **Actionable next step:** The response must offer the customer something concrete to do or promise that something concrete will happen (for example: "I'll check your order status now" or "I'll escalate this to our team and they'll contact you within 24 hours").
4. **No false promises:** The response must not promise a refund, compensation, or delivery date it cannot guarantee.

### Reasoning steps

Step 1: Read the response. Does it sound like something a competent, calm human agent would write? If it sounds like a template or a robot, that's a tone failure.

Step 2: Look for an apology. Is it specific to this situation? "I'm sorry to hear your order has been delayed for 3 weeks" is specific. "We apologize for any inconvenience" is not.

Step 3: Look for a next step. Does the customer know what happens next? Is there a time frame or a clear action?

Step 4: Check for overpromising. Did the model say anything like "your refund will be processed" or "your order will arrive tomorrow"? If yes, mark criteria 4 as failed.

### Output format

```json
{
  "score": 1,
  "reasoning": "Explanation of why this score was given.",
  "criteria_met": {
    "tone_calm_and_empathetic": true,
    "genuine_apology": true,
    "actionable_next_step": true,
    "no_false_promises": true
  }
}
```

Score scale: 0 = response fails on most criteria and could make the situation worse. 1 = response meets all 4 criteria and handles the situation well.

---

### Bias analysis

**Hidden biases this judge might have**

The judge model probably has preferences about what "empathetic" sounds like in English. If the responses being evaluated use more formal or German-influenced phrasing (for example "We take your concern very seriously"), the judge might score those lower even if they'd be appropriate for the brand's audience. There's a style bias toward informal, American-English warmth.

The judge also has no context about this specific company's actual refund policy. If the chatbot correctly says "I can't promise a refund right now because I need to check your order," the judge might flag that as "unhelpful" rather than "responsible." I'd need to give the judge the policy context.

A third risk: the judge may prefer longer responses. Concise, direct responses that cover all 4 criteria might score lower than wordy responses that feel more "thorough."

**Calibration strategy**

I'd write 4 reference examples before running the judge: one clearly bad response (angry, defensive, makes false promises), one mediocre response (correct info but robotic), one good response (meets all 4 criteria, short), and one edge case (meets 3 out of 4, fails only on false promises). I'd run the judge on these first and check if scores match my expectations. If the judge gives the mediocre response a 1 and the good response a 0, I know something is wrong.

If the judge is too lenient (almost everything scores 1), I'd add more explicit failure examples to the prompt and be more prescriptive about what "genuine apology" means versus a template phrase. If it's too strict, I'd add a note that partial compliance on tone is still a pass if the other 3 criteria are met.
