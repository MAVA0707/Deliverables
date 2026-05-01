# RAG with OpenAI — Native Implementation

A complete Retrieval-Augmented Generation (RAG) pipeline built with OpenAI's APIs directly — no frameworks like LangChain or LlamaIndex. Feed it a folder of PDF files and ask questions; it retrieves the most relevant passages and returns a cited, grounded answer.

---

## How it works

```
📁 pdfs/
  └── your_file.pdf
        ↓
  Extract text → Chunk (200 tokens) → Embed → In-Memory Vector Store
                                                        ↓
  User Question → Embed → Cosine Similarity Search → Top 3 Chunks → GPT → Answer
```

---

## Project structure

```
.
├── rag_openai_native.ipynb   # Main notebook — run this
├── pdfs/                     # Drop your PDF files here
├── rag_results.json          # Generated after Q&A session (Step 10)
├── lab_summary.md            # Design decisions write-up
└── README.md                 # This file
```

---

## Setup

**1. Clone the repo and enter the folder**

```bash
git clone <your-repo-url>
cd <repo-folder>
```

**2. Install dependencies**

```bash
pip install openai pypdf tiktoken python-dotenv
```

**3. Add your OpenAI API key**

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

**4. Add your PDFs**

Drop any `.pdf` files into the `pdfs/` folder. The folder is created automatically when you run the notebook if it doesn't exist yet.

---

## Running the notebook

Open `rag_openai_native.ipynb` in Jupyter and run all cells from top to bottom.

```bash
jupyter notebook rag_openai_native.ipynb
```

| Step | What happens |
|------|-------------|
| 1 | Installs packages and initialises the OpenAI client |
| 2 | Scans the `pdfs/` folder and lists found files |
| 3 | Extracts text from every PDF page by page |
| 4 | Chunks the text into 200-token windows with 40-token overlap |
| 5 | Generates embeddings via `text-embedding-3-small` |
| 6 | Stores chunks + vectors in an in-memory vector store |
| 7 | Retrieval test — embed a question, find top-3 matching chunks |
| 8 | Full RAG function — retrieval + GPT answer with citations |
| 9 | Interactive Q&A loop — type questions, type `quit` to stop |
| 10 | Saves all Q&A pairs to `rag_results.json` |

---

## Models used

| Purpose | Model |
|---------|-------|
| Embeddings | `text-embedding-3-small` (1536 dimensions) |
| Answer generation | `gpt-4o-mini` |

Both can be swapped in the notebook constants (`EMBEDDING_MODEL`, `CHAT_MODEL`).

---

## Notes

- **Scanned PDFs** (image-only) won't produce text via `pypdf`. Add OCR support with `pytesseract` if needed.
- **Chunk size** defaults to 200 tokens with 40-token overlap — adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your documents.
- The vector store is **in-memory only** and resets when the kernel restarts. For persistence, export to a file or swap in FAISS / Pinecone.
