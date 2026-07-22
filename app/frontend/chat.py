# app/frontend/chat.py
# Wuthering Waves — Resonance Oracle
# Premium frontend with full custom styling

import streamlit as st
import requests
import os
import html as html_lib

API_URL = os.getenv("API_URL", "http://localhost:8000")
CHARACTER_ID = 1

# ─────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Wuthering Waves — Resonance Oracle",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",  # FIX: sidebar now visible by default
    # so the Save & Exit button is reachable without a hidden toggle
)

# ─────────────────────────────────────────────
# CSS INJECTION
# ─────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

/* ══════════════════════════════════════
   HIDE ALL STREAMLIT CHROME
══════════════════════════════════════ */
#MainMenu                                { visibility: hidden !important; }
.stDeployButton                          { display: none !important; }
footer                                   { visibility: hidden !important; }
header[data-testid="stHeader"]          { display: none !important; }
[data-testid="stToolbar"]               { display: none !important; }
.viewerBadge_container__r5tak          { display: none !important; }
#stDecoration                            { display: none !important; }
[data-testid="stStatusWidget"]          { display: none !important; }
button[kind="header"]                   { display: none !important; }

/* FIX: keep the sidebar toggle arrow but restyle it to match the theme
   instead of hiding it — this is the ONLY way to reach the sidebar
   (and the Save & Exit button) if the user collapses it */
[data-testid="collapsedControl"] {
    background: #0c1420 !important;
    border: 1px solid #4dc8e030 !important;
    border-radius: 8px !important;
    color: #4dc8e0 !important;
    top: 14px !important;
}

/* ══════════════════════════════════════
   BASE RESET
══════════════════════════════════════ */
* { box-sizing: border-box; }

.stApp {
    background: #070b12 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ══════════════════════════════════════
   HEADER BAR
══════════════════════════════════════ */
.ww-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 13px 32px;
    background: linear-gradient(90deg,
        #060910 0%,
        #0a1020 40%,
        #0a1020 60%,
        #060910 100%
    );
    border-bottom: 1px solid #162030;
    position: sticky;
    top: 0;
    z-index: 200;
}

.ww-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.ww-logo {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: linear-gradient(135deg, #1a3a4a, #0d2535);
    border: 1px solid #4dc8e050;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 0 18px rgba(77,200,224,0.25),
                inset 0 1px 0 rgba(255,255,255,0.05);
}

.ww-name {
    font-family: 'Cinzel', serif;
    font-size: 16px;
    font-weight: 700;
    color: #d8e8f0;
    letter-spacing: 3px;
    line-height: 1.2;
}

.ww-tagline {
    font-size: 10px;
    color: #4dc8e0;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    font-weight: 500;
    margin-top: 2px;
}

.ww-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #04120a;
    border: 1px solid #0a2a14;
    border-radius: 20px;
    padding: 5px 16px;
    font-size: 11.5px;
    color: #4ade80;
    font-weight: 500;
    letter-spacing: 0.5px;
}

.ww-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 8px rgba(74,222,128,0.8);
    animation: resonancePulse 2.8s ease-in-out infinite;
}

@keyframes resonancePulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(74,222,128,0.8); }
    50%       { opacity: 0.4; box-shadow: 0 0 2px rgba(74,222,128,0.2); }
}

/* ══════════════════════════════════════
   CHAT AREA
══════════════════════════════════════ */
.chat-area {
    padding: 28px 0 12px;
}

/* ── AI Message ── */
.msg-row-ai {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 8px 32px;
    max-width: 860px;
    margin: 0 auto;
}

.ai-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: radial-gradient(circle at 40% 35%, #1a3545, #0a1e2e);
    border: 1.5px solid #4dc8e045;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    margin-top: 22px;
    box-shadow:
        0 0 16px rgba(77,200,224,0.18),
        inset 0 1px 0 rgba(77,200,224,0.1);
    animation: avatarGlow 3.5s ease-in-out infinite;
}

@keyframes avatarGlow {
    0%, 100% { box-shadow: 0 0 16px rgba(77,200,224,0.18), inset 0 1px 0 rgba(77,200,224,0.1); }
    50%       { box-shadow: 0 0 28px rgba(77,200,224,0.32), inset 0 1px 0 rgba(77,200,224,0.15); }
}

.ai-body { flex: 1; min-width: 0; }

.msg-label-ai {
    font-size: 9.5px;
    font-weight: 600;
    letter-spacing: 2.5px;
    color: #4dc8e0;
    text-transform: uppercase;
    margin-bottom: 8px;
    opacity: 0.85;
}

.msg-bubble-ai {
    background: linear-gradient(145deg, #0b1828 0%, #09131f 100%);
    border: 1px solid #1c3348;
    border-left: 3px solid #4dc8e0;
    border-radius: 2px 16px 16px 16px;
    padding: 16px 20px;
    color: #c0cede;
    font-size: 14.5px;
    line-height: 1.78;
    box-shadow:
        0 4px 28px rgba(77,200,224,0.05),
        inset 0 1px 0 rgba(255,255,255,0.03);
    word-wrap: break-word;
}

/* ── User Message ── */
.msg-row-user {
    display: flex;
    align-items: flex-start;
    justify-content: flex-end;
    gap: 14px;
    padding: 8px 32px;
    max-width: 860px;
    margin: 0 auto;
}

.user-body {
    max-width: 62%;
    min-width: 0;
}

.msg-label-user {
    font-size: 9.5px;
    font-weight: 600;
    letter-spacing: 2.5px;
    color: #e8b84b;
    text-transform: uppercase;
    margin-bottom: 8px;
    text-align: right;
    opacity: 0.85;
}

.msg-bubble-user {
    background: linear-gradient(145deg, #18223c 0%, #141e36 100%);
    border: 1px solid #2a3a5a;
    border-right: 3px solid #e8b84b;
    border-radius: 16px 2px 16px 16px;
    padding: 16px 20px;
    color: #d8e0f0;
    font-size: 14.5px;
    line-height: 1.78;
    box-shadow:
        0 4px 28px rgba(232,184,75,0.05),
        inset 0 1px 0 rgba(255,255,255,0.03);
    word-wrap: break-word;
}

.user-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: radial-gradient(circle at 40% 35%, #2a1e0a, #1a1408);
    border: 1.5px solid #e8b84b40;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    margin-top: 22px;
    box-shadow: 0 0 14px rgba(232,184,75,0.12);
}

/* Message spacing */
.msg-gap { height: 6px; }

/* ══════════════════════════════════════
   INPUT BAR
══════════════════════════════════════ */
.input-wrapper {
    position: sticky;
    bottom: 0;
    background: linear-gradient(180deg,
        rgba(7,11,18,0) 0%,
        rgba(7,11,18,0.95) 28%,
        #070b12 60%
    );
    padding: 20px 32px 28px;
    max-width: 860px;
    margin: 0 auto;
}

[data-testid="stChatInput"] > div {
    background: #0d1828 !important;
    border: 1px solid #1e3048 !important;
    border-radius: 14px !important;
    box-shadow: 0 0 0 0 rgba(77,200,224,0) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

[data-testid="stChatInput"] > div:focus-within {
    border-color: #4dc8e050 !important;
    box-shadow: 0 0 0 3px rgba(77,200,224,0.08) !important;
}

[data-testid="stChatInput"] textarea {
    color: #d8e4f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    background: transparent !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #2a3a50 !important;
}

/* Send button */
[data-testid="stChatInput"] button {
    color: #4dc8e0 !important;
}

/* ══════════════════════════════════════
   SIDEBAR
══════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #060910 !important;
    border-right: 1px solid #162030 !important;
    min-width: 260px !important;
}

[data-testid="stSidebar"] > div {
    padding: 24px 20px !important;
}

.sb-title {
    font-family: 'Cinzel', serif;
    font-size: 11px;
    font-weight: 600;
    color: #4dc8e0;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid #162030;
}

.sb-card {
    background: #0c1420;
    border: 1px solid #162030;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
}

.sb-card-label {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #4dc8e055;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.sb-card-value {
    font-size: 13.5px;
    color: #7890a8;
    font-weight: 500;
}

.sb-divider {
    height: 1px;
    background: #162030;
    margin: 18px 0;
}

.sb-note {
    font-size: 10.5px;
    color: #2a3a50;
    text-align: center;
    line-height: 1.6;
    margin-top: 14px;
}

/* Sidebar button */
.stButton > button {
    background: #0c1828 !important;
    border: 1px solid #4dc8e025 !important;
    color: #4dc8e0 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    letter-spacing: 0.8px !important;
    padding: 10px 16px !important;
    width: 100% !important;
    transition: all 0.22s ease !important;
}

.stButton > button:hover {
    background: #0f2038 !important;
    border-color: #4dc8e055 !important;
    box-shadow: 0 0 20px rgba(77,200,224,0.12) !important;
}

/* ══════════════════════════════════════
   ALERTS
══════════════════════════════════════ */
[data-testid="stSuccess"] {
    background: #04120a !important;
    border: 1px solid #082818 !important;
    color: #4ade80 !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
}

[data-testid="stError"],
div[data-baseweb="notification"][kind="negative"] {
    background: #120608 !important;
    border: 1px solid #2a0810 !important;
    border-radius: 10px !important;
}

[data-testid="stWarning"] {
    background: #12100a !important;
    border: 1px solid #2a2010 !important;
    border-radius: 10px !important;
}

/* ══════════════════════════════════════
   INFO BOX (session loaded etc)
══════════════════════════════════════ */
[data-testid="stInfo"] {
    background: #08121e !important;
    border: 1px solid #162030 !important;
    color: #4dc8e0 !important;
    border-radius: 10px !important;
    font-size: 12px !important;
}

/* ══════════════════════════════════════
   SPINNER
══════════════════════════════════════ */
.stSpinner > div {
    border-top-color: #4dc8e0 !important;
}

/* ══════════════════════════════════════
   MISC CLEANUP
══════════════════════════════════════ */
div[data-testid="stMarkdownContainer"] > p { margin: 0; }
.element-container { margin-bottom: 0 !important; }
section[data-testid="stSidebar"] + div { margin-left: 0 !important; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MESSAGE RENDER HELPERS
# ─────────────────────────────────────────────


def render_ai_message(content: str):
    """Render an AI (Luminae) message with teal styling."""
    safe = html_lib.escape(content).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="msg-row-ai">
            <div class="ai-avatar">⚡</div>
            <div class="ai-body">
                <div class="msg-label-ai">Luminae · Resonance Oracle</div>
                <div class="msg-bubble-ai">{safe}</div>
            </div>
        </div>
        <div class="msg-gap"></div>
        """,
        unsafe_allow_html=True,
    )


def render_user_message(content: str):
    """Render a user (Rover) message with amber styling."""
    safe = html_lib.escape(content).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="msg-row-user">
            <div class="user-body">
                <div class="msg-label-user">Rover</div>
                <div class="msg-bubble-user">{safe}</div>
            </div>
            <div class="user-avatar">⚔️</div>
        </div>
        <div class="msg-gap"></div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown(
    """
    <div class="ww-header">
        <div class="ww-brand">
            <div class="ww-logo">⚡</div>
            <div>
                <div class="ww-name">WUTHERING WAVES</div>
                <div class="ww-tagline">Resonance Oracle</div>
            </div>
        </div>
        <div class="ww-status">
            <div class="ww-status-dot"></div>
            Resonance Active
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# BACKEND HEALTH CHECK
# ─────────────────────────────────────────────

try:
    health = requests.get(f"{API_URL}/health", timeout=3)
    if health.status_code == 200:
        data = health.json()
        if data.get("ollama") != "ok":
            st.warning("⚠️ Resonance link unstable — Ollama unreachable.")
except requests.exceptions.ConnectionError:
    st.error("❌ Cannot reach backend. Start FastAPI first.")
    st.code("uvicorn app.api.routes:app --reload --port 8000")
    st.stop()

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_started" not in st.session_state:
    st.session_state.session_started = False

# ─────────────────────────────────────────────
# START / LOAD SESSION
# ─────────────────────────────────────────────

if not st.session_state.session_started:
    memory_resp = requests.get(f"{API_URL}/memory/{CHARACTER_ID}")

    if memory_resp.status_code == 200:
        mem = memory_resp.json()
        past = mem.get("past_summaries", [])
        recent = mem.get("recent_messages", [])

        if past:
            st.info(f"📜 {len(past)} past session(s) loaded into resonance memory.")

        if recent:
            st.session_state.messages = recent
            st.info(f"💬 {len(recent)} recent exchanges restored.")

    sess_resp = requests.post(
        f"{API_URL}/session/start",
        json={"character_id": CHARACTER_ID},
    )

    if sess_resp.status_code == 200:
        st.session_state.session_id = sess_resp.json()["session_id"]
        st.session_state.session_started = True

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sb-title">Resonance Log</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="sb-card">
            <div class="sb-card-label">Resonator</div>
            <div class="sb-card-value">Rover</div>
        </div>
        <div class="sb-card">
            <div class="sb-card-label">Session ID</div>
            <div class="sb-card-value">#{st.session_state.session_id or "—"}</div>
        </div>
        <div class="sb-card">
            <div class="sb-card-label">Messages This Session</div>
            <div class="sb-card-value">{len(st.session_state.messages)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    if st.button("⚡ Close Resonance Link"):
        if st.session_state.session_id:
            with st.spinner("Compressing resonance data..."):
                end_resp = requests.post(
                    f"{API_URL}/session/end",
                    json={"session_id": st.session_state.session_id},
                )

            if end_resp.status_code == 200:
                summary = end_resp.json()["summary"]
                st.success("Session sealed and saved.")
                st.markdown(
                    f'<div class="sb-card" style="border-color:#4dc8e030">'
                    f'<div class="sb-card-label">Session Summary</div>'
                    f'<div class="sb-card-value" style="font-size:12px;line-height:1.6">'
                    f"{html_lib.escape(summary)}</div></div>",
                    unsafe_allow_html=True,
                )
                st.session_state.session_started = False
                st.session_state.messages = []
                st.session_state.session_id = None
            else:
                st.error("Failed to seal session.")

    st.markdown(
        '<div class="sb-note">All resonance data is sealed automatically after each exchange.</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────

st.markdown('<div class="chat-area">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        render_ai_message(msg["content"])

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────

user_input = st.chat_input("Speak, Rover...")

if user_input:
    # Add to history and render immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_user_message(user_input)

    with st.spinner("Resonance Oracle is channelling..."):
        try:
            resp = requests.post(
                f"{API_URL}/chat",
                json={
                    "messages": st.session_state.messages,
                    "character_id": CHARACTER_ID,
                    "session_id": st.session_state.session_id,
                },
                timeout=60,
            )

            if resp.status_code == 200:
                data = resp.json()
                response = data["response"]
                st.session_state.session_id = data["session_id"]

            elif resp.status_code == 503:
                response = (
                    "The resonance link has faltered. "
                    "The Oracle cannot be reached — Ollama appears offline."
                )
            else:
                detail = resp.json().get("detail", "Unknown disturbance.")
                response = f"Resonance disrupted: {detail}"

        except requests.exceptions.Timeout:
            response = (
                "The Oracle falls silent... the resonance took too long. Try again."
            )
        except requests.exceptions.ConnectionError:
            response = "Resonance link severed. Is the backend still running?"

    # Add to history and render
    st.session_state.messages.append({"role": "assistant", "content": response})
    render_ai_message(response)
