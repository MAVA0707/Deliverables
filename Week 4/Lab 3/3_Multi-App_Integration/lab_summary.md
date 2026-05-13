# lab_summary.md — Telegram → Notion Blog Pipeline for FitByte

---

## Real-World Justification - Following Fitbyte AI Content Creator

Content teams waste significant time bridging inspiration and execution.
A founder, product manager, marketer, or subject matter expert will have a blog idea while commuting,
working out, or reviewing customer feedback — but by the time they sit down at their
desk, the spark is gone or buried in a chat thread. This workflow solves that gap for
any small team that uses Telegram for quick communication and Notion as their content
operating system.

**Who benefits:** A content lead at Fitbyte who wants to move from *idea → structured draft* 
without switching tools or waiting for a writing session to free up.

**What it replaces:** Manual copy-paste between Telegram, OpenAI, and
Notion; ad hoc idea logs that never become drafts; the cognitive overhead of
remembering to act on ideas captured in chat. Optimizing the content with 
good prompte engineering (Content Brief => Blogpost Creation)


**Outcome improvements:**
- Speed: idea → Notion draft in under 30 seconds, hands-free
- Accuracy: structured brief forces consistent angle + hook before the post is written
- Visibility: every request is logged in Notion with metadata (sender, brand fit score,
  best angle, status) — no more ideas lost in DMs

---

## Technical Paragraph

**Integration pair:** Telegram Trigger → Notion (Create Page), with three intermediate
HTTP Request nodes calling the Anthropic Claude API (Haiku model).

**Pipeline stages and field mapping (mirroring `content_pipeline.py`):**

| n8n Stage | Python Equivalent | Key Fields Produced |
|---|---|---|
| Telegram Trigger | — | `message.text`, `message.from.username`, `message.chat.id` |
| Set – Normalize | `ContentDocumenter.document()` | `topic`, `sender`, `chat_id`, `timestamp` |
| IF – Valid Idea? | Input validation in `run()` | Guard: non-empty, ≥5 chars |
| Telegram – Acknowledge | — | UX: immediate feedback |
| HTTP – Brief | `ContentBriefGenerator.generate()` | `content_brief` (ANGLE / HOOK / CORE INSIGHT …) |
| Set – Store Brief | — | Clean field reference |
| HTTP – Publish | `ContentPublisher.publish()` | `blog_body`, `blog_title` |
| Set – Parse Blog Content | — | Extract title from first `#` line |
| Notion – Create Page | `OutputManager.save_content()` | Notion page with properties + body blocks |
| Telegram – Confirm | — | UX: link back to created page |

The source JSON from Telegram is nested (`message.from.username`, `message.chat.id`).
The Set node immediately flattens this into top-level fields so every downstream node
reads simple `$json.topic` expressions rather than deep paths. Monitor output arrives
as a raw JSON string from Claude; a second Set node parses and promotes `brand_fit_score`
and `best_angle` explicitly so they map cleanly to Notion number/text properties.

**Hardest part:** The Notion "Create Page" node requires the database ID and property
names to match exactly (case-sensitive). Mismatches silently drop fields rather than
throwing errors, so testing required checking the Notion page after each run rather
than trusting the n8n success indicator alone. 


