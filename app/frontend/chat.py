# app/frontend/chat.py
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.llm import ask_llm_with_history  # Updated import


# --- Page Configuration ---
st.set_page_config(
    page_title="QuestKeeper",
    page_icon="🎲",
    layout="centered"
)

st.title("🎲 QuestKeeper")
st.caption("Your local AI Dungeon Master")
st.divider()


# --- DM Personality ---
# This defines who Aldric is in every single request
# It never changes during a conversation
SYSTEM_PROMPT = """You are Aldric, a wise and dramatic Dungeon Master.
You speak in an atmospheric, immersive tone.
You remember everything the player tells you.
Keep responses under 4 sentences unless asked for more.
Never break character."""


# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# --- Chat Input ---
user_input = st.chat_input("Speak, adventurer...")

if user_input:

    # 1. Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 2. Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # 3. Send FULL history to LLM
    # This is the key change — we pass all messages, not just the latest
    with st.spinner("Aldric is thinking..."):
        response = ask_llm_with_history(
            messages=st.session_state.messages,
            system_prompt=SYSTEM_PROMPT
        )

    # 4. Add response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # 5. Display response
    with st.chat_message("assistant"):
        st.write(response)