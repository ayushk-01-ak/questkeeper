
from app.rag.pipeline import retrieve_context, build_rag_prompt
from app.core.llm import ask_llm


# Replace the existing chat() function with this
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat route now enhanced with RAG.
    Every player message triggers a context retrieval
    before being sent to the LLM.
    """
    import requests as http_requests

    messages_as_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    try:
        # Get the latest player message for retrieval
        latest_message = messages_as_dicts[-1]["content"]

        # Step 1: Retrieve relevant lore context
        context = retrieve_context(latest_message)

        # Step 2: Build the RAG-enhanced prompt
        prompt = build_rag_prompt(
            system_prompt=SYSTEM_PROMPT,
            context=context,
            messages=messages_as_dicts
        )

        # Step 3: Send to LLM directly (not ask_llm_with_history
        # because we already built the full prompt ourselves)
        response = ask_llm(prompt)

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
        )# app/api/routes.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests as http_requests  # renamed to avoid clash with fastapi
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.llm import ask_llm_with_history

app = FastAPI(title="QuestKeeper API", version="1.0")

SYSTEM_PROMPT = """You are Aldric, a wise and good professional Dungeon Master.
You speak in an atmospheric, immersive tone.
You remember everything the player tells you.
Keep responses under 4 sentences unless asked for more.
Never break character."""


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health_check():
    """
    Check if our API is running.
    Also checks if Ollama is reachable.
    """
    try:
        # Try to reach Ollama's server directly
        ollama_response = http_requests.get(
            "http://localhost:11434",
            timeout=3
        )
        ollama_status = "ok"
    except http_requests.exceptions.ConnectionError:
        # Ollama isn't running
        ollama_status = "unreachable"

    return {
        "status": "ok",
        "api": "running",
        "ollama": ollama_status
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat route with proper error handling.
    """

    # Convert Pydantic models to plain dicts
    messages_as_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    try:
        # Attempt to get LLM response
        response = ask_llm_with_history(
            messages=messages_as_dicts,
            system_prompt=SYSTEM_PROMPT
        )
        return ChatResponse(response=response)

    except http_requests.exceptions.ConnectionError:
        # Ollama server is not running or crashed
        # 503 = Service Unavailable (more honest than 500)
        raise HTTPException(
            status_code=503,
            detail="Cannot reach Ollama. Is it running?"
        )

    except http_requests.exceptions.Timeout:
        # Ollama is running but taking too long
        raise HTTPException(
            status_code=504,
            detail="Ollama took too long to respond. Try again."
        )

    except Exception as e:
        # Catch any other unexpected errors
        # We log it and return a safe message
        print(f"Unexpected error in /chat route: {e}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Check the backend logs."
        )