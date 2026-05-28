# Dataset configuration

**Dataset name:** `fashion-chatbot-evaluation`
**Workspace:** default
**Argilla version:** 2.x (Hugging Face Spaces deployment)

---

## Fields (what annotators read)

| Field name | Type | Required | Description |
|---|---|---|---|
| `instruction` | TextField | Yes | The customer's message, shown with markdown formatting |
| `chatbot_response` | TextField | Yes | The chatbot's response to evaluate |

Both fields use `use_markdown=True` so line breaks and any formatting render cleanly in the UI.

---

## Questions (what annotators fill in)

### Question 1: `accuracy_score`
- **Type:** RatingQuestion
- **Values:** 0, 1, 2, 3
- **Description:** "Factual accuracy — does the response contain correct information? See guidelines for scoring."

### Question 2: `tone_score`
- **Type:** RatingQuestion
- **Values:** 0, 1, 2
- **Description:** "Tone — does the response sound like a calm, professional human agent? See guidelines."

### Question 3: `helpfulness_score`
- **Type:** RatingQuestion
- **Values:** 0, 1, 2
- **Description:** "Helpfulness — does the customer have a clear next step after reading this? See guidelines."

### Question 4: `overall_label`
- **Type:** LabelQuestion
- **Labels:** `good` (6–7 pts), `acceptable` (4–5 pts), `weak` (2–3 pts), `bad` (0–1 pts)
- **Description:** "Overall quality label based on your total score (accuracy + tone + helpfulness)."

### Question 5: `comments`
- **Type:** TextQuestion
- **Required:** No
- **Description:** "Optional — note anything unusual, edge cases, or reasons for a borderline score."

---

## Metadata properties

| Field | Type | Values | Purpose |
|---|---|---|---|
| `test_case_id` | TermsMetadataProperty | TC01–TC05 | Filter by test case |
| `scenario_type` | TermsMetadataProperty | return, complaint, allergen, discount, competitor | Filter by scenario category |
| `llm_judge_score` | TermsMetadataProperty | 0, 1 | The automated judge's score from the previous lab — useful for comparison |
| `model` | TermsMetadataProperty | gpt-4o-mini | Which model generated the response |

---

## Guidelines text (as loaded into Argilla)

The full contents of `annotator_guidelines.md` are passed into the `guidelines` parameter of `rg.Settings()`. Annotators can open this at any time from within the Argilla UI by clicking the "Guidelines" button.

---

## Dataset creation code (summary)

```python
import argilla as rg

client = rg.Argilla(
    api_url="https://yourusername-fashion-eval.hf.space",
    api_key="your-api-key-here"
)

settings = rg.Settings(
    guidelines=open("annotator_guidelines.md").read(),
    fields=[
        rg.TextField(name="instruction", title="Customer message", use_markdown=True),
        rg.TextField(name="chatbot_response", title="Chatbot response", use_markdown=True),
    ],
    questions=[
        rg.RatingQuestion(name="accuracy_score", title="Factual accuracy (0–3)", values=[0, 1, 2, 3],
                          description="Does the response state things that are factually correct?"),
        rg.RatingQuestion(name="tone_score", title="Tone (0–2)", values=[0, 1, 2],
                          description="Does the response sound like a calm, professional agent?"),
        rg.RatingQuestion(name="helpfulness_score", title="Helpfulness (0–2)", values=[0, 1, 2],
                          description="Does the customer have a clear next step?"),
        rg.LabelQuestion(name="overall_label", title="Overall quality label",
                         labels=["good", "acceptable", "weak", "bad"],
                         description="Based on your total score: good=6–7, acceptable=4–5, weak=2–3, bad=0–1"),
        rg.TextQuestion(name="comments", title="Comments (optional)", required=False,
                        description="Edge cases, borderline scores, anything unusual."),
    ],
    metadata=[
        rg.TermsMetadataProperty(name="test_case_id"),
        rg.TermsMetadataProperty(name="scenario_type"),
        rg.TermsMetadataProperty(name="llm_judge_score"),
        rg.TermsMetadataProperty(name="model"),
    ]
)

dataset = rg.Dataset(name="fashion-chatbot-evaluation", settings=settings)
dataset.create()
```

---

## Notes

I chose cumulative scoring (0–3 + 0–2 + 0–2 = 7 total) instead of a single Likert scale because it forces the annotator to think separately about accuracy, tone, and helpfulness. A single 1–5 scale would be ambiguous: a response that's accurate but rude would score differently depending on how the annotator weights those things personally. The separate criteria make that explicit.

The `overall_label` question is redundant with the numeric scores by design. It gives a sanity check: if someone scores 6/7 but labels the response "weak," that's a signal to review the annotation.
