# QuestKeeper 🎲

A local AI-powered Dungeon Master and NPC companion.
Runs completely offline using Ollama and a local LLM.
No internet required after initial setup. No API costs. No data leaving your machine.

![CI](https://github.com/YOURUSERNAME/questkeeper/actions/workflows/ci.yml/badge.svg)

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

---

## What QuestKeeper Can Do

- 🎲 **Roll real dice** — attacks, skill checks, saving throws
- 🗡️ **Track HP** — damage updates your character permanently
- 🎒 **Manage inventory** — items stored in a real database
- 📜 **Remember your campaign** — sessions summarized and recalled
- 📖 **Read your custom lore** — RAG pipeline from your own PDFs
- 🧙 **Distinct NPC voices** — Mira, Old Cobb, and the Hollow King each sound unique
- 🔒 **Fully offline** — Llama 3.2 3B runs locally via Ollama

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| LLM | Ollama + Llama 3.2 3B | Local language model |
| Backend | FastAPI + Uvicorn | API server |
| Frontend | Streamlit | Chat interface |
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
↓           ↓           ↓
Ollama LLM   SQLite DB   ChromaDB
(port 11434) (characters) (lore vectors)
↑
RAG Pipeline
(PDF → chunks → embeddings → retrieval)

---

## Quick Start (Docker)

The easiest way to run QuestKeeper.

**Prerequisites:**
- Docker Desktop installed
- Ollama installed and running
- Llama 3.2 3B downloaded

**1. Install Ollama**
https://ollama.com/download

**2. Pull the model**
```bash
ollama pull llama3.2:3b
```

**3. Clone this repository**
```bash
git clone https://github.com/YOURUSERNAME/questkeeper.git
cd questkeeper
```

**4. Start everything**
```bash
docker compose up --build
```

**5. Open the app**
http://localhost:8501

That's it. One command after setup.

---

## Manual Setup (Without Docker)

**1. Clone the repository**
```bash
git clone https://github.com/YOURUSERNAME/questkeeper.git
cd questkeeper
```

**2. Create virtual environment**
```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Install and start Ollama**
https://ollama.com/download
ollama pull llama3.2:3b

**5. Initialize database**
```bash
python -m app.db.database
```

**6. Add your lore PDFs**
Place any PDF files in the data/ folder
Run: python -m app.rag.embedder

**7. Run the backend**
```bash
uvicorn app.api.routes:app --reload --port 8000
```

**8. Run the frontend (new terminal)**
```bash
streamlit run app/frontend/chat.py
```

**9. Open the app**
http://localhost:8501

---

## Project Structure

```
questkeeper/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── app/
│   ├── core/
│   │   ├── llm.py              # Ollama communication
│   │   ├── tools.py            # Dice, inventory, damage tools
│   │   ├── agent.py            # Tool detection and agent loop
│   │   └── npcs.py             # NPC personality profiles
│   ├── api/
│   │   └── routes.py           # FastAPI routes
│   ├── frontend/
│   │   └── chat.py             # Streamlit chat UI
│   ├── db/
│   │   ├── database.py         # SQLite connection and init
│   │   ├── characters.py       # Character CRUD
│   │   ├── inventory.py        # Inventory CRUD
│   │   └── memory.py           # Session and message storage
│   ├── rag/
│   │   ├── loader.py           # PDF extraction and chunking
│   │   ├── embedder.py         # Embedding and ChromaDB storage
│   │   └── pipeline.py         # RAG retrieval pipeline
│   └── memory/
│       └── summarizer.py       # Session summarization
├── data/                       # Place your PDF lore files here
├── tests/
│   └── test_tools.py           # Automated tests
├── docs/                       # Notes and documentation
├── Dockerfile                  # Container recipe
├── docker-compose.yml          # Multi-container setup
├── requirements.txt            # Python dependencies
├── .gitignore                  # Files excluded from Git
├── .dockerignore               # Files excluded from Docker
└── README.md                   # This file
```
---

## How It Works

### RAG Pipeline
PDF File → Extract text → Split into chunks → Convert to vectors
↓
Player asks question → Convert to vector → Find similar chunks
↓
Relevant chunks + Question + History → LLM → Accurate answer

### Tool Calling
Player: "I attack the goblin"
↓
Code detects attack keyword
↓
roll_dice(sides=20) → result: 14
↓
LLM narrates: "You rolled 14, a solid hit..."

### Memory System
Every message → saved to SQLite
Session ends  → LLM generates summary → saved to SQLite
Next session  → summaries loaded → injected into prompt
→ Aldric remembers everything

### NPC Detection
Player: "I speak to Mira Thornquist"
↓
detect_npc() finds "mira" keyword
↓
Mira's personality profile injected
↓
LLM responds as Mira, not Aldric

---

## Running Tests

```bash
pytest tests/ -v
```

---

## NPCs Available

| NPC | Keywords | Personality |
|-----|---------|-------------|
| Mira Thornquist | mira, captain, guard captain | Gruff, suspicious, short sentences |
| Old Cobb | cobb, hermit, blind hermit | Cryptic, pauses, calls you "shadow-touched" |
| Hollow King | hollow king, velmorath | Cold, uses "we", calls you by name |

---

## Adding Custom Lore

1. Place any PDF in the `data/` folder
2. Run the embedder:
```bash
python -m app.rag.embedder
```
3. Aldric now knows everything in that PDF

---

## Built As A Learning Project

QuestKeeper was built phase by phase as a learning project covering:
Python, FastAPI, Streamlit, SQLite, ChromaDB, RAG pipelines,
tool calling, conversation memory, NPC design, Docker, and CI/CD.

Every component is understood, not just copied.

---

## License

MIT License — use, modify, share freely.

Replace Your Username
Find these two lines and replace YOURUSERNAME with your actual GitHub username:
markdown![CI](https://github.com/YOURUSERNAME/questkeeper/actions/workflows/ci.yml/badge.svg)
git clone https://github.com/YOURUSERNAME/questkeeper.git