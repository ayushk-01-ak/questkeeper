from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests as http_requests
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.rag.pipeline import retrieve_context, build_rag_prompt
from app.core.llm import ask_llm

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
    try:
        ollama_response = http_requests.get("http://localhost:11434", timeout=3)
        ollama_status = "ok"
    except:
        ollama_status = "unreachable"

    return {
        "status": "ok",
        "api": "running",
        "ollama": ollama_status
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat endpoint with RAG support."""
    
    messages_as_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    try:
        # Get latest player message for retrieval
        latest_message = messages_as_dicts[-1]["content"]

        # Retrieve relevant context using full history
        context = retrieve_context(
            query=latest_message,
            messages=messages_as_dicts
        )

        # Build enhanced prompt with RAG context
        prompt = build_rag_prompt(
            system_prompt=SYSTEM_PROMPT,
            context=context,
            messages=messages_as_dicts
        )

        # Get response from LLM
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
        )