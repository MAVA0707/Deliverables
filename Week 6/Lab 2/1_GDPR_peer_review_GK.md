# Phase 4 — Peer Review

**Reviewer:** Gunter
**Reviewed document:** GDPR Audit Pack — Markus vA (CV Screening Tool with Human Review)
**Review date:** May 2026

---

## Peer Feedback Rubric

| Criterion | Score (1–3) | Comment |
|---|---|---|
| Clear bottom-line recommendation | 3 | "Go with conditions" is unambiguous and backed by a specific two-part justification — no transfer mechanism and no DPIA. The one-sentence reason names the exact gap, which is exactly what a client needs to understand the urgency. |
| Lawful basis selection is justified | 3 | Purpose 1 (legitimate interests) includes a brief but complete three-part reasoning. Purpose 2 is honestly flagged as TBD with a clear explanation of why consent is the safer option. Flagging a gap as TBD — legal review is more useful than guessing a basis and getting it wrong. |
| Top actions are specific and sequenced | 3 | All three actions are concrete and reference specific legal provisions. Sequencing is logical: fix the unlawful transfer first, then conduct the DPIA, then build rights workflows. The note to involve external DPO advice for the German DPA context shows practical awareness. |
| Residual risks are named honestly | 3 | Proxy discrimination, Article 22 nominal review exposure, and model training basis uncertainty are all named without softening. The "5% override" framing for the Article 22 risk is a strong and realistic illustration of what a supervisory authority would look for in practice. |
| Law stacking is addressed (AI Act / ePrivacy) | 3 | AI Act classification as high-risk under Annex III (employment) is correct and the specific obligations — registration, technical documentation, conformity assessment — are listed. ePrivacy is scoped correctly as out of scope for the core workflow. |

---

## Reviewer Note (as client)

We accept the recommendation and agree that the two go-live blockers — the missing US transfer mechanism and the absent DPIA — must be resolved before any production data is processed.

One concern we want to flag: the memo identifies DPAs as necessary with AWS and TextAnalytics Inc., but the worksheet also notes that each corporate HR client may function as a controller, making a DPA with every client a go-live requirement as well. This is not surfaced as a top action in the memo, and in practice it may affect the same timeline as Action 1 — coordinating DPAs with multiple corporate clients across Germany and the Netherlands is not a quick task.

We would ask the consultant to add this as either a fourth action or a consolidated note within Action 1, so the client's legal team does not discover it independently during vendor onboarding.
