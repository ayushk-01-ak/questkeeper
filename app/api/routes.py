# app/api/routes.py
from app.core.npcs import detect_npc, get_personality_prompt, ALDRIC_PERSONALITY
from app.core.agent import run_agent, TOOLS_DESCRIPTION
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests as http_requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.rag.pipeline import retrieve_context, build_rag_prompt
from app.db.database import initialize_database
from app.db.memory import (
    create_session,
    save_message,
    get_recent_messages,
    get_all_summaries
)
from app.memory.summarizer import summarize_session

initialize_database()

app = FastAPI(title="QuestKeeper API", version="1.0")

BASE_SYSTEM_PROMPT = """You are Aldric, a wise and dramatic Dungeon Master.
You speak in an atmospheric, immersive tone.
You remember everything the player tells you.
Keep responses under 4 sentences unless asked for more.
Never break character.
The player is ALIVE unless deal_damage tool confirms HP reached 0."""

SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + "\n\n" + TOOLS_DESCRIPTION


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    character_id: int
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    session_id: int


class SessionRequest(BaseModel):
    character_id: int


class SummarizeRequest(BaseModel):
    session_id: int


@app.get("/health")
def health_check():
    try:
        http_requests.get("http://localhost:11434", timeout=3)
        ollama_status = "ok"
    except http_requests.exceptions.ConnectionError:
        ollama_status = "unreachable"
    return {"status": "ok", "api": "running", "ollama": ollama_status}


@app.post("/session/start")
def start_session(request: SessionRequest):
    session_id = create_session(request.character_id)
    return {"session_id": session_id, "message": f"Session {session_id} started"}


@app.post("/session/end")
def end_session(request: SummarizeRequest):
    summary = summarize_session(request.session_id)
    return {"session_id": request.session_id, "summary": summary}


@app.get("/memory/{character_id}")
def get_memory(character_id: int):
    summaries = get_all_summaries(character_id)
    recent = get_recent_messages(character_id, limit=20)
    return {
        "character_id": character_id,
        "past_summaries": summaries,
        "recent_messages": recent
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    messages_as_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    session_id = request.session_id
    if session_id is None:
        session_id = create_session(request.character_id)

    try:
        latest_message = messages_as_dicts[-1]["content"]

        # Long-term memory
        past_summaries = get_all_summaries(request.character_id)
        memory_context = ""
        if past_summaries:
            memory_context = "CAMPAIGN HISTORY (past sessions):\n"
            for entry in past_summaries:
                memory_context += f"- {entry['summary']}\n"
            memory_context += "\n"

        # RAG retrieval
        lore_context = retrieve_context(
            query=latest_message,
            messages=messages_as_dicts
        )

        combined_context = memory_context + lore_context

        # --- NPC Detection ---
        # Check if player is addressing a specific NPC
        npc_key = detect_npc(latest_message)

        # Get the right personality for this message
        personality = get_personality_prompt(npc_key)

        if npc_key:
            # NPC speaking — no tool descriptions needed
            # NPCs don't roll dice or check inventory
            system_prompt = personality
            print(f"[NPC] Switching to: {npc_key}")
        else:
            # Aldric narrating — include tools
            system_prompt = personality + "\n\n" + TOOLS_DESCRIPTION

        # --- Build prompt with dynamic personality ---
        prompt = build_rag_prompt(
            system_prompt=system_prompt,
            context=combined_context,
            messages=messages_as_dicts
        )

        # --- Run agent ---
        # Only pass player_message for tool detection when Aldric is speaking
        # NPCs don't use tools
        if npc_key:
            response = run_agent(prompt, player_message="")
        else:
            response = run_agent(prompt, player_message=latest_message)

        # Save both messages
        save_message(
            session_id=session_id,
            character_id=request.character_id,
            role="user",
            content=latest_message
        )
        save_message(
            session_id=session_id,
            character_id=request.character_id,
            role="assistant",
            content=response
        )

        return ChatResponse(response=response, session_id=session_id)

    except http_requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot reach Ollama.")
    except Exception as e:
        print(f"Error in /chat route: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong.")