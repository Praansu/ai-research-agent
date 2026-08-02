"""Tools the agent can call: search_documents, web_search, get_time."""

import re
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Search previously uploaded documents (PDFs, notes, articles) for relevant passages. "
                "Use this when the question might be answered by the user's own documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query, usually the user's question.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the live web for current information. "
                "Use this for recent events, up-to-date facts, or anything not in the user's documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The web search query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current date and time. Use when the question involves 'now', 'today', or dates.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def index_document(path: str | Path, doc_id: str, store) -> tuple[int, int]:
    """Extract text from a document and store chunks in the vector store.

    Returns (chunk_count, page_count).
    """
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        pages, chunks = _index_pdf(path, doc_id, store)
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
        chunks = _chunk_text([{"page_num": 1, "text": text}], path.name)
        chunks = [{**c, "source": path.name} for c in chunks]
        store.add_document(doc_id, chunks)
        pages = 1
    return len(chunks), pages


def _index_pdf(path: Path, doc_id: str, store) -> tuple[int, list[dict]]:
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({"page_num": i + 1, "text": text})
    doc.close()
    chunks = _chunk_text(pages, path.name)
    store.add_document(doc_id, chunks)
    return len(pages), chunks


def _chunk_text(pages: list[dict], source: str, max_chars: int = 1000, overlap: int = 100) -> list[dict]:
    chunks = []
    for page in pages:
        sentences = re.split(r"(?<=[.!?])\s+", page["text"])
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) > max_chars and current:
                chunks.append({"text": current.strip(), "page_num": page["page_num"], "source": source})
                current = current[-overlap:] if overlap > 0 else ""
            current += sentence + " "
        if current.strip():
            chunks.append({"text": current.strip(), "page_num": page["page_num"], "source": source})
    return chunks


def search_documents(query: str, store) -> str:
    """Search indexed documents, return formatted passages with sources."""
    results = store.search(query, top_k=3)
    if not results:
        return "No relevant passages found in the uploaded documents."
    parts = []
    for r in results:
        src = r.get("source", "document")
        page = r.get("page_num", 0)
        parts.append(f"[{src} p.{page}] {r['text']}")
    return "\n\n".join(parts)


def web_search(query: str) -> str:
    """Search the web via DuckDuckGo HTML (no API key needed)."""
    import httpx
    from bs4 import BeautifulSoup

    url = "https://html.duckduckgo.com/html/"
    try:
        resp = httpx.get(url, params={"q": query}, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-agent/1.0"
        })
        resp.raise_for_status()
    except Exception as e:
        return f"Web search failed: {str(e)}"

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for res in soup.select(".result")[:5]:
        link = res.select_one("a.result__a")
        snippet = res.select_one("a.result__snippet")
        if link:
            title = link.get_text(strip=True)
            href = link.get("href", "")
            body = snippet.get_text(strip=True) if snippet else ""
            results.append(f"{title}\n{body}\n{href}")

    if not results:
        return "No web results found."
    return "\n\n".join(results)


def get_time() -> str:
    return datetime.now().strftime("%A, %Y-%m-%d %H:%M")
