# app/api/routes.py
# FastAPI backend — now powered by the full agent loop

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests as http_requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.rag.pipeline import retrieve_context, build_rag_prompt
from app.core.agent import run_agent, TOOLS_DESCRIPTION

app = FastAPI(title="QuestKeeper API", version="1.0")

# DM personality — combined with tools description
# Agent needs to know both who Aldric is AND what tools he has
BASE_SYSTEM_PROMPT = """You are Aldric, a wise and dramatic Dungeon Master.
You speak in an atmospheric, immersive tone.
You remember everything the player tells you.
Keep responses under 4 sentences unless asked for more.
Never break character."""

# Full system prompt includes tool instructions
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + "\n\n" + TOOLS_DESCRIPTION


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health_check():
    """Check if API and Ollama are both running."""
    try:
        http_requests.get("http://localhost:11434", timeout=3)
        ollama_status = "ok"
    except http_requests.exceptions.ConnectionError:
        ollama_status = "unreachable"

    return {
        "status": "ok",
        "api": "running",
        "ollama": ollama_status
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat route — full pipeline:
    1. Retrieve relevant lore via RAG
    2. Build prompt with context + history + tools
    3. Run agent loop (handles tool calls automatically)
    4. Return final narrative to player
    """

    messages_as_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    try:
        # Step 1: Get latest message for retrieval
        latest_message = messages_as_dicts[-1]["content"]

        # Step 2: Retrieve relevant lore context
        context = retrieve_context(
            query=latest_message,
            messages=messages_as_dicts
        )

        # Step 3: Build the complete prompt
        prompt = build_rag_prompt(
            system_prompt=SYSTEM_PROMPT,
            context=context,
            messages=messages_as_dicts
        )

        # Step 4: Run the agent loop
        # This handles tool calls automatically before returning
        response = run_agent(prompt)

        return ChatResponse(response=response)

    except http_requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot reach Ollama. Is it running?"
        )

    except Exception as e:
        print(f"Error in /chat route: {e}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Check backend logs."
        )