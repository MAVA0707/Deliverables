"""
Argilla setup, data upload, and export script
Fashion chatbot human evaluation lab

Steps:
  1. Connect to Argilla (Hugging Face Space)
  2. Create the dataset with fields, questions, and metadata
  3. Upload 5 evaluation records
  4. (After annotating in UI) Download and export annotated results

Set these in a .env file:
  ARGILLA_API_URL=https://yourusername-spacename.hf.space
  ARGILLA_API_KEY=your-argilla-api-key
  HF_TOKEN=your-huggingface-token   # only needed for private Spaces
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------
# Step 1: Connect
# --------------------------------------------------------------------------

import argilla as rg

client = rg.Argilla(
    api_url=os.getenv("ARGILLA_API_URL"),
    api_key=os.getenv("ARGILLA_API_KEY"),
    # headers={"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}  # uncomment for private Space
)

# Quick connectivity check
print(f"Connected as: {client.me.username}")


# --------------------------------------------------------------------------
# Step 2: Create dataset
# --------------------------------------------------------------------------

GUIDELINES = open("annotator_guidelines.md", encoding="utf-8").read()

settings = rg.Settings(
    guidelines=GUIDELINES,
    fields=[
        rg.TextField(
            name="instruction",
            title="Customer message",
            use_markdown=True,
        ),
        rg.TextField(
            name="chatbot_response",
            title="Chatbot response",
            use_markdown=True,
        ),
    ],
    questions=[
        rg.RatingQuestion(
            name="accuracy_score",
            title="Factual accuracy (0–3)",
            values=[0, 1, 2, 3],
            description=(
                "Does the response state things that are factually correct? "
                "0 = serious error (made-up info, wrong policy), 3 = fully accurate."
            ),
        ),
        rg.RatingQuestion(
            name="tone_score",
            title="Tone (0–2)",
            values=[0, 1, 2],
            description=(
                "Does the response sound like a calm, professional agent? "
                "0 = cold or defensive, 2 = warm and genuine."
            ),
        ),
        rg.RatingQuestion(
            name="helpfulness_score",
            title="Helpfulness (0–2)",
            values=[0, 1, 2],
            description=(
                "Does the customer have a clear next step after reading this? "
                "0 = no next step, 2 = specific and actionable."
            ),
        ),
        rg.LabelQuestion(
            name="overall_label",
            title="Overall quality label",
            labels=["good", "acceptable", "weak", "bad"],
            description="Based on total score: good = 6–7, acceptable = 4–5, weak = 2–3, bad = 0–1.",
        ),
        rg.TextQuestion(
            name="comments",
            title="Comments (optional)",
            required=False,
            description="Edge cases, borderline scores, anything unusual.",
        ),
    ],
    metadata=[
        rg.TermsMetadataProperty(name="test_case_id"),
        rg.TermsMetadataProperty(name="scenario_type"),
        rg.TermsMetadataProperty(name="llm_judge_score"),
        rg.TermsMetadataProperty(name="model"),
    ],
)

dataset = rg.Dataset(
    name="fashion-chatbot-evaluation",
    settings=settings,
    client=client,
)
dataset.create()
print("Dataset created: fashion-chatbot-evaluation")


# --------------------------------------------------------------------------
# Step 3: Upload records
# --------------------------------------------------------------------------

# Raw data — 5 test cases from the LLM judge evaluation lab
RAW_DATA = [
    {
        "id": "TC01",
        "scenario_type": "return",
        "llm_judge_score": "1",
        "instruction": "I bought a pair of jeans 2 weeks ago and they don't fit. Can I return them?",
        "chatbot_response": (
            "Yes, you can return the jeans! Since you bought them 2 weeks ago, you're well within "
            "our 30-day return window. Just make sure they're unworn and have the original tags "
            "attached. You can start the return process easily through our website or app. Let me "
            "know if you need help finding the return section!"
        ),
    },
    {
        "id": "TC02",
        "scenario_type": "complaint",
        "llm_judge_score": "1",
        "instruction": (
            "This is ridiculous. I've been waiting 3 weeks for my order and nobody responds to "
            "my emails. I want a refund NOW."
        ),
        "chatbot_response": (
            "I'm really sorry to hear your order has been delayed for 3 weeks with no response. "
            "That's not the experience we want for you, and I completely understand your frustration. "
            "I'm escalating this to our customer care team right now — they'll reach out to you "
            "within 24 hours with an update on your order. I can't promise a refund at this moment "
            "without knowing the full situation, but I'll make sure this gets priority attention."
        ),
    },
    {
        "id": "TC03",
        "scenario_type": "allergen",
        "llm_judge_score": "0",
        "instruction": "Does the blue linen shirt (item #SH-4421) contain any polyester? I'm allergic.",
        "chatbot_response": (
            "The blue linen shirt is made from 100% linen with no polyester content, "
            "so it should be safe for your allergy!"
        ),
    },
    {
        "id": "TC04",
        "scenario_type": "discount",
        "llm_judge_score": "1",
        "instruction": (
            "I have a 20% discount code SUMMER20 but the checkout won't accept it. "
            "It keeps saying 'invalid code'."
        ),
        "chatbot_response": (
            "Sorry to hear the code isn't working! A few things to check: make sure the code "
            "hasn't expired, that your cart total meets any minimum order requirement, and that "
            "the code applies to the items in your cart (some codes exclude sale items). If "
            "everything looks fine and it still doesn't work, please contact our support team "
            "at support@fashionretail.de and they'll sort it out for you."
        ),
    },
    {
        "id": "TC05",
        "scenario_type": "competitor",
        "llm_judge_score": "1",
        "instruction": (
            "Zalando has free returns forever. Why is your return window only 30 days? "
            "That's terrible."
        ),
        "chatbot_response": (
            "I hear you, and I appreciate the honest feedback. Our return window is 30 days from "
            "the delivery date, and within that window returns are free and easy to start through "
            "the app. We're always looking at how to improve the experience for our customers. "
            "If you'd like to share more feedback, our team reads every message at "
            "feedback@fashionretail.de."
        ),
    },
]

records = [
    rg.Record(
        fields={
            "instruction": item["instruction"],
            "chatbot_response": item["chatbot_response"],
        },
        metadata={
            "test_case_id": item["id"],
            "scenario_type": item["scenario_type"],
            "llm_judge_score": item["llm_judge_score"],
            "model": "gpt-4o-mini",
        },
    )
    for item in RAW_DATA
]

dataset.records.log(records)
print(f"Uploaded {len(records)} records.")
print("Open your Argilla Space and annotate the records, then run the export below.")


# --------------------------------------------------------------------------
# Step 4: Download annotated data (run after annotating in the UI)
# --------------------------------------------------------------------------

def export_annotations(output_path="annotated_dataset_from_argilla.json"):
    """
    Download completed annotations from Argilla and save to JSON.
    Run this after you've finished annotating in the UI.
    """
    ds = client.datasets("fashion-chatbot-evaluation")
    annotated = ds.records.to_datasets()  # returns a HuggingFace Dataset object

    # Convert to list of dicts and save
    records_list = annotated.to_list()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records_list, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(records_list)} records to {output_path}")
    return records_list


# Uncomment to export after annotating:
# export_annotations()
