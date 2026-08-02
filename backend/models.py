"""Pydantic models for the research agent."""

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks: int
    pages: int


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)


class ToolCallEvent(BaseModel):
    type: str = "tool_call"
    tool: str
    args: dict
    result: str


class StreamEvent(BaseModel):
    type: str  # "tool_call" | "chunk" | "done" | "error"
    tool: str | None = None
    args: dict | None = None
    result: str | None = None
    content: str | None = None
    error: str | None = None
