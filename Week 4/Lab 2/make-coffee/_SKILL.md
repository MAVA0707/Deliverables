---
name: make-coffee
description: Guide coffee brewing step by step when the user wants to brew coffee, choose a method, or make a specific drink such as espresso, pour over, French press, Americano, or AeroPress. Use when the user asks for help like "make me a coffee", "how do I brew espresso", or "walk me through a pour over".
---

# Make Coffee

Use this skill to guide brewing a specific coffee drink in clear, ordered steps.

## Inputs To Confirm

Ask for the minimum needed before giving steps:

- What drink are they making?
- What equipment do they have?
- What beans and grind size do they have?
- How strong do they want it?

## Brewing Workflow

1. Confirm the drink type and equipment.
2. State the ratio from [references/ratios.md](references/ratios.md).
3. Walk through prep: grind, warm equipment, measure, and set up.
4. Walk through brewing: temperature, timing, pouring or extraction technique.
5. Serve and give one adjustment tip for next time.

## Output Format

Always include:

- Ingredient list with measurements
- Numbered steps in order
- Brew time and temperature where relevant
- One `to taste` adjustment tip at the end

## Gotchas

- Specify grind size whenever possible; it is a common failure point.
- Use 90-96°C water unless the method calls for something different.
- Do not apply espresso ratios to immersion methods.
- Include bloom for pour over and AeroPress style brews when appropriate.
- Mention warming cups or brewers when temperature retention matters.

## References

- See [references/ratios.md](references/ratios.md) for method-specific brew ratios.
- See [references/grind-guide.md](references/grind-guide.md) if the user is unsure about grind size.
