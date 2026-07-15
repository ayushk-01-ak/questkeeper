# app/frontend/chat.py
# Streamlit frontend with full memory support
# Tracks sessions, saves history, loads past context

import streamlit as st
import requests

import os
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="QuestKeeper",
    page_icon="🎲",
    layout="centered"
)

st.title("🎲 QuestKeeper")
st.caption("Your local AI Dungeon Master")

# --- Backend Health Check ---
try:
    health = requests.get(f"{API_URL}/health", timeout=3)
    if health.status_code == 200:
        data = health.json()
        if data["ollama"] == "ok":
            st.success("✅ Connected — Ollama running")
        else:
            st.warning("⚠️ Backend running but Ollama unreachable")
except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to backend. Is FastAPI running?")
    st.code("uvicorn app.api.routes:app --reload --port 8000")
    st.stop()

st.divider()

# --- Character Selection ---
# For now we hardcode character_id=1 (Arjun from testing)
# Phase 9 will add a proper character selection screen
CHARACTER_ID = 1

# --- Session State Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_started" not in st.session_state:
    st.session_state.session_started = False


# --- Start Session ---
if not st.session_state.session_started:

    # Load past memory for this character
    memory_response = requests.get(f"{API_URL}/memory/{CHARACTER_ID}")

    if memory_response.status_code == 200:
        memory_data = memory_response.json()
        past_summaries = memory_data.get("past_summaries", [])
        recent_messages = memory_data.get("recent_messages", [])

        if past_summaries:
            st.info(f"📜 {len(past_summaries)} past session(s) remembered")

        # Load recent messages into session state
        # So the chat history shows previous conversation
        if recent_messages:
            st.session_state.messages = recent_messages
            st.info(f"💬 Loaded {len(recent_messages)} recent messages")

    # Start a new session on the backend
    session_response = requests.post(
        f"{API_URL}/session/start",
        json={"character_id": CHARACTER_ID}
    )

    if session_response.status_code == 200:
        st.session_state.session_id = session_response.json()["session_id"]
        st.session_state.session_started = True


# --- Sidebar: Session Controls ---
with st.sidebar:
    st.header("Campaign Controls")
    st.write(f"Character ID: {CHARACTER_ID}")
    st.write(f"Session ID: {st.session_state.session_id}")

    # End session button — triggers summarization
    if st.button("⚔️ End Session & Save"):
        if st.session_state.session_id:
            with st.spinner("Summarizing session..."):
                end_response = requests.post(
                    f"{API_URL}/session/end",
                    json={"session_id": st.session_state.session_id}
                )

            if end_response.status_code == 200:
                summary = end_response.json()["summary"]
                st.success("Session saved!")
                st.write("**Summary:**")
                st.write(summary)

                # Reset for next session
                st.session_state.session_started = False
                st.session_state.messages = []
                st.session_state.session_id = None
            else:
                st.error("Failed to save session")

    st.divider()
    st.caption("Session history is saved automatically after each message.")


# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# --- Chat Input ---
user_input = st.chat_input("Speak, adventurer...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    with st.spinner("Aldric is thinking..."):
        try:
            api_response = requests.post(
                f"{API_URL}/chat",
                json={
                    "messages": st.session_state.messages,
                    "character_id": CHARACTER_ID,
                    "session_id": st.session_state.session_id
                },
                timeout=60
            )

            if api_response.status_code == 200:
                data = api_response.json()
                response = data["response"]

                # Update session_id in case backend created one
                st.session_state.session_id = data["session_id"]

            elif api_response.status_code == 503:
                response = "⚠️ The oracle is silent. Ollama appears offline."
            else:
                detail = api_response.json().get("detail", "Unknown error")
                response = f"⚠️ Error: {detail}"

        except requests.exceptions.Timeout:
            response = "⚠️ Aldric ponders too long. Try again."
        except requests.exceptions.ConnectionError:
            response = "⚠️ Lost connection to backend."

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.write(response)