# GDPR Audit Worksheet

# Section A — Data Map

| Field | Answer |
|---|---|
| Categories of personal data | Names, addresses, financial records, transaction history, income data, debt exposure, behavioral indicators |
| Sources | Customers, banking systems, transaction records, credit databases |
| Purpose | Loan eligibility assessment and risk scoring |
| Lawful basis — Art. 6(1)(b) Contract | Processing is necessary for pre-contractual steps and performance of the loan agreement at the customer's request |
| Lawful basis — Art. 6(1)(f) Legitimate interests | The bank has a legitimate interest in credit risk management and default prevention; subject to LIA three-step test below — note: not a valid basis for the automated decision element under Art. 22(2) |
| Retention period | 5 years after loan application closure |
| Recipients and subprocessors | US hosted AI analytics provider, cloud hosting provider |
| International transfers | EU to US via Standard Contractual Clauses |
| Security measures | Encryption, role based access control, audit logging |


> **Note on Article 22:** For the automated decision-making element specifically, legitimate interests is not a valid lawful basis under Article 22(2) GDPR. Only contract necessity (Art. 22(2)(a)), consent (Art. 22(2)(c)), or legal obligation applies. Article 6(1)(b) is the appropriate and sufficient ground for this processing activity.

---

## Legitimate Interests Assessment (LIA) — Three-Step Test

**Step 1 — Purpose:** The bank has a legitimate interest in assessing the creditworthiness of loan applicants to protect against financial default and ensure responsible lending.

**Step 2 — Necessity:** Credit risk scoring based on financial records, transaction history, and behavioral indicators is a proportionate and industry-standard method for evaluating repayment reliability. Less intrusive alternatives would not provide equivalent predictive value for the stated purpose.

**Step 3 — Balancing:** Data subjects entering a loan application relationship reasonably expect their financial profile to be assessed. However, the automated nature of processing and potential for significant individual effects increase the privacy interference. Transparency, the right to object, and meaningful human review are required to maintain the balance. Legitimate interests must not be relied upon as the lawful basis for the automated decision element itself.

---

# Section B — Risk and Rights

## Are special-category data present?

Potentially yes. Financial behavior and transaction history may indirectly reveal sensitive information such as health conditions, political affiliation, or religious activities.

## Is there automated decision-making with legal or similarly significant effects?

Yes. The AI system significantly influences customer access to financial services. Human review is therefore required as a safeguard under Article 22 GDPR.

## Is a DPIA required?

Yes. Profiling, financial scoring, automated processing, and potentially significant effects on individuals meet multiple EDPB DPIA criteria.

## What data subject friction points are most likely?

Most likely issues are access requests, objections to profiling, requests for human review, and deletion requests.

## What is the controller / processor split?

The financial institution acts as controller. The AI analytics provider and cloud provider act as processors.

## Is a DPA needed with vendors?

Yes. DPAs are required with all external processors handling customer financial data.

---

# Section C — Law Stacking

| Topic | Answer |
|---|---|
| AI Act cross-check | High Risk AI system under Annex III because it supports access to financial services and creditworthiness assessment |
| ePrivacy check | No significant cookie or tracking dependency in this scenario |
| Data Act check | N/A |

---

# Additional Notes

## DPIA Trigger Criteria — EDPB Nine-Criteria Assessment

| Criterion | Applies | Explanation |
|---|---|---|
| 1. Evaluation or scoring | Yes | The system profiles and scores customers based on financial behavior and repayment indicators |
| 2. Automated decision-making with legal or similarly significant effects | Yes | Loan approval or denial directly affects access to financial services |
| 3. Systematic monitoring | No | The system does not continuously monitor individuals beyond the loan application process |
| 4. Sensitive or highly personal data | Yes | Financial data is inherently sensitive; transaction patterns may infer health conditions, religious practice, or political affiliation |
| 5. Large-scale processing | Yes | A financial institution processes loan applications at significant volume across its customer base |
| 6. Matching or combining datasets | Yes | The system combines financial records, transaction history, credit databases, and behavioral indicators |
| 7. Data concerning vulnerable subjects | Yes | Loan applicants may be in financially precarious situations, increasing potential harm from adverse decisions |
| 8. Innovative use of new technology | Yes | AI-based creditworthiness scoring represents a new technological approach with untested failure modes |
| 9. Prevents exercise of rights or use of a service | Yes | A denied loan application directly restricts access to financial services |

**Assessment:** Eight of nine EDPB criteria apply. A DPIA is mandatory before any live processing begins. If residual high risk cannot be mitigated after the DPIA, prior consultation with the lead supervisory authority is required under Article 36 GDPR before launch.

## Recommended Safeguards

- Mandatory human oversight
- Bias monitoring and audit reviews
- Explainability documentation
- Data minimization controls
- Clear privacy notice updates