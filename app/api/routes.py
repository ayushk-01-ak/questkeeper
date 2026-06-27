# app/api/routes.py
# This is our FastAPI backend server
# It receives requests from the frontend and talks to the LLM

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import sys
import os

# Add project root to path so we can import from app/core
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.llm import ask_llm_with_history

# Create the FastAPI application
# Think of this as creating the restaurant
app = FastAPI(title="QuestKeeper API", version="1.0")

# The DM personality stays here in the backend now
# Frontend doesn't need to know about this anymore
SYSTEM_PROMPT = """You are Aldric, a wise and dramatic Dungeon Master.
You speak in an atmospheric, immersive tone.
You remember everything the player tells you.
Keep responses under 4 sentences unless asked for more.
Never break character."""


# --- Data Models ---
# Pydantic models define the exact shape of data we expect
# FastAPI uses these to validate incoming requests automatically
# If the request doesn't match this shape, FastAPI rejects it with a clear error

class Message(BaseModel):
    # A single chat message has exactly two fields
    role: str      # either "user" or "assistant"
    content: str   # the actual text


class ChatRequest(BaseModel):
    # A chat request contains a list of messages
    messages: List[Message]


class ChatResponse(BaseModel):
    # Our response back to the frontend
    response: str


# --- Routes ---

@app.get("/health")
def health_check():
    """
    Simple route to verify the server is running.
    Frontend can call this to check if backend is alive.
    """
    return {"status": "ok", "message": "QuestKeeper API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat route.
    Receives conversation history, returns DM response.
    """

    # Convert Pydantic Message objects to plain dictionaries
    # ask_llm_with_history expects a list of dicts
    messages_as_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    # Call our LLM function with the full history
    response = ask_llm_with_history(
        messages=messages_as_dicts,
        system_prompt=SYSTEM_PROMPT
    )

    # Return the response wrapped in our ChatResponse model
    return ChatResponse(response=response)
