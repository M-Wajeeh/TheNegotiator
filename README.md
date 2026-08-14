# 🤖 AI Price Negotiator — Autonomous Multi-Agent Procurement & Negotiation Platform

An enterprise-grade, stateful, multi-agent platform designed to automate service procurement, vendor rate discovery, tactical price negotiations, and quote decision analysis. Built with **Next.js 15**, **FastAPI**, **LangGraph**, **Google Gemini**, **PostgreSQL**, and **Celery**.

---

## 📑 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [LangGraph Workflow Pipeline](#-langgraph-workflow-pipeline)
- [Directory Structure](#-directory-structure)
- [Tech Stack](#-tech-stack)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Environment Variables](#-environment-variables)
- [Installation & Getting Started](#-installation--getting-started)
  - [Prerequisites](#prerequisites)
  - [Method 1: Docker Compose (Full Stack)](#method-1-docker-compose-full-stack)
  - [Method 2: Manual Local Development](#method-2-manual-local-development)
- [Running Automated Tests](#-running-automated-tests)
- [License](#-license)

---

## 🌟 Overview

Negotiating service contracts (such as HVAC repairs, plumbing, enterprise moving, equipment maintenance, and logistics) is traditionally manual, slow, and opaque. **AI Price Negotiator** automates the entire lifecycle:

1. **Intake & Document OCR**: Upload past invoices, estimates, or competitor bids. Gemini Vision parses line items, rates, and terms automatically.
2. **Dynamic Requirement Discovery**: Clarifying agents identify missing job requirements and interact with the user via adaptive intake forms.
3. **Vendor Search & Strategic Planning**: Discovers local or national candidate suppliers and creates a mathematical concession boundary and target discount strategy.
4. **Concurrent Multi-Agent Telephony & Email**: Deploys parallel sub-graphs for each candidate vendor to simulate telephone conversations and email RFQs concurrently using LangGraph's `Send` API.
5. **Quote Normalization & Decision Matrix**: Aggregates received bids into a normalized comparison matrix and generates downloadable executive summary reports.

---

## ⚡ Key Features

- **📄 Multimodal Vision Parser**: Analyzes scanned PDF/PNG/JPEG contractor estimates, extracting vendor identities, hourly rates, materials markup, and service warranties.
- **🧠 LangGraph Multi-Agent Orchestration**: Stateful graph execution supporting checkpointer resumption, interrupts for human approval, and conditional branching.
- **📞 Sub-Graph Parallel Calling**: Executes isolated sub-agent state machines per vendor simultaneously, generating transcripts and negotiated terms.
- **🎙️ Voice Engine & Wave Visualizations**: Real-time voice simulation with audio waveforms, live speech-to-text transcript streams, and ElevenLabs telephony integration.
- **📧 Automated Vendor Email Dispatch**: Drafts and sends formal RFQ emails via Google Gmail API integration.
- **📊 Executive Decision Matrix**: Side-by-side comparison of supplier quotes scoring price, timeline, reviews, and warranty terms.
- **🔒 Checkpointed State Persistence**: Async PostgreSQL persistence with Alembic database migrations and Celery background workers.

---

## 📐 System Architecture

```mermaid
flowchart TD
    User["User / Procurement Manager"] -->|Uploads Invoices & Service Spec| Frontend["Next.js 15 Frontend UI"]
    Frontend -->|REST API / WebSocket| BackendAPI["FastAPI Gateway (:8000)"]
    
    subgraph LG ["LangGraph Execution Pipeline"]
        BackendAPI --> N1["01: Intake & Validation"]
        N1 --> N2["02: Document OCR Parser"]
        N2 --> N3["03: Vendor Discovery (Tavily)"]
        N3 --> N4["04: Strategic Call Planning"]
        N4 -->|LangGraph Send API Fan-Out| VFlow["05: Parallel Vendor Flow (Voice/Email)"]
        VFlow -->|Fan-In / Aggregate| N6["06: Quote Normalization & Analysis"]
        N6 --> N7["07: Recommendation Engine"]
        N7 --> N8{"08: High-Value Human Gate?"}
        N8 -->|Approved| N9["09: Executive Report Generator"]
        N8 -->|Requires Review| UIApproval["Human-in-the-Loop Review"]
        UIApproval --> N9
    end
    
    subgraph Integrations ["Services, Storage & AI Models"]
        BackendAPI --> Postgres[("PostgreSQL 15 (Async DB)")]
        BackendAPI --> Redis[("Redis 7 + Celery Workers")]
        BackendAPI --> GCS[("Google Cloud Storage")]
        N2 -.-> Gemini["Google Gemini 2.5 Vision"]
        VFlow -.-> OpenAI["OpenAI GPT-4o / Realtime"]
        VFlow -.-> ElevenLabs["ElevenLabs Voice Engine"]
        VFlow -.-> Gmail["Gmail API (Auto RFQs)"]
    end
```

---

## 🔄 LangGraph Workflow Pipeline

The state machine is built in `negotiation-platform/app/graph/build_graph.py` with the following nodes:

| Stage | Node Name | Description | Routing / Conditions |
| :--- | :--- | :--- | :--- |
| **01** | `intake` | Extracts user requirements, validates completeness, asks follow-up questions | Loop back if `is_complete == False` |
| **02** | `document_parser` | Multimodal OCR parsing of uploaded estimate invoices | Advances to `business_discovery` |
| **03** | `business_discovery`| Discovers matching vendor businesses via Tavily search | Ends if 0 candidates; else `call_planning` |
| **04** | `call_planning` | Computes target discounts, maximum concession caps, and talking points | Fans out to `vendor_flow` using `Send` API |
| **05** | `vendor_flow` *(Subgraph)* | Concurrent execution for each vendor: calls simulate dialogue, drafts emails, records quotes | Joins all branches into `quote_analysis` |
| **06** | `quote_analysis` | Normalizes bids, parses exclusions, compares pricing and warranties | Advances to `recommendation` |
| **07** | `recommendation` | Selects primary & runner-up vendor, computes risk flags | Routes to `human_gate` or `report` |
| **08** | `human_gate` | Pause checkpoint for human authorization if high-budget threshold reached | Resumes to `report` upon approval |
| **09** | `report` | Compiles full negotiation dossier and executive contract review | Transitions to `END` |

---

## 📁 Directory Structure

```plaintext
Price Negotiator/
├── price-negotiator/
│   ├── app/                               # Next.js 15 App Router
│   │   ├── api/                           # Frontend Next.js Route Handlers
│   │   │   ├── discovery/route.ts         # Vendor search endpoint
│   │   │   ├── gemini/route.ts            # Gemini direct proxy
│   │   │   └── negotiate/route.ts         # Negotiation orchestration proxy
│   │   ├── globals.css                    # Tailwind CSS system styles
│   │   ├── layout.tsx                     # Root layout & font configuration
│   │   └── page.tsx                       # Full interactive negotiation dashboard
│   ├── hooks/                             # React custom hooks
│   │   └── use-mobile.ts                  # Responsive layout detection hook
│   ├── lib/                               # Client utilities
│   │   └── utils.ts                       # Class merging (clsx + tailwind-merge)
│   ├── package.json                       # Frontend dependencies & scripts
│   ├── tsconfig.json                      # TypeScript configuration
│   ├── next.config.ts                     # Next.js runtime configuration
│   ├── .gitignore                         # Root git ignore (protects all secrets)
│   │
│   └── negotiation-platform/              # 🐍 Python FastAPI & LangGraph Backend
│       ├── alembic/                       # Database migrations
│       │   ├── versions/                  # Migration history
│       │   │   └── 0001_initial_schema.py # Initial DB tables
│       │   └── env.py                     # Async SQLAlchemy Alembic environment
│       ├── app/                           # Backend application source
│       │   ├── agents/prompts/            # Structured agent system prompts
│       │   │   ├── business_discovery.py  # Vendor search prompts
│       │   │   ├── call_planning.py       # Negotiation strategy prompts
│       │   │   ├── document_parser.py     # Multimodal OCR prompts
│       │   │   └── intake.py              # Intake requirements prompts
│       │   ├── api/routes/                # FastAPI REST endpoints
│       │   │   ├── analytics.py           # Negotiation savings metrics
│       │   │   ├── calls.py               # Call records & transcripts
│       │   │   ├── documents.py           # Document OCR uploads
│       │   │   ├── files.py               # Google Cloud Storage file handler
│       │   │   ├── negotiations.py        # Pipeline trigger & state polling
│       │   │   ├── quotes.py              # Quote comparison queries
│       │   │   ├── reports.py             # Executive PDF/Text report download
│       │   │   └── voice.py               # Telephony simulation endpoints
│       │   ├── core/                      # Database engine & session setup
│       │   │   └── database.py            # Async engine (asyncpg + SQLAlchemy)
│       │   ├── graph/                     # LangGraph workflow engine
│       │   │   ├── build_graph.py         # Main StateGraph assembly
│       │   │   ├── state.py               # TypedDict state schemas
│       │   │   └── nodes/                 # Individual workflow node logic
│       │   │       ├── business_discovery.py
│       │   │       ├── call_planning.py
│       │   │       ├── document_parser.py
│       │   │       ├── intake.py
│       │   │       ├── quote_analysis.py
│       │   │       ├── recommendation.py
│       │   │       ├── report.py
│       │   │       └── vendor_flow.py     # Subgraph for concurrent vendor calls
│       │   ├── models/                    # SQLAlchemy ORM database models
│       │   │   ├── base.py                # Declarative base
│       │   │   └── schema.py              # User, Negotiation, Business, Quote, Call
│       │   ├── schemas/                   # Pydantic v2 validation models
│       │   │   └── core.py                # API payload schemas
│       │   ├── services/                  # Cloud integrations
│       │   │   └── gcs.py                 # Google Cloud Storage upload/download
│       │   ├── tools/                     # External API client wrappers
│       │   │   ├── elevenlabs_client.py   # ElevenLabs Voice generation
│       │   │   ├── gmail_client.py        # Gmail API RFQ email sender
│       │   │   ├── openai_client.py       # OpenAI GPT-4o client
│       │   │   └── tavily_client.py       # Tavily Web Search client
│       │   ├── workers/                   # Background job queue
│       │   │   └── celery_app.py          # Celery app & worker tasks
│       │   ├── config.py                  # Pydantic Settings configuration
│       │   └── main.py                    # FastAPI application entrypoint
│       ├── tests/                         # Pytest test suite
│       │   └── agents/                    # Node & agent unit tests
│       ├── Dockerfile                     # Backend container definition
│       ├── docker-compose.yml             # API, Worker, Flower, Postgres, Redis
│       ├── requirements.txt               # Python package dependencies
│       └── alembic.ini                    # Alembic migration configuration
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: [Next.js 15](https://nextjs.org/) (React 19, App Router)
- **Styling**: [Tailwind CSS 4](https://tailwindcss.com/)
- **Animations**: [Motion](https://motion.dev/) & [tw-animate-css](https://www.npmjs.com/package/tw-animate-css)
- **Icons**: [Lucide React](https://lucide.dev/)
- **AI SDK**: `@google/genai`

### Backend & Orchestration
- **API Framework**: [FastAPI](https://fastapi.tiangolo.com/) with `uvicorn`
- **Agent Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) & [LangChain](https://www.langchain.com/)
- **Database & ORM**: [PostgreSQL 15](https://www.postgresql.org/), [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/), [asyncpg](https://magicstack.github.io/asyncpg/), [Alembic](https://alembic.sqlalchemy.org/)
- **Background Tasks**: [Celery](https://docs.celeryq.dev/) + [Redis 7](https://redis.io/)
- **Worker Monitoring**: [Flower](https://flower.readthedocs.io/)
- **AI Vision & LLM**: Google Gemini 2.5 Flash, OpenAI GPT-4o
- **Audio & Telephony**: ElevenLabs API
- **Vendor Discovery**: Tavily Web Search API
- **File Storage**: Google Cloud Storage (GCS)

---

## 🔌 API Reference

### FastAPI Backend Endpoints (`http://localhost:8000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | API health check and uptime status |
| `POST` | `/api/v1/negotiations/start` | Initiates a new stateful negotiation workflow |
| `GET` | `/api/v1/negotiations/{id}/state` | Fetches the current snapshot of the LangGraph state |
| `POST` | `/api/v1/negotiations/{id}/resume` | Resumes an interrupted workflow (Human-in-the-Loop gate) |
| `POST` | `/api/v1/documents/parse` | Uploads and parses estimate invoice via Gemini Vision |
| `POST` | `/api/v1/files/upload` | Uploads documents directly to Google Cloud Storage |
| `GET` | `/api/v1/quotes/{negotiation_id}` | Returns all negotiated quotes for comparison |
| `GET` | `/api/v1/calls/{negotiation_id}` | Retrieves call records, audio links, and transcripts |
| `GET` | `/api/v1/reports/{negotiation_id}` | Generates and returns executive negotiation summary |
| `GET` | `/api/v1/analytics/summary` | Aggregated ROI, discounts secured, and negotiation metrics |

### Next.js API Routes (`http://localhost:3000`)

| Method | Route | Description |
| :--- | :--- | :--- |
| `POST` | `/api/discovery` | Searches for vendor candidates using location and service keywords |
| `POST` | `/api/gemini` | Server-side proxy for Gemini Vision document parsing |
| `POST` | `/api/negotiate` | Fallback browser-side simulated multi-agent negotiation loop |

---

## 🗄️ Database Schema

```mermaid
erDiagram
    USERS ||--o{ NEGOTIATIONS : owns
    NEGOTIATIONS ||--o{ BUSINESSES : discovers
    NEGOTIATIONS ||--o{ QUOTES : receives
    NEGOTIATIONS ||--o{ CALLS : initiates
    NEGOTIATIONS ||--o| REPORTS : generates
    BUSINESSES ||--o{ QUOTES : provides
    BUSINESSES ||--o{ CALLS : participates
    CALLS ||--o| TRANSCRIPTS : contains

    USERS {
        uuid id PK
        string email
        timestamp created_at
    }
    NEGOTIATIONS {
        uuid id PK
        uuid user_id FK
        string status
        json state_payload
        timestamp created_at
        timestamp updated_at
    }
    BUSINESSES {
        uuid id PK
        uuid negotiation_id FK
        string name
        string phone_number
        json details
    }
    QUOTES {
        uuid id PK
        uuid negotiation_id FK
        uuid business_id FK
        string amount
        json details
        timestamp created_at
    }
    CALLS {
        uuid id PK
        uuid negotiation_id FK
        uuid business_id FK
        string status
        string outcome
        timestamp created_at
    }
    TRANSCRIPTS {
        uuid id PK
        uuid call_id FK
        string content
        timestamp created_at
    }
    REPORTS {
        uuid id PK
        uuid negotiation_id FK
        string report_url
        timestamp created_at
    }
```

---

## 🔑 Environment Variables

### 1. Root / Frontend `.env` (or `.env.local`)

```bash
# Google Gemini API (Required for Vision OCR & chat)
GEMINI_API_KEY=your_gemini_api_key_here

# Backend Service URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Backend `negotiation-platform/.env`

```bash
# Database & Cache
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/negotiation
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# LLM Providers
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Vendor Discovery & Telephony
TAVILY_API_KEY=your_tavily_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Cloud Storage & Gmail
GCS_BUCKET_NAME=your_gcs_bucket_name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-credentials.json
GMAIL_SENDER_EMAIL=procurement@yourcompany.com
```

---

## 🚀 Installation & Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18.0 or higher)
- [Python](https://www.python.org/) (v3.11 or higher)
- [Docker](https://www.docker.com/) & Docker Compose *(Optional, for containerized run)*

---

### Method 1: Docker Compose (Full Stack Backend)

To launch PostgreSQL, Redis, FastAPI, Celery worker, and Flower monitoring in containers:

1. **Navigate to the backend directory**:
   ```bash
   cd price-negotiator/negotiation-platform
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and supply your API keys
   ```

3. **Start services**:
   ```bash
   docker-compose up -d --build
   ```

4. **Run database migrations**:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Access services**:
   - **FastAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Flower Dashboard**: [http://localhost:5555](http://localhost:5555)

6. **Start the Next.js Frontend**:
   ```bash
   cd ..
   npm install
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### Method 2: Manual Local Development

#### 1. Backend Setup:
```bash
cd price-negotiator/negotiation-platform

# Create and activate virtual environment
python -m venv env
# On Windows:
.\env\Scripts\activate
# On Linux/macOS:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Start Celery Worker (In a separate terminal):
```bash
cd price-negotiator/negotiation-platform
.\env\Scripts\activate
celery -A app.workers.celery_app worker --loglevel=info
```

#### 3. Frontend Setup:
```bash
cd price-negotiator
npm install
npm run dev
```

---

## 🧪 Running Automated Tests

The backend includes automated unit and integration tests using `pytest` and `pytest-asyncio`:

```bash
cd price-negotiator/negotiation-platform
pytest tests/ -v
```

### Test Coverage Areas:
- `tests/agents/test_intake.py` — Verifies requirement extraction and completeness evaluation.
- `tests/agents/test_document_parser.py` — Tests invoice OCR data extraction schema validation.
- `tests/agents/test_business_discovery.py` — Tests candidate business query formatting and ranking.
- `tests/agents/test_call_planning.py` — Validates concession target calculations and tactic selections.

---

## 📄 License

This project is licensed under the **MIT License**. Feel free to use, modify, and distribute for personal and commercial projects.
