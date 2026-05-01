# Lab Summary: Which Chunking Strategy Should You Use?

## For PDF Documents → Go with Recursive Character Chunking

- It reads the document the way a human would — finishing a thought before moving on, never stopping mid-sentence
- In our tests, it kept sentences whole 100% of the time, while the simplest method broke them 80% of the time
- The pieces it creates are roughly the same size every time, so the AI can search through them reliably
- No special tools or accounts needed — it works out of the box

## For Podcast Transcripts → Go with Semantic Chunking

- Podcasts jump between topics in conversation, so cutting them into equal-sized pieces doesn't make sense — this method cuts them by *topic* instead
- It keeps related ideas together, so when you ask the AI a question it finds the right part of the conversation
- It handles the messy back-and-forth of real dialogue naturally, even when speakers switch frequently
- There are two versions: a more powerful one that needs an internet connection, and a simpler one that works fully offline

## The Main Trade-offs

- **Simplest method (Fixed-Size)** — quick to set up but it regularly cuts sentences in half, which confuses the AI when it tries to find answers
- **Our PDF pick (Recursive)** — takes a little more effort to configure but gives much cleaner results; works well for anything with a clear structure like reports or articles
- **Token-Based** — good for making sure you don't overload the AI with too much text at once, but it doesn't care about meaning so answers can feel out of context
- **Our Podcast pick (Semantic)** — gives the most meaningful pieces but takes longer to run and the piece sizes are less predictable

## Bottom Line

| Content type | What to use | Why it works |
|---|---|---|
| PDF | Recursive Character | Finishes sentences and respects the document's structure |
| Podcast | Semantic Chunking | Keeps related ideas together instead of splitting by length |

> Not sure which to pick? **Recursive Character Chunking** is the safest choice for almost anything — it's reliable, easy to use, and doesn't need any extra setup.
