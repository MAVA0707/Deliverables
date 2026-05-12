---
name: codex-skill-authoring
description: Create or update Codex skills, including choosing a skill name, writing trigger-focused SKILL.md frontmatter and body, adding optional scripts/references/assets, and validating the result. Use when the user asks to design, scaffold, revise, package, or troubleshoot a skill for Codex.
---

# Codex Skill Authoring

Use this skill to build skills that another Codex instance can use without extra explanation.

## Workflow

1. Identify the concrete user requests the skill should handle.
2. Choose a short hyphenated skill name that matches the task.
3. Decide whether the skill needs `scripts/`, `references/`, or `assets/`.
4. Initialize or update the skill folder.
5. Write frontmatter that clearly states what the skill does and when it triggers.
6. Keep the body imperative, concise, and specific.
7. Validate the skill before finishing.

## Writing Rules

- Put trigger conditions in the `description`, not in a later section.
- Prefer procedures over long explanation.
- Keep one primary workflow unless the skill truly needs multiple modes.
- Add resources only when they reduce repetition, ambiguity, or risk.

## Resource Guidance

- Use `scripts/` for deterministic automation or repeated transformations.
- Use `references/` for schemas, APIs, policies, or longer guidance.
- Use `assets/` for templates, boilerplate, or files that should be reused in output.

## Quality Check

- Would another Codex instance know exactly when to use this skill?
- Is the workflow narrow enough to follow without guessing?
- Are the resource files actually necessary?
