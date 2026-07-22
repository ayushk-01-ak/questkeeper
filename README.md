# QuestKeeper 🎲⚡

A local AI-powered Dungeon Master and game companion — runs completely
offline using Ollama and a local LLM. No internet after setup. No API
costs. No data leaving your machine.

Includes a **Wuthering Waves themed mode** — a custom "Resonance Oracle"
companion (Luminae) that gives real gameplay advice — builds, Echo farming,
combat strategy, lore — wrapped in full in-world immersion.

![CI](https://github.com/ayushk-01-ak/questkeeper/actions/workflows/ci.yml/badge.svg)

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
| Phase 7 | Tool Calling | ✅ Complete |
| Phase 8 | Conversation Memory | ✅ Complete |
| Phase 9 | NPC Personalities | ✅ Complete |
| Phase 10 | Docker | ✅ Complete |
| Phase 11 | CI/CD with GitHub Actions | ✅ Complete |
| Bonus | Wuthering Waves Companion Mode | ✅ Complete |

---

## What QuestKeeper Can Do

- 🎲 **Roll real dice** — attacks, skill checks, saving throws
- 🗡️ **Track HP** — damage updates your character permanently
- 🎒 **Manage inventory** — items stored in a real database
- 📜 **Remember your campaign** — sessions summarized and recalled
- 📖 **Read your custom lore** — RAG pipeline from your own PDFs
- 🧙 **Distinct NPC voices** — every character sounds different
- ⚡ **Real gameplay companion mode** — Luminae gives actual Wuthering
  Waves builds, Echo advice, and combat strategy, fully in character
- 🔒 **Fully offline** — Llama 3.2 3B runs locally via Ollama

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| LLM | Ollama + Llama 3.2 3B | Local language model |
| Backend | FastAPI + Uvicorn | API server |
| Frontend | Streamlit (custom CSS) | Premium chat interface |
| Database | SQLite | Characters, inventory, memory |
| Vector DB | ChromaDB | RAG retrieval |
| Embeddings | sentence-transformers | Text to vectors |
| Container | Docker + Compose | Reproducible setup |
| CI/CD | GitHub Actions | Automated testing |

---

## Architecture

Streamlit Frontend (port 8501)
↓
FastAPI Backend (port 8000)
↓ ↓ ↓
Ollama LLM SQLite DB ChromaDB
(port 11434) (characters) (lore vectors)
↑
RAG Pipeline
(PDF → chunks → embeddings → retrieval)


---

## Quick Start (Docker)

```bash
ollama serve
ollama pull llama3.2:3b
git clone https://github.com/ayushk-01-ak/questkeeper.git
cd questkeeper
docker compose up --build
```

Open `http://localhost:8501`

---

## Manual Setup

```bash
git clone https://github.com/ayushk-01-ak/questkeeper.git
cd questkeeper
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3.2:3b
python -m app.db.database

# Terminal 1
ollama serve

# Terminal 2
uvicorn app.api.routes:app --reload --port 8000

# Terminal 3
streamlit run app/frontend/chat.py
```

Open `http://localhost:8501`

---

questkeeper/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .streamlit/
│   └── config.toml
├── app/
│   ├── core/
│   │   ├── llm.py
│   │   ├── tools.py
│   │   ├── agent.py
│   │   └── npcs.py
│   ├── api/
│   │   └── routes.py
│   ├── frontend/
│   │   └── chat.py
│   ├── db/
│   │   ├── database.py
│   │   ├── characters.py
│   │   ├── inventory.py
│   │   └── memory.py
│   ├── rag/
│   │   ├── loader.py
│   │   ├── embedder.py
│   │   └── pipeline.py
│   └── memory/
│       └── summarizer.py
├── data/
├── tests/
│   └── test_tools.py
├── docs/
│   └── notes.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── .dockerignore
└── README.md

## How It Works

**RAG Pipeline**

PDF → chunks → embeddings → ChromaDB
Player question → vector search → relevant chunks → LLM → grounded answer


**Tool Calling**

"I attack the goblin" → code detects intent → roll_dice(20) → real result
→ LLM narrates using that real number


**Memory System**

Every message saved to SQLite
Session ends → LLM summarizes → saved
Next session → summaries + recent messages loaded → full continuity


**NPC / Persona Detection**

Message mentions a character/topic → matching personality profile loaded
→ LLM responds fully in that voice, whether narrating or giving real advice


---

## Running Tests

```bash
pytest tests/ -v
```

---

## Built As A Learning Project

QuestKeeper was built phase by phase, covering Python, FastAPI, Streamlit,
SQLite, ChromaDB, RAG pipelines, tool calling, conversation memory, NPC
design, custom UI theming, Docker, and CI/CD — with every component
understood, not just copied.

---

## License

MIT License — use, modify, share freely.