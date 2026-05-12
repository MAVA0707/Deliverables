---
name: session-recap
description: Produce a concept-forward learning recap after a study or troubleshooting session, including chat snippets, notes, or "what did we just do?" requests even when the user does not say "recap" verbatim. Use when the user wants a recap of work plus reflection on how they learned or worked.
---

# Session Recap

Use this skill to turn a session into a concept-forward recap with gentle reflection.

## Procedure

1. Identify the main concepts, not just the timeline.
2. Connect ideas together in plain language.
3. Reflect on how the session felt and what affected learning.
4. Synthesize one insight about how the user learns.
5. Keep the tone warm, non-judgmental, and useful for spaced repetition.

## Output Shape

Prefer this format:

- `Concepts & connections`: definitions, ideas linked together, and anything worth revisiting later; avoid raw transcript dump
- `Process reflection`: brief answers to prompts such as `What helped learning today?`, `What felt noisy or rushed?`, and `What would you tweak next session?`
- `One insight about how you learn`: one sentence the agent synthesizes from what you said, with room for correction
- `Next steps`: concrete follow-up actions if relevant

## Rules

- Keep the recap warm and non-judgmental.
- Do not dump the transcript; compress it into concepts.
- If the synthesis might be wrong, state it tentatively so the user can correct it.
- Preserve concrete names, files, dates, and choices when they matter.
- If the session is incomplete, say so clearly and separate partial progress from final outcomes.
