# Lab: Build your own human evaluation lab

**Scenario:** Human evaluation of a customer service chatbot for a German online fashion retailer. The 5 records come from the LLM judge lab — same prompts, same responses, now scored by a human annotator using a cumulative rubric (accuracy + tone + helpfulness, max 7 points).

**Argilla Space URL:** `https://yourusername-fashion-eval.hf.space` *(replace with your actual URL after deployment)*

---

## Evaluation task overview

Each annotator reads a customer message and the chatbot's response, then scores 3 criteria separately:
- Factual accuracy (0–3)
- Tone (0–2)
- Helpfulness (0–2)

Total: 0–7. Labels: good (6–7), acceptable (4–5), weak (2–3), bad (0–1).

Full scoring rules are in `annotator_guidelines.md`.

---

## File map

| File | What it is |
|---|---|
| `annotator_guidelines.md` | Complete scoring guidelines for annotators |
| `dataset_config.md` | Argilla dataset fields, questions, metadata — with creation code |
| `argilla_setup_and_upload.py` | Python script: connects to Argilla, creates dataset, uploads records, exports results |
| `annotated_dataset.csv` | Human-annotated results for all 5 records |
| `lab_summary.md` | Analysis summary with metrics and comparison to LLM judge |

---

## How to run

1. Deploy Argilla to Hugging Face Spaces (follow the [Argilla Spaces guide](https://docs.argilla.io/latest/getting_started/how-to-deploy-argilla-on-hugging-face/))
2. Create a `.env` file:
   ```
   ARGILLA_API_URL=https://yourusername-spacename.hf.space
   ARGILLA_API_KEY=your-api-key
   HF_TOKEN=your-hf-token   # only for private Spaces
   ```
3. Install: `pip install argilla python-dotenv`
4. Run: `python argilla_setup_and_upload.py`
5. Open the Argilla UI, annotate all records
6. Uncomment the `export_annotations()` call at the bottom and re-run to download results
