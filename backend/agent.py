"""The agent loop — no framework, built from scratch.

This is the core of the project: an LLM decides which tools to call,
we execute them, feed results back, and repeat until it has an answer.
"""

import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

from .models import StreamEvent
from .tools import TOOL_SCHEMAS, get_time, search_documents, web_search

load_dotenv()

MAX_STEPS = 5

SYSTEM_PROMPT = """You are a research agent. You answer questions by gathering information.

You have access to tools:
- search_documents(query): search the user's uploaded documents. Use when the answer might be in their own material.
- web_search(query): search the live web. Use for recent events, up-to-date facts, or anything not in the documents.
- get_time(): current date/time. Use when the question involves "now", "today", or dates.

Rules:
1. Decide what the question needs. You may call multiple tools in sequence if needed.
2. When you have enough information, answer with your final text answer.
3. Cite sources when you use them: mention document names or "web" in your answer.
4. If you cannot find an answer, say so honestly.
5. Keep answers clear and well-organized.
"""

TOOL_IMPLEMENTATIONS = {
    "search_documents": lambda args, store: search_documents(args.get("query", ""), store),
    "web_search": lambda args, store: web_search(args.get("query", "")),
    "get_time": lambda args, store: get_time(),
}


def run_agent_stream(user_message: str, history: list[dict], store) -> list[dict]:
    """Run the agent loop, yielding events: tool calls + final answer.

    Yields dicts matching StreamEvent. Returns a list for simplicity;
    the FastAPI layer streams them as SSE.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return [StreamEvent(type="error", error="GROQ_API_KEY not set. Create a .env file.").model_dump()]

    client = Groq(api_key=api_key)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Include conversation history so the agent remembers context
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_message})

    events: list[dict] = []

    for step in range(MAX_STEPS):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.3,
            )
        except Exception as e:
            # If tool calling itself failed (e.g. Groq rejecting a malformed
            # generated call), retry once with tools disabled so we still answer.
            if step == 0 and "tool_use_failed" in str(e):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages,
                        temperature=0.3,
                    )
                    answer = response.choices[0].message.content or ""
                    events.append(StreamEvent(type="done", content=answer).model_dump())
                    return events
                except Exception as e2:
                    events.append(StreamEvent(type="error", error=f"LLM call failed: {str(e2)}").model_dump())
                    return events
            events.append(StreamEvent(type="error", error=f"LLM call failed: {str(e)}").model_dump())
            return events

        choice = response.choices[0]
        message = choice.message

        # No tool call → the agent is done, answer is in the content
        if not message.tool_calls:
            answer = message.content or ""
            events.append(StreamEvent(type="done", content=answer).model_dump())
            return events

        # Execute each requested tool call
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            try:
                args = _parse_args(tool_call.function.arguments)
            except Exception:
                args = {}

            result = TOOL_IMPLEMENTATIONS[name](args, store) if name in TOOL_IMPLEMENTATIONS \
                else f"Unknown tool: {name}"

            events.append(StreamEvent(
                type="tool_call",
                tool=name,
                args=args,
                result=result[:500],  # keep stream lean
            ).model_dump())

            messages.append({
                "role": "assistant",
                "tool_calls": [tool_call.model_dump()],
                "content": None,
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    # Ran out of steps without a final answer
    events.append(StreamEvent(
        type="done",
        content="I hit my step limit trying to answer that. Could you rephrase the question?",
    ).model_dump())
    return events


def _parse_args(arguments: str) -> dict:
    """Parse JSON arguments from the tool call. Falls back to regex extraction."""
    try:
        return json.loads(arguments) if isinstance(arguments, str) else arguments
    except Exception:
        # Extract "key": "value" pairs as a last resort
        pairs = re.findall(r'"(\w+)":\s*"([^"]*)"', arguments)
        return {k: v for k, v in pairs}
