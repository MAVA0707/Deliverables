# Fact Pattern

## Transition Note — Carried Forward from EU AI Act Lab

This audit carries forward **Case 2** from the EU AI Act lab: an AI-assisted private loan approval system for a European financial institution.

Under the EU AI Act, the system was classified as **High Risk** under Annex III, Point 5(b), which covers AI systems used to evaluate the creditworthiness of natural persons or establish their credit score. This classification requires conformity assessment, technical documentation, human oversight measures, and registration in the EU database before the system can be placed on the market.

Case 2 is the most relevant scenario for a GDPR analysis because it combines three elements that create the highest compliance complexity: automated decision-making with legal or similarly significant effects on individuals (Article 22), detailed financial data processing with potential for special-category inference (Article 9), and an international transfer to a US-based AI analytics vendor. These elements reflect a realistic pattern where EU AI Act and GDPR obligations must be addressed in parallel, not sequentially.

## Scenario Overview

A European financial institution wants to modernize its private loan approval process using AI assisted decision support.

The system processes customer financial records, transaction history, debt exposure, income information, and behavioral indicators in order to estimate repayment reliability and assign internal risk scores.

Most standard applications are processed automatically, while human employees mainly review unclear or borderline cases before final approval.

Data subjects are primarily EU based banking customers.

The bank uses a US hosted AI analytics provider and cloud infrastructure vendor for parts of the scoring and summarization workflow.

The AI system supports loan eligibility assessments and may significantly influence customer access to financial services.