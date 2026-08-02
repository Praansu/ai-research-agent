# AI Research Agent

An AI agent that answers questions by combining **your uploaded documents** (RAG) and **live web search** — without any agent framework. The agent loop, tool calling, and retrieval are all built from scratch.

![stack](https://img.shields.io/badge/Python-3.11-3776AB?logo=python) ![framework](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi) ![llm](https://img.shields.io/badge/Groq-Llama_3.1_8B_Instant-f55036?logo=groq) ![rag](https://img.shields.io/badge/ChromaDB-vector-blue)

## What it does

Upload a PDF, TXT, or Markdown file — then ask anything. The agent decides **itself** which tools to use:

| Tool | What it does |
|------|-------------|
| 🔍 `search_documents` | Retrieves relevant passages from your uploaded files (semantic search, ChromaDB + MiniLM embeddings) |
| 🌐 `web_search` | Searches the live web (DuckDuckGo, no API key) |
| 🕐 `get_time` | Tells the agent the current date/time so it can reason about "recent" |

Example: *"What did I upload about transformers, and what's the latest news on them?"* → the agent searches your document, then searches the web, then combines both into one answer — with the tool calls shown live in the UI.

## How it works

```
user message
   │
   ▼
┌─────────────────────────── agent loop ───────────────────────────┐
│  LLM decides: call tool(s) or answer?                            │
│   ├─ search_documents(query) → vector search over your files     │
│   ├─ web_search(query)       → live search results               │
│   └─ get_time()              → current date/time                 │
│  tool results fed back to the LLM … repeat until it answers      │
└───────────────────────────────────────────────────────────────────┘
   │
   ▼
streamed answer (SSE) + live tool-call cards in the chat UI
```

- **Agent loop** — `backend/agent.py`: no LangChain, no frameworks. A plain loop that sends the conversation + tool schemas to the LLM, executes requested tools, feeds results back, and repeats (max 5 steps).
- **RAG** — `backend/rag.py`: documents are chunked (`tools.py`), embedded with `all-MiniLM-L6-v2`, stored in ChromaDB, and retrieved with cosine similarity.
- **Streaming** — `backend/main.py`: tool calls stream to the browser first, then the final answer (SSE).

## Getting started

### 1. Get a free API key

1. Create a free account at [console.groq.com](https://console.groq.com)
2. Go to **API Keys** → **Create API Key** (free tier — the agent uses Llama 3.1 8B Instant, which is fast and supports tool calling)
3. Copy the key

### 2. Run it locally

```bash
# 1. Copy the env template and paste your key
cp .env.example .env        # then edit .env:
                            # GROQ_API_KEY=your-key-here

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn backend.main:app --reload
```

Open **http://localhost:8000** — upload a document and ask away.

> First startup downloads the sentence-transformers model (~90MB) — it takes a minute or two.

### With Docker

```bash
docker build -t ai-research-agent .
docker run -p 8000:8000 -e GROQ_API_KEY=your-key-here ai-research-agent
```

## Project structure

```
backend/
  main.py      # FastAPI app — /health, /upload, /chat (SSE streaming)
  agent.py     # the agent loop (tool calling, no framework)
  rag.py       # vector store — embeddings + retrieval (ChromaDB)
  tools.py     # tool schemas + implementations (documents, web, time)
  models.py    # request/response schemas
frontend/
  index.html   # chat UI with live tool-call cards
```

## Example questions to try

- *"What did I upload about neural networks?"* → document search
- *"What's the latest AI news this week?"* → web search
- *"What did I upload about transformers, and what's the latest news on them?"* → both (the signature demo)
