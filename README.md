# AI Research Agent

[![CI](https://img.shields.io/github/actions/workflow/status/Praansu/ai-research-agent/ci.yml?style=flat-square)](https://github.com/Praansu/ai-research-agent/actions)
[![License](https://img.shields.io/badge/License-MIT-1F2328?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-1F2328?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-1F2328?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-1F2328?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

Custom agent loop built **from scratch**. No LangChain — I wanted to understand how tool calling actually works.

It decides by itself whether to check my docs (ChromaDB), search the web, or do both. Streams everything live so you can see what it's thinking.

Hardest part was stopping it from calling the wrong tool. Still tweaking that.

## How it Works

```
User Query
    │
    ▼
┌─────────────────────┐
│  Agent Loop (ReAct) │
└─────────┬───────────┘
    │
    ├──────────────────┐
    ▼                  ▼
┌──────────┐    ┌──────────────┐
│ ChromaDB │    │  Web Search  │
│  (RAG)   │    │  (Groq API)  │
└──────────┘    └──────────────┘
    │                  │
    └────────┬─────────┘
             ▼
    ┌────────────────┐
    │  Synthesis &   │
    │  Streaming Out │
    └────────────────┘
```

## Quick Start

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Add your Groq API key
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# 3. Add PDFs to data/ (optional)
# mkdir -p data && cp your-paper.pdf data/

# 4. Run
python main.py  # FastAPI on :8000
```

Or with Docker:
```bash
docker build -t ai-research-agent .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key ai-research-agent
```

Then open `http://localhost:8000` for the chat UI.

## Stack

| Layer | Tech |
|-------|------|
| Agent Loop | Custom ReAct implementation |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Groq (Llama 3 8B) |
| Web Search | Custom implementation |
| API | FastAPI + SSE streaming |
| Frontend | Simple HTML/JS (served by FastAPI) |

## Project Structure

```
ai-research-agent/
├── backend/
│   ├── agent.py          # ReAct loop
│   ├── rag.py            # ChromaDB + embeddings
│   ├── tools.py          # Tool definitions
│   ├── web_search.py     # Web search tool
│   └── main.py           # FastAPI app
├── frontend/             # Static chat UI
├── data/                 # PDF documents (gitignored)
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Features

- **Autonomous routing** — agent picks RAG vs web search
- **Live streaming** — see every tool call and thought
- **Document management** — upload/delete PDFs via UI
- **No framework lock-in** — raw Python, easy to modify

## Known Issues

- Slow on large PDFs — chunking strategy needs improvement
- Web search rate limits — no exponential backoff yet
- Single-user, no auth

## What I Learned

- Building an agent loop from scratch teaches you *why* frameworks exist
- Tool schema design is critical — vague schemas = wrong tool calls
- SSE streaming is simpler than WebSockets for this use case
- ChromaDB's simplicity is both strength and limitation