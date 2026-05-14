# FitByte Lead Qualification Agent

**Autonomous Agent Challenge Lab — Module 3**

A Telegram bot that qualifies fitness leads through 3 targeted questions and automatically routes them to the correct Notion sales team database using n8n and OpenAI.

## Files

| File | Description |
|---|---|
| `project_plan.md` | Complete project plan: use case, tech stack, MVP scope, risks, implementation phases |
| `lab_summary.md` | Reflection paragraph on hardest parts, open questions |
| `fitbyte_n8n_workflow.json` | Ready-to-import n8n workflow JSON |

## How to Run

### Prerequisites
- n8n instance (cloud or self-hosted)
- Telegram Bot token (from @BotFather)
- OpenAI API key
- Notion API key + 3 databases created

### Setup
1. **Import the workflow**: In n8n, go to Workflows → Import → paste `fitbyte_n8n_workflow.json`
2. **Create credentials** in n8n:
   - `FitByte Telegram Bot` — Telegram API credential with your bot token
   - `FitByte OpenAI` — OpenAI API credential
   - `FitByte Notion` — Notion API credential
3. **Create 3 Notion databases** with these properties:
   - `Name` (title), `Email` (email), `Fitness Goal` (rich text), `Tracking Preference` (rich text), `Training Intensity` (rich text), `Product Match` (select), `Source` (rich text), `Timestamp` (date)
4. **Replace placeholder IDs** in the 3 Notion nodes:
   - `YOUR_WATCH_DATABASE_ID`
   - `YOUR_RING_DATABASE_ID`
   - `YOUR_CHESTBAND_DATABASE_ID`
5. **Activate the workflow** — the Telegram webhook activates automatically

### Conversation Flow
```
User starts bot
  → Q1: Fitness goal (lose weight / build muscle / track performance / wellness)
  → Q2: Tracking preference (wrist / discreet ring / chest strap)
  → Q3: Training intensity (casual / regular / athlete)
  → Name collection
  → Email collection (with validation retry)
  → GPT-4o-mini classifies: WATCH / RING / CHESTBAND
  → Lead written to correct Notion table
  → Confirmation message sent to user
```
