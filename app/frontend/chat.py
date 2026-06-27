# app/frontend/chat.py
# Streamlit frontend that talks to our FastAPI backend
# Notice: no LLM imports here anymore
# The frontend only knows about the API, not about Ollama

import streamlit as st
import requests  # For calling our FastAPI backend

# The URL of our FastAPI backend
# This is OUR server, not Ollama
API_URL = "http://localhost:8000"


# --- Page Configuration ---
st.set_page_config(
    page_title="QuestKeeper",
    page_icon="🎲",
    layout="centered"
)

st.title("🎲 QuestKeeper")
st.caption("Your local AI Dungeon Master")


# --- Check Backend Health ---
# Before showing the chat, verify the backend is running
# If it's not, show a clear error instead of a confusing crash
try:
    health = requests.get(f"{API_URL}/health", timeout=3)
    if health.status_code == 200:
        st.success("✅ Connected to QuestKeeper backend")
    else:
        st.error("❌ Backend returned an error")
except requests.exceptions.ConnectionError:
    # This error means the backend server isn't running
    st.error("❌ Cannot connect to backend. Is FastAPI running?")
    st.code("uvicorn app.api.routes:app --reload --port 8000")
    st.stop()  # Stop rendering the rest of the page

st.divider()


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

    # 2. Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)

    # 3. Send full history to FastAPI backend
    # Notice: we send to OUR backend now, not to Ollama directly
    with st.spinner("Aldric is thinking..."):
        try:
            api_response = requests.post(
                f"{API_URL}/chat",
                json={"messages": st.session_state.messages},
                timeout=60  # LLM can take time, wait up to 60 seconds
            )

            if api_response.status_code == 200:
                # Extract the response text from JSON
                response_data = api_response.json()
                response = response_data["response"]

            else:
                # Backend returned an error we didn't expect
                response = f"Backend error: {api_response.status_code}"

        except requests.exceptions.Timeout:
            # LLM took too long to respond
            response = "Aldric is taking too long to respond. Try again."

        except requests.exceptions.ConnectionError:
            # Backend went down mid-session
            response = "Lost connection to backend. Is FastAPI still running?"

    # 4. Add response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # 5. Display response
    with st.chat_message("assistant"):
        st.write(response)