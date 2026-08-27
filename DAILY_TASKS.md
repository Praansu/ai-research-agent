# Daily Tasks — ai-research-agent

Pick **one** task per day (5–10 min). Commit via PR so every change is reviewable and explainable in interviews.

## Backend (FastAPI + Python)

- [ ] Add type hints to one function in `backend/tools.py` or `backend/rag.py`
- [ ] Write one unit test for `search_documents` or `web_search` in `backend/test_tools.py` (create if missing)
- [ ] Refactor one function in `backend/agent.py` to reduce complexity (extract helper, rename vars)
- [ ] Add docstring + example to one FastAPI endpoint in `backend/main.py`
- [ ] Add one integration test for `/chat` SSE stream in `backend/test_chat.py`
- [ ] Replace one `print()` with proper `logging` call in `backend/agent.py`
- [ ] Add input validation (Pydantic) to one tool parameter in `backend/tools.py`
- [ ] Extract magic number/string to a constant at top of file

## Frontend (Vanilla HTML/JS)

- [ ] Add one accessibility improvement (aria-label, focus style, semantic HTML) in `frontend/index.html`
- [ ] Extract one inline style to CSS class in `frontend/index.html`
- [ ] Add error boundary for one tool-call card render
- [ ] Improve mobile layout for one section (media query)

## Docs / Meta

- [ ] Update `README.md` with one new example question or clarification
- [ ] Add one entry to `CHANGELOG.md` (create if missing) for recent change
- [ ] Fix one typo or unclear sentence in `README.md`
- [ ] Add one badge to `README.md` (e.g., Python version, license)

## Quality

- [ ] Run `ruff check backend/` → fix one lint warning
- [ ] Run `black --check backend/` → format one file
- [ ] Add `pre-commit` hook config (`.pre-commit-config.yaml`) if missing

---

**How to use:** Each morning, pick ONE unchecked item. Do it. Commit with message like `refactor: extract helper for tool parsing in agent.py`. Open PR. Merge after review. Check the box.