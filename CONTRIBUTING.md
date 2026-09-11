# Contributing to AI Research Agent

Thank you for considering contributing! This project is a learning portfolio piece, but contributions are welcome.

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear, focused commits
3. **Run tests and linting**: `ruff check backend/ && ruff format --check backend/`
4. **Open a Pull Request** with a clear description

## Code Style

- Python: ruff for linting and formatting
- Commit messages: Conventional Commits (e.g., `feat: add new tool`, `fix: handle empty upload`)

## Development Setup

```bash
git clone https://github.com/Praansu/ai-research-agent.git
cd ai-research-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn backend.main:app --reload
```

## Project Structure

```
ai-research-agent/
├── backend/
│   ├── agent.py      # Custom agent loop (no framework)
│   ├── rag.py        # ChromaDB + sentence-transformers
│   ├── tools.py      # search_documents, web_search, get_time
│   ├── llm.py        # Groq integration (streaming + non-streaming)
│   └── main.py       # FastAPI endpoints
├── frontend/
│   └── index.html    # Vanilla JS chat UI with SSE streaming
└── .github/workflows/ # CI/CD pipelines
```

## Areas for Contribution

- Add new tools (e.g., code execution, file operations)
- Improve RAG chunking strategy
- Add authentication/multi-user support
- Write unit/integration tests
- Improve frontend UX
- Add Docker Compose for production

## Questions?

Open an issue or email Praansu12@gmail.com