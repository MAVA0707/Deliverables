# LangChain Guardrails — Healthcare AI Agent

Layered safety mechanisms for an AI agent handling sensitive patient data.

---

## Overview

This lab demonstrates how to protect a LangChain agent with **multiple layers of guardrails** — a practical requirement for any AI system deployed in healthcare, finance, or legal settings. You'll build from a basic agent all the way to a four-layer protection pipeline.

**Scenario:** You're building an AI agent for a healthcare company. The agent can search patient records, send emails, delete records, and query medical literature. Without guardrails, it's vulnerable to PII leakage, prompt injection, and unsafe automated actions.

---

## What You'll Learn

| Step | Topic | Type |
|------|-------|------|
| 1 | Environment setup | — |
| 2 | Base agent + fake patient database | — |
| 3 | PII detection & redaction | Deterministic |
| 4 *(optional)* | Human-in-the-loop approval | Workflow |
| 5 *(optional)* | Before-agent content filter | Deterministic |
| 6 *(optional)* | After-agent safety check | Model-based |
| 7 *(optional)* | Combined layered pipeline | All of the above |. 

---

## Prerequisites

- Python 3.10+
- OpenAI API key
- Familiarity with LangChain agents and basic Python

---

## Installation

```bash
pip install langchain langchain-openai langgraph python-dotenv
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_key_here
```

---

## Guardrail Architecture

```
User Input
    │
    ▼
Layer 1: Content Filter         ← Block banned keywords BEFORE any LLM call
    │
    ▼
Layer 2: PII Redaction (input)  ← Strip PII before it reaches the LLM
    │
    ▼
   Agent (LLM + Tools)
    │
    ▼
Layer 3: PII Redaction (output) ← Strip any PII the agent may have surfaced
    │
    ▼
Layer 4: Safety Check           ← Model-based review of the final response
    │
    ▼
Safe Response
```

Human-in-the-loop approval sits between the LLM decision and tool execution for sensitive operations (`send_email`, `delete_record`).

---

## Key Concepts

### Deterministic vs. Model-Based Guardrails

| Property | Deterministic (regex/rules) | Model-based (LLM reviewer) |
|---|---|---|
| Speed | Fast | Slower (extra LLM call) |
| Cost | Free | Adds token cost |
| Flexibility | Low — exact pattern matching | High — nuanced judgment |
| Auditability | Easy to inspect | Harder to explain |
| Best for | Known, well-defined threats | Complex, context-dependent safety |

Use deterministic guardrails as your first line of defense. Add model-based guardrails where the safety criteria are too nuanced for rules alone.

### PII Types Covered

- Email addresses
- Social Security Numbers (SSN)
- Dates of birth
- Credit card numbers
- Phone numbers

### Content Filter Keywords (configurable)

`hack`, `exploit`, `malware`, `delete all`, `bypass`, `ignore previous instructions`

---

## Project Structure

```
langchain_guardrails.ipynb   ← Main lab notebook
README.md                    ← This file
.env                         ← Your API key (not committed to git)
```

---

## Warm-Up Exercise: Gandalf

Before writing code, play [Gandalf by Lakera AI](https://gandalf.lakera.ai/) (levels 1–3). It demonstrates exactly the prompt injection vulnerabilities these guardrails defend against, and builds intuition for why layered defenses matter.

---

## Estimated Time

**Core lab (Steps 1–3):** ~45 minutes  
**Full lab with optional steps:** ~120–150 minutes

---

## References

- [LangChain Docs](https://python.langchain.com/docs/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Guardrails AI](https://www.guardrailsai.com/)
- [Lakera Gandalf](https://gandalf.lakera.ai/) — interactive prompt injection demo
- [EU AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [HIPAA Compliance Overview](https://www.hhs.gov/hipaa/index.html)

---

> **Note:** This is a sensitization lab. Guardrails, security risks, and the EU AI Act will be covered in more depth in later modules.
