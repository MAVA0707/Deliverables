# Chunking Strategies Lab

Explore and compare four text-chunking strategies for building RAG (Retrieval-Augmented Generation) systems. The lab uses two content types — a **structured PDF document** and a **podcast audio file** — and applies Fixed-Size, Recursive Character, Token-Based, and Semantic (TF-IDF) chunking to both, producing comparison tables, boundary-quality analysis, and four visualisation charts.

---

## File & Folder Map

```
chunking-strategies-lab/
│
├── chunking_strategies.ipynb   # Main notebook — all code, results, and charts
├── .env                        # API keys (create this yourself, never commit it)
├── .env.example                # Template showing which keys are needed
│
├── transcriptions/             # Auto-created on first run
│   └── <audio_stem>.txt        # Whisper transcription cached here (one file per audio)
│
├── audio_chunks/               # Auto-created only when an audio file exceeds 25 MB
│   └── chunk_*.mp3             # Split segments sent to Whisper individually
│
├── README.md                   # This file
└── lab_summary.md              # One-paragraph findings summary (required submission file)
```

> **Your source files go in the same folder as the notebook:**
> ```
> chunking-strategies-lab/
> ├── my_document.pdf             # ← drop your PDF here
> └── podcast_episode.mp3         # ← drop your audio file here
> ```

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.9+ | Tested on 3.12 |
| `OPENAI_API_KEY` | Required for Whisper transcription only |
| Audio file | MP3, WAV, M4A, FLAC, OGG, or WEBM; max 25 MB per file |
| PDF file | Any standard PDF; multi-page supported |

---

## Setup

**1. Clone / download the repository**

```bash
git clone <your-repo-url>
cd chunking-strategies-lab
```

**2. Create a `.env` file** with your OpenAI key:

```bash
# .env
OPENAI_API_KEY=sk-...
```

There is a `.env.example` file in the repo you can copy and fill in:

```bash
cp .env.example .env
# then edit .env and paste your key
```

**3. Install dependencies** (the first notebook cell does this automatically, but you can also run it manually):

```bash
pip install langchain langchain-community langchain-text-splitters \
            PyPDF2 openai python-dotenv matplotlib seaborn scikit-learn pydub
```

---

## How to Run

**Open the notebook:**

```bash
jupyter notebook chunking_strategies.ipynb
# or
jupyter lab chunking_strategies.ipynb
```

Then run cells top-to-bottom (`Shift+Enter` or **Run All**). The two user-configuration cells are the only ones you need to edit.

---

## Configuration

There are exactly **two lines to change** in the notebook before running:

### Cell 6 — PDF source

```python
PDF_PATH = "my_document.pdf"   # path to your PDF, or None for synthetic fallback
```

| Value | Behaviour |
|---|---|
| `"filename.pdf"` | Extracts text from that file using PyPDF2 |
| `None` | Uses the built-in synthetic Trustworthy AI document |

### Cell 9 — Audio source

```python
AUDIO_PATH = "podcast_episode.mp3"   # path to your audio, or None for synthetic fallback
```

| Value | Behaviour |
|---|---|
| `"filename.mp3"` | Sends file to OpenAI Whisper; saves transcript to `transcriptions/` |
| `None` | Uses the built-in synthetic podcast transcript |

> **Re-runs are free:** If a transcription file already exists in `transcriptions/`, Whisper is **not called again** — the cached `.txt` is loaded directly.

> **Large audio files (> 25 MB):** The notebook automatically splits the file into chunks using `pydub`, transcribes each chunk, and concatenates the results.

---

## Notebook Cell Guide

| Cell(s) | Section | What it does |
|---|---|---|
| 0 | Setup & Installs | `pip install` all dependencies |
| 1 | Imports & Config | Loads `.env`, initialises OpenAI client, creates `transcriptions/` folder |
| 2 | **Load PDF** | Extracts text from your PDF (or uses synthetic fallback) |
| 3–4 | **Audio & Transcription** | Splits large audio if needed, calls Whisper, saves `.txt` to `transcriptions/` |
| 5 | Utility Functions | `token_count`, `chunk_stats`, `token_split`, `semantic_chunk_tfidf` helpers |
| 6 | Load Source Texts | Confirms `pdf_text` and `podcast_text` variables are ready |
| 7 | Strategy 1 – Fixed-Size | `CharacterTextSplitter` at 500 / 1000 / 2000 chars with varying overlap |
| 8 | Strategy 2 – Recursive | `RecursiveCharacterTextSplitter` — tries `\n\n → \n → . → space` before splitting mid-word |
| 9 | Strategy 3 – Token-Based | Character-budget splitter approximating token counts (4 chars ≈ 1 token) |
| 10 | Strategy 4 – Semantic | TF-IDF cosine similarity splits; replace with SentenceTransformer in production |
| 11 | Comparison Table | Side-by-side stats: chunk count, mean/median/std chars, approx tokens, broken endings % |
| 12–15 | Visualisations | Four charts: size histograms, box plots, broken-endings bar chart, overlap sensitivity |
| 16 | Boundary Analysis | Per-strategy % of chunks ending mid-sentence and starting with a speaker turn |
| 17 | Recommendations | Final strategy picks with reasoning and trade-off table |

---

## Outputs

| File | Description |
|---|---|
| `transcriptions/<stem>.txt` | Plain-text Whisper transcript, cached for re-use |
| `lab_summary.md` | One-paragraph submission summary |
| Inline charts | Four matplotlib figures rendered inside the notebook |

---

## Strategy Quick Reference

| Strategy | Chunk boundaries | Best for | Broken endings |
|---|---|---|---|
| Fixed-Size | Hard character limit | Uniform / simple corpora | High (~80%) |
| **Recursive** ✅ | Paragraph → sentence → word | **Structured PDFs** | ~0% |
| Token-Based | Character budget (≈ tokens) | LLM context-window control | Medium |
| **Semantic** ✅ | Meaning-shift detection | **Podcast / conversational text** | ~0% |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `AuthenticationError` | Check that `OPENAI_API_KEY` is set in your `.env` file |
| `File not found` for PDF or audio | Make sure the file is in the **same directory** as the notebook |
| Audio exceeds 25 MB limit | The notebook handles this automatically via `pydub`; install `ffmpeg` if `pydub` raises an error (`brew install ffmpeg` / `apt install ffmpeg`) |
| `ModuleNotFoundError` | Re-run Cell 0 to reinstall dependencies |
| Transcription is slow | Whisper processes ~1 min of audio per API call second; large files may take a few minutes |
