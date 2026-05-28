# Client Recommendation Memo

**To:** Legal Team and CTO
**From:** Maxx — Privacy and AI Compliance Advisory
**Re:** GDPR Compliance Assessment — AI-Assisted Loan Approval System
**Date:** May 2026

---

## Bottom Line

**Go with conditions.**

The proposed system has a viable legal path under GDPR, but it cannot go live in its current form. Three structural compliance requirements must be addressed before any live processing of customer financial data begins. Proceeding without these controls would expose the institution to enforcement risk under both GDPR and the EU AI Act simultaneously.

---

## Top Three Actions

**1. Conduct a DPIA before first processing.**

A DPIA is mandatory here — not discretionary. Your scenario triggers eight of the nine EDPB criteria, including large-scale financial profiling, automated decision-making with significant individual effects, potential inference of sensitive data, and deployment of an innovative technical solution. Complete the DPIA, document mitigation measures, and if residual high risk cannot be eliminated, consult your lead supervisory authority before launch. This step cannot be done in parallel with deployment — it must come first.

**2. Execute DPAs with all US vendors and complete a Transfer Impact Assessment.**

Both the AI analytics provider and the cloud infrastructure vendor require signed Data Processing Agreements before any customer data flows to them. Standard Contractual Clauses are necessary but not sufficient post-Schrems II. You must conduct a Transfer Impact Assessment for each US processor to verify that the SCCs provide effective protection in practice given US surveillance law exposure. If a TIA cannot be substantiated, data localisation or an EU-based vendor alternative must be considered before go-live.

**3. Implement substantive Article 22 safeguards and revise your privacy notice.**

Your system constitutes automated decision-making with legal or similarly significant effects. Human review must be meaningful — reviewers need genuine authority and sufficient information to override AI recommendations, not a nominal sign-off under volume pressure. Customers must be informed of the logic involved, the significance of automated scoring, and their right to request human review and contest decisions. Your current privacy notice will need a dedicated section covering this processing activity before it is lawful.

---

## Residual Risks

Even if all three actions above are completed, the following risks cannot be fully eliminated.

**Special-category inference.** Transaction patterns may inadvertently reveal health conditions, religious practice, or political affiliation. Regulatory interpretation of inferential processing under Article 9 is still developing across EU supervisory authorities. Proactive bias auditing and output monitoring are strongly recommended, but cannot guarantee that no supervisory authority will take a different view.

**US vendor exposure.** SCCs and a completed TIA reduce legal risk but do not eliminate it. US surveillance law — including FISA 702 — may permit government access to data held by US-based processors regardless of contractual protections. This is a structural and geopolitical risk that cannot be fully contracted away, and it will remain as long as US vendors are in the processing stack.

**Nominal human oversight.** Article 22 compliance depends on genuine oversight in practice. If volume pressure means reviewers rarely challenge AI recommendations, regulators may find that the safeguard fails operationally even if it exists on paper. This is a governance and culture risk as much as a legal drafting issue, and it requires active monitoring of override rates after launch.
