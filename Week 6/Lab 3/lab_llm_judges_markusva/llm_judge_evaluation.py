"""
LLM-as-judge evaluation pipeline
Customer service chatbot for a German fashion retailer

Uses gpt-4o-mini for both the tested model and the judge.
Set OPENAI_API_KEY in a .env file before running.
"""

import json
import time
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Test dataset ---
# 5 prompts from the evaluation design, with ground truth info for the judge

TEST_CASES = [
    {
        "id": "TC01",
        "title": "Basic return question",
        "prompt": "I bought a pair of jeans 2 weeks ago and they don't fit. Can I return them?",
        "context": "Company return policy: 30 days, item must be unworn with original tags, return started via website or app.",
        "criteria": ["confirms return is possible", "mentions 30-day window", "gives next step (website or app)"]
    },
    {
        "id": "TC02",
        "title": "Angry customer complaint",
        "prompt": "This is ridiculous. I've been waiting 3 weeks for my order and nobody responds to my emails. I want a refund NOW.",
        "context": "The chatbot should de-escalate, apologize specifically, and offer a concrete next step. It must not promise a refund.",
        "criteria": ["calm and empathetic tone", "specific apology (not a template phrase)", "actionable next step offered", "no false refund promise"]
    },
    {
        "id": "TC03",
        "title": "Allergen product question",
        "prompt": "Does the blue linen shirt (item #SH-4421) contain any polyester? I'm allergic.",
        "context": "The chatbot does not have access to product database. It must not make up material composition. It should say it doesn't know and direct the customer to the product page or support email.",
        "criteria": ["does not invent material composition", "acknowledges uncertainty", "gives useful next step"]
    },
    {
        "id": "TC04",
        "title": "Discount code not working",
        "prompt": "I have a 20% discount code SUMMER20 but the checkout won't accept it. It keeps saying 'invalid code'.",
        "context": "The chatbot cannot apply codes. It should troubleshoot (expired code? minimum cart value? wrong items?) and offer a path forward.",
        "criteria": ["addresses likely causes", "offers a next step", "does not promise to apply the code itself"]
    },
    {
        "id": "TC05",
        "title": "Competitor comparison",
        "prompt": "Zalando has free returns forever. Why is your return window only 30 days? That's terrible.",
        "context": "The chatbot must not criticize competitors or make false claims about its own policy. It should acknowledge the feedback politely and explain its own policy.",
        "criteria": ["no negative mention of competitor", "factually accurate about own policy", "not defensive in tone"]
    }
]

SYSTEM_PROMPT = """You are a helpful and professional customer service chatbot for an online fashion retailer.
You handle questions about returns, shipping, products, and complaints.
Return policy: 30 days, items must be unworn with original tags, returns started via the website or app.
You do not have access to individual order data or product databases.
Keep responses concise, under 120 words. Be warm but not overly casual."""

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator for customer service chatbot responses.
You will be given the original customer message, the chatbot's response, the evaluation criteria, and context about the correct behavior.
You must evaluate the response strictly against the criteria.
Return ONLY a valid JSON object, no other text."""

def get_chatbot_response(prompt):
    """Get a response from the tested model."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=200,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content, response.usage

def evaluate_with_judge(customer_message, chatbot_response, context, criteria):
    """Run the LLM-as-judge on a chatbot response."""
    criteria_text = "\n".join([f"- {c}" for c in criteria])
    
    judge_prompt = f"""You are evaluating a customer service chatbot response.

CUSTOMER MESSAGE:
{customer_message}

CHATBOT RESPONSE:
{chatbot_response}

CONTEXT (what the correct behavior looks like):
{context}

CRITERIA TO CHECK:
{criteria_text}

Step 1: Read the chatbot response carefully.
Step 2: Check each criterion. Did the response meet it? Yes or no, and why.
Step 3: Give an overall score.

Score: 0 = response fails 2 or more criteria or could make the situation worse.
Score: 1 = response meets all or all-but-one criteria well.

Return this exact JSON structure:
{{
  "score": 0 or 1,
  "reasoning": "short explanation of your score",
  "criteria_results": {{
    "criterion_1": true or false,
    "criterion_2": true or false
  }}
}}

Use the actual criterion names from the list above as keys in criteria_results."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=400,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": judge_prompt}
        ]
    )
    
    result = json.loads(response.choices[0].message.content)
    return result, response.usage

def run_evaluation():
    """Run the full evaluation pipeline and save results."""
    results = []
    total_input_tokens = 0
    total_output_tokens = 0
    total_time = 0

    print("Starting evaluation...\n")
    print("=" * 60)

    for case in TEST_CASES:
        print(f"\n[{case['id']}] {case['title']}")
        print(f"Prompt: {case['prompt'][:80]}...")

        start_time = time.time()

        # Step 1: get the chatbot response
        chatbot_response, chatbot_usage = get_chatbot_response(case["prompt"])
        
        # Step 2: evaluate it with the judge
        judge_result, judge_usage = evaluate_with_judge(
            case["prompt"],
            chatbot_response,
            case["context"],
            case["criteria"]
        )

        elapsed = round(time.time() - start_time, 2)
        total_time += elapsed

        input_tokens = chatbot_usage.prompt_tokens + judge_usage.prompt_tokens
        output_tokens = chatbot_usage.completion_tokens + judge_usage.completion_tokens
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        # gpt-4o-mini pricing as of 2024: $0.15 / 1M input, $0.60 / 1M output
        cost_estimate = (input_tokens * 0.00000015) + (output_tokens * 0.00000060)

        case_result = {
            "id": case["id"],
            "title": case["title"],
            "prompt": case["prompt"],
            "chatbot_response": chatbot_response,
            "score": judge_result.get("score"),
            "reasoning": judge_result.get("reasoning"),
            "criteria_results": judge_result.get("criteria_results", {}),
            "time_seconds": elapsed,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(cost_estimate, 6)
        }

        results.append(case_result)

        print(f"Score: {judge_result.get('score')} | Time: {elapsed}s | Tokens: {input_tokens}+{output_tokens}")
        print(f"Reasoning: {judge_result.get('reasoning', '')[:120]}")

    # Aggregate stats
    scores = [r["score"] for r in results]
    total_cost = (total_input_tokens * 0.00000015) + (total_output_tokens * 0.00000060)

    summary = {
        "total_test_cases": len(TEST_CASES),
        "passed": sum(scores),
        "failed": len(scores) - sum(scores),
        "average_score": round(sum(scores) / len(scores), 2),
        "total_time_seconds": round(total_time, 2),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_estimated_cost_usd": round(total_cost, 6)
    }

    output = {
        "model_tested": "gpt-4o-mini",
        "judge_model": "gpt-4o-mini",
        "scenario": "Customer service chatbot, German fashion retailer",
        "summary": summary,
        "results": results
    }

    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"Passed: {summary['passed']} / {summary['total_test_cases']}")
    print(f"Average score: {summary['average_score']}")
    print(f"Total time: {summary['total_time_seconds']}s")
    print(f"Total tokens: {total_input_tokens} input, {total_output_tokens} output")
    print(f"Estimated cost: ${summary['total_estimated_cost_usd']}")
    print("\nResults saved to evaluation_results.json")

if __name__ == "__main__":
    run_evaluation()
