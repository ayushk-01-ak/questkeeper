# QuestKeeper 🎲

A local AI-powered Dungeon Master and NPC companion.
Runs completely offline using Ollama and a local LLM.

---

## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Environment Setup | ✅ Complete |
| Phase 1 | Local LLM with Ollama | ✅ Complete |
| Phase 2 | Streamlit Chat UI | ✅ Complete |
| Phase 3 | FastAPI Backend | ✅ Complete |
| Phase 4 | Connect FastAPI to Ollama | ✅ Complete |
| Phase 5 | SQLite Database | ✅ Complete |
| Phase 6 | RAG Pipeline | ✅ Complete |
| Phase 7 | Tool Calling | 🚧 In Progress |
| Phase 8 | Conversation Memory | ⏳ Upcoming |
| Phase 9 | NPC Personalities | ⏳ Upcoming |
| Phase 10 | Docker | ⏳ Upcoming |
| Phase 11 | CI/CD | ⏳ Upcoming |

---

## Tech Stack

- **Python 3.11**
- **Ollama** — runs Llama 3.2 3B locally
- **FastAPI** — backend API server
- **Streamlit** — chat frontend
- **SQLite** — character and inventory storage
- **ChromaDB** — vector database for RAG (Phase 6)

---

## Architecture
Streamlit (frontend)

↓

FastAPI (backend) ← SQLite (characters, inventory)

↓

Ollama (local LLM)

---

## Setup Instructions

1. Clone this repository
2. Install Python 3.11
3. Create virtual environment: `py -3.11 -m venv venv`
4. Activate it: `venv\Scripts\activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Install and start Ollama: https://ollama.com
7. Pull the model: `ollama pull llama3.2:3b`
8. Initialize database: `python -m app.db.database`

## Running The App

Terminal 1 — Backend:
uvicorn app.api.routes:app --reload --port 8000

Terminal 2 — Frontend:
streamlit run app/frontend/chat.py

---

## Project Structure
questkeeper/

├── app/

│   ├── core/

│   │   └── llm.py          # LLM communication

│   ├── api/

│   │   └── routes.py       # FastAPI routes

│   ├── frontend/

│   │   └── chat.py         # Streamlit UI

│   ├── db/

│   │   ├── database.py     # Connection and initialization

│   │   ├── characters.py   # Character CRUD

│   │   └── inventory.py    # Inventory CRUD

│   ├── rag/                # Phase 6

│   └── memory/             # Phase 8

├── data/                   # PDFs and game content

├── docs/                   # Notes and documentation

├── requirements.txt

├── .gitignore

└── README.md