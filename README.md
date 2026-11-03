





# 🌍  Multi-Agent Travel Concierge

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful_Orchestration-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-psycopg3_Pool-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7.svg)](https://render.com/)

An asynchronous, stateful multi-agent travel concierge application built with **FastAPI**, **LangGraph**, and **PostgreSQL**. The platform generates personalized multi-day travel itineraries via real-time tool orchestration (live weather and places retrieval) and provides interactive, multi-turn itinerary refinement powered by persistent database checkpointing and JWT authentication.

---

## 🚀 Live Demo & Visual Walkthrough

- **Live Application:** [https://multi-agent-travel-concierge.onrender.com/](https://multi-agent-travel-concierge.onrender.com/)
- **API Documentation (Swagger UI):** `https://multi-agent-travel-concierge.onrender.com/docs`

 ![App Demo](https://github.com/user-attachments/assets/5279c1b2-a5ae-49ac-880e-5ae87df06c60)
 
| Dual-Pane Responsive Workspace | Multi-Turn Contextual Refinement |
| :---: | :---: |
| *![](assets/Screenshot%203.png)* | *![](assets/Screenshot%204.png)* |

---

### Key Architectural Capabilities
- **Stateful Multi-Agent Workflows:** Orchestrated via LangGraph with cyclic validation nodes.
- **Session Checkpointing:** Conversation state and thread checkpoints persisted across restarts using PostgreSQL.
- **Zero-Flicker Split Panes:** Independent dual-column scrolling with synchronous Markdown parsing.



## ⚡ Architectural Evolution: Prototype to Production

This project represents an end-to-end refactor from a traditional single-turn Flask wrapper to an enterprise-grade agentic architecture:

| Capability | Legacy Prototype (Flask + Raw LLM) | Current Architecture (FastAPI + LangGraph) |
| :--- | :--- | :--- |
| **Execution Model** | Synchronous, blocking HTTP requests | Asynchronous non-blocking event loop with strict I/O concurrency |
| **Agent Orchestration** | Single unconstrained prompt completion | Cyclic multi-agent graph with dynamic tool invocation & validation |
| **Context & State** | Stateless; client had to resend history | Persistent multi-turn session checkpointing via `AsyncPostgresSaver` |
| **Data Validation** | Manual string manipulation & regex | Strict runtime validation using Pydantic schemas and `EmailStr` |
| **Database Access** | Ad-hoc single connections | `psycopg_pool.AsyncConnectionPool` with lifecycle management |
| **Security & Auth** | None / basic form | Password hashing via `bcrypt` and stateless JWT authorization |
| **Deployment** | Local Python script | Production-ready Dockerized microservice hosted on Render |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    User([Client / Browser]) <-->|JWT / JSON API| Router[FastAPI Application]
    
    subgraph Storage & Session Lifecycle
        Router <-->|AsyncConnectionPool| PG[(PostgreSQL Database)]
        PG -.-> Users[(Users & Auth)]
        PG -.-> Checkpoints[(LangGraph Checkpoints)]
    end

    subgraph LangGraph Multi-Agent Workflow
        Router -->|ainvoke with thread_id| Graph[StateGraph Engine]
        Graph --> Researcher[Researcher Node]
        Researcher --> ToolCond{Requires Tool?}
        ToolCond -- Yes --> ToolNode[Tool Execution Node]
        ToolNode -->|OpenWeather / Places API| ToolCond
        ToolCond -- No --> Generator[Synthesis / Generator Node]
        Generator --> EndNode([Compiled Itinerary Output])
    end

    EndNode -->|JSON / Structured Delimiters| UI[Split-Pane UI Workspace]
```

### Key Workflow Highlights
1. **Researcher Agent:** Interprets travel preferences and dynamically determines if live data (weather, seasonal forecasts, local attractions) is required via bound tools.
2. **Tool Execution Node (`ToolNode`):** Executes async HTTP requests against external weather and attraction APIs.
3. **Generator Agent:** Synthesizes tool insights into an actionable, budgeted day-by-day plan.
4. **Interactive Concierge (`/chat_refine`):** Uses session-scoped threads (`thread_id`) stored in PostgreSQL to modify specific itinerary elements without losing destination context or hallucinating other cities.

---

## 📂 Repository Structure

```text
├── app/
│   ├── core/
│   │   ├── database.py       # Connection pool (psycopg_pool) & table lifecycle
│   │   └── security.py       # Password hashing (bcrypt) & JWT token handlers
│   ├── graph/
│   │   ├── nodes.py          # Agent definitions (researcher, generator)
│   │   ├── state.py          # TypedDict AgentState definitions
│   │   ├── tools.py          # Async weather and places tool integrations
│   │   └── workflow.py       # StateGraph construction & compilation
│   ├── routes/
│   │   ├── auth.py           # Registration & login endpoints
│   │   └── itinerary.py      # Plan generation & follow-up chat refinement
│   ├── schemas/
│   │   ├── request.py        # Pydantic input models (EmailStr, requests)
│   │   └── response.py       # Pydantic structured output models
│   ├── static/               # Assets (brand logos, styling, marked.js)
│   ├── templates/            # Frontend (index.html, login.html)
│   └── main.py               # FastAPI initialization & async lifespan manager
├── Dockerfile                # Production multi-stage Docker configuration
├── requirements.txt          # Frozen, minimal dependency specifications
└── README.md
```

---

## 🛠️ Tech Stack & Key Libraries

- **Backend Framework:** FastAPI (Asynchronous Python 3.11+)
- **Agent Orchestration:** LangGraph, LangChain Core, LangChain Groq
- **LLM Inference:** Groq Cloud (Llama 3 / Mixtral models for low-latency completions)
- **Database & Checkpointing:** PostgreSQL (Supabase), `psycopg[binary]`, `psycopg-pool`
- **Data Validation & Auth:** Pydantic v2, `email-validator`, `python-jose`, `passlib[bcrypt]`
- **Frontend Workspace:** Modern dual-column responsive UI, Vanilla JS, CSS Flexbox, `marked.js`
- **DevOps & Infrastructure:** Docker, Render Cloud Web Services

---

## ⚙️ Local Setup and Installation

### Prerequisites
- Python 3.11+
- PostgreSQL database (paid or free cloud tier via Supabase)
- Groq Cloud API Key

### 1. Clone the Repository
```bash
git clone https://github.com/mohammedawan/multi-agent-travel-concierge.git
cd multi-agent-travel-concierge
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# Windows (Command Prompt / PowerShell)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
# Application Settings
SECRET_KEY=your_super_secret_jwt_key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database (PostgreSQL)
# Note: For pooler connections on Supabase, ensure sslmode=require
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# External APIs
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### 5. Run Database Initialization & API Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
- **Interactive App:** `http://127.0.0.1:8000`
- **Interactive OpenAPI Docs:** `http://127.0.0.1:8000/docs`

---

## 🐳 Docker Deployment

### Build and Run with Docker
```bash
# 1. Build the Docker container image
docker build -t travel-concierge .

# 2. Run the container exposing port 8000
docker run -p 8000:8000 --env-file .env travel-concierge
```

---

## 🔌 API Reference

### Authentication
- `POST /auth/register` — Registers a new user with email and hashed password.
- `POST /auth/login` — Authenticates credentials and returns a Bearer JWT token.

### Travel Concierge Engine
- `POST /generate_itinerary` — Initiates the multi-agent graph with destination, duration, and preferences; outputs initial structured Markdown itinerary.
- `POST /chat_refine` — Receives iterative feedback (e.g., *"Make day 3 more museum-focused"*), retrieves existing checkpoint state from PostgreSQL, and outputs a revised itinerary with conversation summary.

---

## 🛡️ Production Engineering & Reliability Notes

During deployment to containerized Linux environments (Render), several production challenges were systematically addressed:
- **Async Pool Lifecycle:** Implemented deferred pool opening (`open=False`) paired with FastAPI's `lifespan` context manager and `await db_pool.wait()` to avoid `RuntimeError: AsyncConnectionPool open with no running loop` during module import.
- **IPv4 Cloud Compatibility:** Handled outbound IPv6 routing restrictions by configuring IPv4 connection poolers (Supavisor) in session mode.
- **Strict Delimited Parsing:** Implemented a robust fallback parser using `---ITINERARY---` delimiters to prevent duplicate rendering and UI desynchronization between chat bubbles and the main display.

---

