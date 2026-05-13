# n8n Lab Reference Guide

## Overview

This document serves as a comprehensive reference for n8n workflow automation. It covers node configurations, JSON data flow, transformation patterns, and workflow analysis findings across all lab exercises.

---

## Node Reference Table

| Node | Parameters | Settings | What It Does | JSON Input | JSON Output | Key Transformations |
|------|------------|----------|--------------|------------|-------------|---------------------|
| Webhook | Method, Path, Response Mode | Auth, Response Code | Receives HTTP requests and starts a workflow | HTTP request (headers, body, query params) | n8n data format with request details | HTTP → n8n format |
| HTTP Request | Method, URL, Auth Type, Body | Response Format, Custom Headers, Timeout | Makes outbound API calls to external services | n8n data (used to build request) | API response body | n8n → API call → n8n |
| Set | Keep Fields, Values, Field names | Assignments mode | Adds, modifies, or removes fields in the data | Any JSON object | Modified JSON with new/removed fields | Field manipulation |
| Function | Function Code | Mode (Run Once / Per Item) | Runs custom JavaScript to transform data | Any JSON | Any JSON (custom shaped) | Custom JS transformation |
| IF | Condition, Value1, Operation, Value2 | Combine Conditions (AND/OR) | Routes data down true or false branch based on a condition | Any JSON | Same JSON sent to true or false output | Conditional routing |
| OpenAI | Operation, Model, Messages / Prompt | Resource, Max tokens, Temperature | Calls the OpenAI API for completions, embeddings, and more | Prompt data (messages array or string) | AI-generated response object | Text generation |
| Switch | Rules (value + output) | Mode (rules / expression) | Routes data to one of many output branches based on rules | Any JSON | Same JSON sent to matching output branch | Multi-route switching |
| Merge | Mode (Append / Wait / Multiplex) | Options | Combines data from two or more parallel branches | Multiple data streams | Merged item list | Data combination |
| Split In Batches | Batch Size | Reset (loop control) | Splits a large array into smaller chunks for processing | Array of items | Batches of N items | Array splitting |
| Wait | Amount, Unit (seconds/minutes/hours) | Resume (webhook / time) | Pauses the workflow for a set duration or until a signal | Any JSON | Same JSON (after delay) | Time delay |
| Code | Code | Language (JS / Python) | Executes Python or JavaScript code with full language support | Any JSON | Any JSON (code output) | Code execution |
| Notion | Operation, Resource (database/page), Properties | Database ID, Page ID, Auth | Reads and writes to Notion databases and pages | n8n data | Notion API response | Database operations |
| Form Trigger | formTitle, formDescription, formFields (label, type, name, acceptFileTypes) | appendAttribution | Presents an HTML form; on submit triggers the workflow with file/field data | Browser form submission | Binary file data + field values as n8n items | Form upload → n8n binary |
| Pinecone Vector Store (insert) | mode: insert, pineconeIndex | options | Embeds and upserts document chunks into a Pinecone index | Document chunks + embeddings | Upsert confirmation | Text chunks → vector DB |
| Pinecone Vector Store (retrieve) | mode: retrieve-as-tool, pineconeIndex, topK, useReranker | toolDescription | Semantic similarity search; returns top-K chunks, optionally reranked | Query embedding vector | Ranked document chunks | Vector search → context |
| OpenAI Embeddings | dimensions (512) | — | Converts text to a numeric embedding vector for storage or search | Plain text string | 512-dim float array | Text → embedding vector |
| Document Loader | dataType: binary, textSplittingMode | — | Parses uploaded binary files (PDF, CSV, JSON) into raw text | Binary file item | Raw text document | Binary file → text |
| Text Splitter | — | chunkSize, chunkOverlap | Splits long text into overlapping chunks for vector storage | Raw text document | Array of text chunks | Long text → chunks |
| LM Chat (OpenAI) | model (gpt-4.1-mini) | builtInTools, options | Provides the language model brain for an AI agent | Agent prompt + context | Model completion | Prompt → chat response |
| Agent (RAG) | systemMessage | options | Orchestrates tool use — calls retrieval tool, feeds context to LM, returns answer | User chat message | Grounded answer with citations | Query → retrieve → respond |
| Cohere Reranker | — | cohereApi credential | Re-scores retrieved chunks by semantic relevance before passing to the LM | Array of candidate chunks | Re-ranked + scored chunks | Chunks → relevance-sorted |

---

## Node Categories

### Trigger Nodes
Trigger nodes start a workflow. They listen for an event and fire when it occurs.

- **Webhook** — listens for incoming HTTP requests

### Integration Nodes
Integration nodes connect n8n to external services and APIs.

- **HTTP Request** — generic outbound API calls to any REST endpoint
- **Notion** — purpose-built integration for Notion databases and pages

### Transform Nodes
Transform nodes reshape data as it passes through the workflow.

- **Set** — add, update, or delete specific fields
- **Function** — full JavaScript logic for complex transformations
- **Code** — JavaScript or Python for advanced processing

### Logic Nodes
Logic nodes control which path data takes through the workflow.

- **IF** — binary true/false branching
- **Switch** — multi-path routing based on rules

### Flow Nodes
Flow nodes manage timing, sequencing, and data volume.

- **Merge** — combine parallel branches back into one stream
- **Split In Batches** — break large arrays into manageable chunks
- **Wait** — pause execution for a set duration

### AI Nodes
AI nodes integrate machine learning and language model capabilities.

- **OpenAI** — completions, chat, embeddings, and image generation
- **LM Chat (OpenAI)** — language model sub-node powering an agent
- **OpenAI Embeddings** — converts text to vector embeddings for storage or search
- **Agent (RAG)** — orchestrates tool calls, retrieval, and response generation
- **Cohere Reranker** — re-scores retrieved chunks by semantic relevance

### RAG / Vector Nodes
Nodes for building retrieval-augmented generation pipelines.

- **Form Trigger** — collects file uploads via a browser form
- **Document Loader** — parses binary files (PDF, CSV, JSON) into text
- **Text Splitter** — chunks long text into overlapping segments
- **Pinecone Vector Store** — inserts embeddings or retrieves top-K similar chunks

---

## JSON Data Flow Patterns

### Standard n8n Item Structure

All nodes pass data as an array of items. Each item wraps the payload in a `json` key:

```json
[
  {
    "json": {
      "field1": "value1",
      "field2": "value2"
    }
  }
]
```

### Webhook Input Example

An incoming POST request is converted to the following n8n format:

```json
[
  {
    "json": {
      "headers": {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
      },
      "params": {},
      "query": {},
      "body": {
        "name": "Alice",
        "email": "alice@example.com"
      }
    }
  }
]
```

### HTTP Request Output Example

A successful API call returns the response body wrapped in n8n format:

```json
[
  {
    "json": {
      "id": 42,
      "name": "Alice",
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z"
    }
  }
]
```

### OpenAI Response Example

The OpenAI node returns the full API response object:

```json
[
  {
    "json": {
      "id": "chatcmpl-abc123",
      "object": "chat.completion",
      "model": "gpt-4",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "Here is the generated response..."
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 50,
        "completion_tokens": 120,
        "total_tokens": 170
      }
    }
  }
]
```

> **Tip:** To access just the text, use an expression like `{{ $json.choices[0].message.content }}` in the next node.

---

## Key Transformation Patterns

### Pattern 1: Extracting a Nested Value (Set Node)

Use the Set node to promote a deeply nested field to the top level.

**Input:**
```json
{ "response": { "data": { "userId": 99 } } }
```

**Set node assignment:**
- Field name: `userId`
- Value: `{{ $json.response.data.userId }}`

**Output:**
```json
{ "userId": 99 }
```

---

### Pattern 2: Conditional Branching (IF Node)

Route items based on a field value.

| Setting | Value |
|---------|-------|
| Value 1 | `{{ $json.status }}` |
| Operation | Equal |
| Value 2 | `active` |

- **True branch** → process active users
- **False branch** → log or skip inactive users

---

### Pattern 3: Batch Processing (Split In Batches + HTTP Request)

Process large lists without hitting API rate limits.

```
[Array of 500 items]
       ↓
Split In Batches (Batch Size: 10)
       ↓
HTTP Request (runs once per batch)
       ↓
Merge
       ↓
[Combined results]
```

---

### Pattern 4: AI Enrichment (Set + OpenAI + Set)

Enrich records with AI-generated content.

```
Input record
    ↓
Set node — build prompt string
    ↓
OpenAI node — generate content
    ↓
Set node — extract choices[0].message.content → attach to original record
    ↓
Enriched record
```

---

### Pattern 5: Parallel API Calls (HTTP Request + Merge)

Fan out to multiple APIs simultaneously, then combine results.

```
Webhook
    ↓
HTTP Request A          HTTP Request B
(fetch user data)       (fetch order data)
        \                   /
         → Merge (Append) ←
                ↓
        Combined dataset
```

### Pattern 6: Multi-Route Switching (Switch Node)

Route items to different branches based on a field value.

**Input:**
```json
{ "json": { "plan": "pro" } }
```

**Switch rules:**
| Rule | Output branch |
|------|--------------|
| `plan` equals `free` | Branch 0 |
| `plan` equals `pro` | Branch 1 |
| `plan` equals `enterprise` | Branch 2 |

**Output** (sent to Branch 1 — unchanged data, different path):
```json
{ "json": { "plan": "pro" } }
```

---

### Pattern 7: Merging Two Branches (Merge Node)

Combine results from a parallel fan-out back into one stream.

**Input A (user data branch):**
```json
{ "json": { "userId": 1, "name": "Alice" } }
```

**Input B (order data branch):**
```json
{ "json": { "userId": 1, "orderTotal": 149.99 } }
```

**Output (Append mode — both items in one array):**
```json
[
  { "json": { "userId": 1, "name": "Alice" } },
  { "json": { "userId": 1, "orderTotal": 149.99 } }
]
```

---

### Pattern 8: Batch Splitting (Split In Batches Node)

Break a 500-item array into chunks of 10 for rate-safe API calls.

**Input (full array):**
```json
[
  { "json": { "id": 1, "email": "a@example.com" } },
  { "json": { "id": 2, "email": "b@example.com" } },
  "...497 more items"
]
```

**Output per loop iteration (Batch Size: 10):**
```json
[
  { "json": { "id": 1, "email": "a@example.com" } },
  { "json": { "id": 2, "email": "b@example.com" } },
  "...8 more items"
]
```

> The node loops automatically until all batches are processed. Connect a Merge node at the end to collect all results.

---

### Pattern 9: Timed Delay (Wait Node)

Pass data through unchanged after a pause — useful before retry or rate-limited API calls.

**Input:**
```json
{ "json": { "jobId": "abc-123", "status": "pending" } }
```

**Configuration:**
- Amount: `5`
- Unit: `seconds`

**Output (after 5 s delay — identical to input):**
```json
{ "json": { "jobId": "abc-123", "status": "pending" } }
```

---

### Pattern 10: Custom Code Transformation (Code Node)

Calculate a derived field and return a reshaped item.

**Input:**
```json
{ "json": { "firstName": "Alice", "lastName": "Smith", "score": 87 } }
```

**Code (JavaScript):**
```javascript
return items.map(item => ({
  json: {
    fullName: item.json.firstName + ' ' + item.json.lastName,
    grade: item.json.score >= 80 ? 'pass' : 'fail'
  }
}));
```

**Output:**
```json
{ "json": { "fullName": "Alice Smith", "grade": "pass" } }
```

---

### Pattern 11: Notion Database Write (Notion Node)

Create a new page (row) in a Notion database.

**Input:**
```json
{ "json": { "title": "Follow up with Alice", "status": "To Do", "due": "2025-06-01" } }
```

**Configuration:**
- Operation: `Create`
- Resource: `Database Page`
- Database ID: `<your-database-id>`
- Properties mapped from `$json.title`, `$json.status`, `$json.due`

**Output (Notion API response):**
```json
{
  "json": {
    "id": "page-uuid-here",
    "object": "page",
    "created_time": "2025-06-01T09:00:00.000Z",
    "properties": {
      "Name": { "title": [{ "plain_text": "Follow up with Alice" }] },
      "Status": { "select": { "name": "To Do" } }
    }
  }
}
```

---

## Workflow Analysis Checklist

Use this checklist when documenting a new workflow:

### Per Node
- [ ] Node type identified
- [ ] All parameters listed (required vs. optional noted)
- [ ] Settings tab reviewed and documented
- [ ] Input JSON structure captured (copy from execution view)
- [ ] Output JSON structure captured
- [ ] Transformation described (fields added / removed / modified)
- [ ] Any expressions or dynamic values noted

### Per Workflow
- [ ] Entry point (trigger) identified
- [ ] All branches mapped
- [ ] Error handling nodes noted
- [ ] External services / credentials documented
- [ ] Data retained vs. discarded at each step noted

---

## Common Expressions Reference

| Goal | Expression |
|------|------------|
| Access current item field | `{{ $json.fieldName }}` |
| Access previous node output | `{{ $node["Node Name"].json.fieldName }}` |
| Current timestamp (ISO) | `{{ $now.toISO() }}` |
| Format date | `{{ $now.toFormat('yyyy-MM-dd') }}` |
| Count input items | `{{ $input.all().length }}` |
| Access item index | `{{ $itemIndex }}` |
| String concatenation | `{{ $json.firstName + ' ' + $json.lastName }}` |
| Conditional value | `{{ $json.score > 80 ? 'pass' : 'fail' }}` |
| Parse JSON string | `{{ JSON.parse($json.rawData) }}` |
| Stringify to JSON | `{{ JSON.stringify($json.data) }}` |

---

## Node Version Notes

| Node | Note |
|------|------|
| Function vs. Code | **Code** node (v1.0+) supersedes **Function**. Both support JS; Code also supports Python. Prefer Code for new workflows. |
| Set (v2) | The current Set node uses an assignment-based UI. Older workflows may use the legacy mode — check the node version badge. |
| OpenAI | Operation names changed in n8n v1.x. Verify `Chat`, `Complete`, and `Embed` operation labels match your n8n version. |
| Merge (Multiplex mode) | Outputs a combination of every item from both inputs — use carefully with large datasets. |

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Node shows no output | Upstream node failed silently | Check execution log; add error branch |
| Expression returns `undefined` | Wrong field path | Use execution view to inspect actual JSON keys |
| IF always goes false | Type mismatch (string vs number) | Cast with `Number($json.value)` or `String(...)` |
| HTTP Request 401 error | Missing or expired credential | Re-authenticate in Credentials settings |
| Merge output missing items | Branch finished before other | Switch Merge mode to `Wait` |
| OpenAI rate limit error | Too many requests per minute | Add a Wait node (1–2 seconds) before OpenAI |
| Split In Batches loops forever | `Reset` not configured | Set Reset to `true` at the end of the loop branch |

---

---

## RAG Workflow — Document Upload Chatbot with Cohere Reranking

### Workflow Overview

This workflow has two sub-flows triggered independently:

```
SUB-FLOW 1 — Document Ingestion
Upload Documents Form (Form Trigger)
    ↓
Document Loader  ←  Text Splitter
    ↓
Store in Pinecone  ←  OpenAI Embeddings (512-dim)

SUB-FLOW 2 — Chat & Retrieval
Chat Interface (Chat Trigger)
    ↓
RAG Agent
    ├── OpenAI Chat Model (gpt-4.1-mini)   [language model]
    └── Retrieve from Pinecone              [retrieval tool]
            ├── Query Embeddings (512-dim)
            └── Cohere Reranker
```

### Node-by-Node Analysis

#### Form Trigger — `Upload Documents Form`
| Field | Value |
|-------|-------|
| Form title | Upload Documents for RAG |
| Accepted types | `.pdf`, `.csv`, `.json` |
| Field name | `documents` |
| Output | Binary file item passed to Document Loader |

#### Document Loader
| Field | Value |
|-------|-------|
| dataType | `binary` |
| textSplittingMode | `custom` (delegates to Text Splitter sub-node) |

**Output chunk example:**
```json
{
  "pageContent": "Section 3: Results showed a 42% improvement...",
  "metadata": { "source": "report.pdf", "page": 3 }
}
```

#### Text Splitter
Recursively splits text using `RecursiveCharacterTextSplitter`. Default settings create overlapping chunks to preserve context across chunk boundaries.

#### OpenAI Embeddings (insert path)
- **Model:** `text-embedding-3-small` (512 dimensions)
- Converts each chunk to a float vector before upsert into Pinecone.

#### Store in Pinecone
- **Mode:** `insert`
- **Index:** `test-n8n`
- Upserts chunk text + 512-dim vector + metadata into the index.

---

#### Chat Trigger — `Chat Interface`
- **public:** `true` — generates a shareable chat URL
- **Initial message:** *"Hello! I can answer questions about your uploaded documents."*

#### RAG Agent
- **System message:** Answer ONLY from retrieved context; cite source documents; fall back to *"I couldn't find that in the uploaded documents."* if context is insufficient.
- Connects to: OpenAI Chat Model (LM) + Retrieve from Pinecone (tool)

#### Query Embeddings (retrieve path)
- Same model and dimensions (512) as the insert path — **must match** or similarity scores will be meaningless.

#### Cohere Reranker
- Re-scores the top-5 Pinecone results by deeper semantic relevance before the agent sees them.
- Credential: Cohere API key.

**Reranker output example:**
```json
[
  { "pageContent": "Most relevant chunk...", "score": 0.97 },
  { "pageContent": "Second best chunk...",  "score": 0.84 },
  { "pageContent": "Third chunk...",         "score": 0.61 }
]
```

#### Retrieve from Pinecone
- **Mode:** `retrieve-as-tool` — exposed as a callable tool to the RAG Agent
- **topK:** 5
- **useReranker:** `true` (Cohere Reranker sub-node attached)

#### OpenAI Chat Model
- **Model:** `gpt-4.1-mini`
- Generates the final answer grounded in the reranked chunks.

---

### Key RAG Design Decisions

| Decision | Why it matters |
|----------|---------------|
| 512-dim embeddings (not 1536) | Lower cost and faster retrieval; sufficient for document Q&A |
| Cohere reranking after top-5 retrieval | Vector similarity alone can miss semantically close but lexically different matches; reranking corrects this |
| `retrieve-as-tool` mode | Lets the agent decide *when* to retrieve, enabling multi-turn conversations without forced retrieval every turn |
| System message citation requirement | Grounds answers and makes hallucinations easier to spot |
| Two separate Pinecone indexes (`test-n8n` for insert, `n8n` for retrieve) | Likely a dev/prod split — ensure both indexes use the same embedding dimensions |

---

## Lab Exercises Index

| Exercise | Workflow | Nodes Covered |
|----------|----------|---------------|
| 3.1 | Workflow 1 — Basic HTTP | Webhook, HTTP Request, Set |
| 3.2 | Workflow 1 — Node Analysis | IF, Function, Set |
| 3.3 | Workflow 2 | OpenAI, Switch, Merge |
| 3.3 | Workflow 3 | Split In Batches, Wait, Code, Notion |
| 3.4 | All Workflows | Full reference table (this document) |
| RAG Lab | Document Upload RAG Chatbot with Cohere Reranking | Form Trigger, Document Loader, Text Splitter, OpenAI Embeddings, Pinecone Vector Store (insert + retrieve), Chat Trigger, RAG Agent, LM Chat OpenAI, Cohere Reranker |

---

*Last updated: May 2026 — n8n Lab Reference Guide*
