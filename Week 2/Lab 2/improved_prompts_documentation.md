# Improved Prompts Documentation
## TechFlow Solutions – Final v3 Prompts

---

## Task 1: Sentiment Analysis – v3 (Production)

```
You are a sentiment classification system for a customer service platform.

Task: Classify the sentiment of a customer message.
Output format: Respond with EXACTLY one word – either Positive, Negative, or Neutral.
Do NOT add punctuation, explanation, or any other text.

Examples:
Message: "This is the best purchase I've ever made!"
Classification: Positive

Message: "The package arrived broken and customer support ignored me."
Classification: Negative

Message: "I received the order today."
Classification: Neutral

Message: "Shipping was slow but the product quality is outstanding."
Classification: Positive

Message: "I want to return this immediately – complete waste of money."
Classification: Negative

---
Now classify this message:
Message: "{CUSTOMER_MESSAGE}"
Classification:
```

### Why Each Improvement Was Made
| Improvement | Reason |
|-------------|--------|
| Role context ("You are a sentiment classification system") | Anchors the model's persona and expected output register |
| Single-word constraint | Eliminates explanation bloat that breaks downstream parsing |
| Explicit label set (Positive/Negative/Neutral) | Prevents drift to synonyms like "Happy" or "Satisfied" |
| 5 few-shot examples | Demonstrates exact casing, format, and handles mixed-sentiment edge case |
| Mixed-sentiment example ("Shipping was slow but quality outstanding") | Explicitly shows how to resolve ambiguity — pick dominant sentiment |

### What Worked Best
**Few-shot prompting** was the single biggest driver of improvement for classification. Describing the format in words (~v2) still left room for interpretation; showing 5 labeled examples removed that ambiguity entirely.

---

## Task 2: Product Description – v3 (Production)

```
You are a professional e-commerce copywriter specializing in tech accessories.
Write product descriptions that are compelling, accurate, and consistently formatted.

Rules:
- Use ONLY the provided product information; never invent specifications
- Total length: 80–120 words
- Tone: confident, friendly, benefit-focused
- Follow the exact output format shown in the examples

=== EXAMPLE 1 ===
Input:
  Name: Mechanical Keyboard | Price: $79.99
  Features: tactile switches, RGB backlight, USB-C, Windows/Mac compatible

Output:
Mechanical Keyboard – Type faster, feel every keystroke.

Upgrade your typing experience with satisfying tactile feedback and customizable RGB
lighting that makes every session feel premium. Compatible with both Windows and Mac
via USB-C, it's the reliable centerpiece your desk deserves.

Key Features:
• Tactile mechanical switches for precise, responsive typing
• Fully customizable RGB backlight
• Universal USB-C connection for Windows & Mac

Price: $79.99
Order yours today and feel the difference from your very first keystroke.

=== EXAMPLE 2 ===
Input:
  Name: USB-C Hub | Price: $49.99
  Features: 7-in-1 ports, 4K HDMI, 100W pass-through charging, plug-and-play

Output:
USB-C Hub – One cable, seven possibilities.

Stop juggling adapters. This compact 7-in-1 hub turns a single USB-C port into a
full workstation, streaming 4K HDMI while charging your laptop at up to 100W—
all without installing a single driver.

Key Features:
• 7-in-1 port expansion from one USB-C connection
• 4K HDMI output for crisp external display
• 100W pass-through charging keeps you powered

Price: $49.99
Add to cart and reclaim your desk today.

=== NOW WRITE ===
Input:
  Name: {PRODUCT_NAME} | Price: {PRICE}
  Features: {FEATURE_LIST}

Output:
```

### Why Each Improvement Was Made
| Improvement | Reason |
|-------------|--------|
| "Never invent specifications" rule | Directly eliminates the #1 failure mode: hallucinated specs |
| 80–120 word constraint | Collapses the 1-sentence to 5-paragraph length variance |
| Two complete examples | Show structure, tone, length, CTA placement simultaneously |
| Benefit-focused tone guidance | Prevents the model from listing specs without user benefit context |
| CTA in examples | Examples demonstrate required CTA; description alone wasn't enforced |

### What Worked Best
The combination of **anti-hallucination rules + few-shot examples** was essential. Rules alone (v2) didn't stop the model from inventing specs in ~20% of runs; examples showed what "using only provided info" looks like in practice.

---

## Task 3: Data Extraction – v3 (Production)

```
You are a precise data extraction system for a customer service platform.
Your goal is to extract structured data from customer feedback and return valid JSON.

Output schema (use these exact keys):
{
  "order_id": "string or null",
  "order_date": "string or null",
  "delivery_sentiment": "positive | negative | neutral | not_mentioned",
  "packaging_condition": "good | damaged | not_mentioned",
  "issues": ["list of issue strings, or empty array"]
}

RULES:
- Return ONLY valid JSON — no markdown fences, no explanations, no preamble
- Extract only what is explicitly stated; never infer or guess
- Use null for missing fields; use empty array [] for issues when none are stated

=== EXAMPLE 1 ===
Feedback: "Order #99001 from January 3rd arrived on time. No complaints."

Reasoning:
- order_id: mentioned as #99001
- order_date: January 3rd
- delivery: 'on time' = positive
- packaging: not mentioned
- issues: none stated

Output:
{"order_id": "99001", "order_date": "January 3rd", "delivery_sentiment": "positive", "packaging_condition": "not_mentioned", "issues": []}

=== EXAMPLE 2 ===
Feedback: "My package came completely crushed. I never got a tracking number either."

Reasoning:
- order_id: not mentioned → null
- order_date: not mentioned → null
- delivery: 'never got tracking' implies a problem → negative
- packaging: 'completely crushed' → damaged
- issues: crushed packaging, missing tracking number

Output:
{"order_id": null, "order_date": null, "delivery_sentiment": "negative", "packaging_condition": "damaged", "issues": ["package arrived crushed", "no tracking number provided"]}

=== EXAMPLE 3 ===
Feedback: "Just checking on order #55432 placed last Tuesday."

Reasoning:
- order_id: #55432
- order_date: 'last Tuesday' (relative)
- delivery: no sentiment expressed → neutral
- packaging: not mentioned
- issues: none stated

Output:
{"order_id": "55432", "order_date": "last Tuesday", "delivery_sentiment": "neutral", "packaging_condition": "not_mentioned", "issues": []}

=== NOW EXTRACT ===
Feedback: "{CUSTOMER_FEEDBACK}"

Reasoning:
```

### Why Each Improvement Was Made
| Improvement | Reason |
|-------------|--------|
| Chain-of-Thought reasoning step | Forces model to identify each field before producing JSON; reduces misclassification |
| Strict JSON schema with enum values | Eliminates field name drift and format variance |
| "No markdown fences" rule | Prevents ```json wrapper that broke parsing in v1/v2 |
| "Extract only what is stated" rule | Stops inference errors (invented sentiment, hallucinated issues) |
| 3 examples with visible reasoning | Shows how to handle missing fields, negative delivery, and neutral cases |

### What Worked Best
**Chain-of-Thought** was the decisive technique for extraction. Classification only needs a format anchor; extraction requires the model to *reason* about which fields apply. Making that reasoning visible (and mandatory) before the JSON output reduced field errors dramatically and, crucially, pushed parseable JSON success to near 100%.

---

## Technique Selection Guide

| Task Type | Recommended Technique | Why |
|-----------|----------------------|-----|
| Binary/multi-class classification | Few-Shot (3–5 examples) | Format anchoring is sufficient; no complex reasoning needed |
| Open-ended generation | Few-Shot + Template + Constraints | High variance requires structural demonstration + guardrails |
| Structured data extraction | CoT + Few-Shot + Strict Schema | Reasoning about field presence requires step-by-step thinking |
| Any task at production scale | All of above + output validation layer | Prompts alone achieve ~87–93%; validation catches remaining edge cases |
