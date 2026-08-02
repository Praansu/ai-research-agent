"""AI Research Agent — FastAPI backend.

An agent that answers questions using uploaded documents (RAG)
and live web search (tool calling).
"""

import json
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .agent import run_agent_stream
from .models import ChatRequest, UploadResponse
from .rag import VectorStore
from .tools import index_document

load_dotenv()

app = FastAPI(title="AI Research Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

store: VectorStore | None = None


def get_store() -> VectorStore:
    global store
    if store is None:
        store = VectorStore()
    return store


@app.get("/health")
async def health():
    return {"status": "ok", "docs_indexed": get_store().count()}


@app.post("/upload", response_model=UploadResponse)
async def upload_doc(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".pdf", ".txt", ".md"}:
        raise HTTPException(400, "Only PDF, TXT, or MD files are allowed")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "File too large — max 20MB")

    doc_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{doc_id}{ext}"
    save_path.write_bytes(content)

    try:
        chunks, pages = index_document(save_path, doc_id, get_store())
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to index document: {str(e)}")

    return UploadResponse(doc_id=doc_id, filename=file.filename or "doc", chunks=chunks, pages=pages)


@app.post("/chat")
async def chat(req: ChatRequest):
    """Stream agent events: tool calls first, then the final answer."""
    if not req.message.strip():
        raise HTTPException(400, "Message cannot be empty")

    async def event_stream():
        for event in run_agent_stream(req.message, req.history, get_store()):
            yield f"data: {json.dumps(event)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Serve frontend — mounted last so it doesn't shadow API routes
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
