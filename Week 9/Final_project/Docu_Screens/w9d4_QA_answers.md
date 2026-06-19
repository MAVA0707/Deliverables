# Likely questions — answers

*Ravenstack AI churn prediction  ·  Markus von Aschoff  ·  June 2026*

---

## Why did you classify your system as Limited Risk?

The EU AI Act (Regulation 2024/1689) has four levels: Unacceptable, High, Limited, and Minimal.

I worked through the Annex III high-risk categories one by one. Employment (4b) covers HR decisions about workers, not B2B customer retention. Essential services (5) covers creditworthiness and health insurance, not SaaS subscriptions. The system is not biometric, not law enforcement, not critical infrastructure.

What pushes it above Minimal Risk is the LLM component. Claude generates text that the CS team reads and acts on. Article 52(1) says users must be told when AI generated the content they are seeing. That is a transparency obligation, which makes it Limited Risk, not Minimal.

The system already meets the Article 52(1) requirement. Every Slack digest header reads "Model: rule-based v1". The obligation is satisfied from day one.

---

## What happens if the AI output is wrong — who is liable?

The CS team makes all contact decisions. The model ranks accounts and Claude writes one sentence per account. No automated message goes to any customer. A human reviews the list every Monday and decides who to call.

If a CS rep calls a customer based on a wrong or misleading alert, Ravenstack as the operator is liable. Anthropic's API terms explicitly exclude liability for decisions made using model output. The workflow design limits the damage: raw risk signals are shown alongside each LLM sentence, so the CS manager can cross-check before picking up the phone.

If the system were ever offered to third-party customers, Ravenstack would need professional indemnity insurance and a formal error-reporting process before signing any contract.

---

## How did you calculate the ROI? What is your biggest assumption?

Start with what the data shows: Ravenstack's annual churn rate is 12.1%. Applied to a $60M ARR base, that is $7.26m in ARR at risk per year, spread across about 47 accounts.

If CS outreach (triggered by the weekly alerts) retains 15% of those at-risk accounts, that is 7 accounts saved and $1m ARR protected per year.

Costs: $10,000 upfront across Phases 1 to 3, then $1,395/month ongoing. The system goes live at month 3. Running the numbers: benefit starts with saving the first account.


**The biggest assumption is the 15% save rate.** Published B2B SaaS case studies show 5% to 25% improvement when usage-based alerts pair with CS outreach at this scale. I used 15% as a defensible midpoint, but there is no Ravenstack-specific data yet. Phase 2 will measure actual lift against a control group. If the real number is 5%, the ROI drops to about 40%. If it is 25%, the ROI exceeds 400%. Everything hinges on whether CS outreach actually changes outcomes.

---

## What personal data does your system process, and what is the legal basis?

The scoring model processes account names, industry, country, plan tier, MRR, feature usage counts, and support ticket counts. Most of this is B2B company data, not personal data.

The one personal data risk: if an account is a sole trader whose company name is their personal name ("Jane Smith Ltd" or just "Jane Smith"), that name is personal data under GDPR Article 4(1). The system treats all account names as potentially personal for that reason.

The data sent to Anthropic each week is: up to 20 account names (or IDs), industry segment, plan type, MRR, and 2 to 4 behavioral signals (e.g., "new account, 6 days old", "usage down 63%"). No email addresses, no user-level data, no special categories.

**Legal basis: Legitimate Interest (Article 6(1)(f)).** Processing customer behavioral data to prevent churn is a legitimate business interest. The Legitimate Interest Assessment (LIA) concludes the processing is proportionate and necessary: the data is used to help the account (by giving the CS team early warning), not against it, and all contact decisions go through a human.

---

## What would you do first to move from POC to pilot?

Decide whether to deploy with internal tech-stack or N8N/Claude like the POC.

After that: activate the schedule, confirm the first digest arrives, have the CS team lead rate the top 5 alerts to check that the output is readable and actionable, and set a date for the week 4 precision review. Everything else (ML model, CRM integration, Power BI dashboard) waits until that signal is proven.

---

## What is the main compliance gap you would need to close before deploying?

The Anthropic Business API Data Processing Agreement is not signed.

Every week, the system sends account behavioral data to Anthropic's US-based API. Without a signed DPA covering Standard Contractual Clauses, that transfer violates GDPR Chapter V on third-country transfers. This is a blocking gap. Nothing in Phase 3 should go live until it is closed.

Two other gaps exist but are not blocking:

1. The Slack DPA needs to be signed for the same reason.
2. A short written policy for the CS team is needed to meet the EU AI Act Article 52(1) obligation formally (a Slack channel description note and a one-page doc explaining what the model does and does not do).

The DPA review takes a day. The Slack note and CS policy take an afternoon. None of these are hard, but all three need to be done before Phase 3.

---

## What would you do differently if you had more time?

Four things.

**Run a proper A/B control group from day one.** The ROI model depends on measuring lift. Without a control group (accounts flagged but deliberately not contacted), you cannot know whether the churn reduction came from the alerts or from something else. I documented this as a plan, but I would build it into the n8n workflow itself from the first live run.

**Build the feedback loop.** CS reps react with ✅ or ⏭️ in Slack, but those reactions currently go nowhere. With more time I would read those reactions via the Slack API, write them to a database, and use them to retrain the model. Right now the model learns nothing from how the CS team uses it.

**Test the ML model earlier.** The Phase 1 data audit found that the usage-drop signal is weak (median drop ratio: 1.02, only 18% of churned accounts dropped to under 50% of prior activity). I would have explored more features: days since first login, number of integrations set up, onboarding step completion. The current rule-based model uses only what I checked; a proper feature selection pass might have found better signals.

**Explore the support ticket text.** The scoring model uses only ticket counts and satisfaction scores. The churn events table has free-text feedback. With more time I would have run a topic model over that text to see whether specific complaint themes predict churn better than raw counts. "Features" is the top stated reason for cancellation — but that is an exit survey label, not a signal you can detect early. The ticket text might have given earlier warning.
