# AI Negotiation Platform

This is a stateful, multi-step pipeline for automating service negotiations, built with FastAPI, LangGraph, PostgreSQL, and Celery.

## Phase 0: Skeleton Setup

The foundational phase establishes the project structure, database migrations, and docker-compose networking according to the locked tech stack.

### Getting Started Locally

1. Export this project folder.
2. Ensure you have Docker and `docker-compose` installed locally.
3. Run the stack:
   ```bash
   docker-compose up -d
   ```
4. Verify the API health check:
   ```bash
   curl localhost:8000/health
   ```
5. Run the initial database migration:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

---

## Phase 1: Intake & Upload Screen

Captures user service specifications and supports uploading competitor or supplier invoices (e.g., HVAC, moving, plumbing estimates) parsed dynamically using Gemini Vision capabilities.

- **Dynamic Verification:** Analyzes user prompts with a structured output schema to detect missing details recursively.
- **Invoice Vision Analysis:** Automatically extracts vendor names, line items, and prices from uploaded files.

---

## Phase 2: Active Workspace Dashboard

A high-fidelity monitoring and response control center.

- **Status Monitor:** Connects the client to the stateful pipeline, providing progress tracking.
- **Interactive Chat Interface:** Serves follow-up questions from the Intake Agent if more details are needed to finalize requirements.

---

## Phase 3: Strategic Call Planning

Calculates targeted concession bounds and discount targets before initiating call center simulations.

- **Strategic Bento Panel:** Displays the specific strategy chosen for negotiations.
- **Focus Targets:** Highlights the key areas that negotiation agents will emphasize (e.g., Hourly Labor, Warranty, Travel fees).

---

## Phase 4: Voice Calling & Telephony Simulation (Voice Engine)

Handles dialing, conversation state tracking, and post-call speech logs.

- **Live Transcripts:** Access realistic conversation transcripts with each candidate business.
- **Voice Wave Animations:** Visual wave indicator feedback illustrating continuous negotiation.

---

## Phase 5: Decision Support Matrix

Organizes bids and generates professional executive summaries.

- **Quotes Comparison Grid:** A complete visual data matrix comparing competitor pricing, rating, and availability side-by-side.
- **Direct Executive Report Generation:** Download a professionally compiled executive contract review in standard text form directly from the UI.

---

## Phase 6: Multi-Agent Parallel Voice Simulation

A complete parallel voice negotiation framework in both the Next.js fallback simulator and python backend.

- **Sub-graph Concurrency:** Uses LangGraph `Send` API to spawn concurrent, isolated negotiations for each candidate business simultaneously.
- **Realistic Telephony Logs:** Generates distinct, detailed dialogue transcripts and negotiated quotes using Gemini/OpenAI for each concurrent dial.

---

## Phase 7: Real End-to-End Backend Integration

A production-grade Python LangGraph implementation.

- **Dynamic Node Execution:** Connects the Intake, Planning, Multi-Agent Calling, Quote Analysis, and Report nodes.
- **Checkpointed State Persistence:** Employs a robust checkpointer system for full process state resume/pause capabilities.
- **Fallback Simulation Layer:** Leverages a high-fidelity server-side Next.js proxy to guarantee complete, zero-config offline capability.

---

## Architecture

- **API Layer:** FastAPI + Uvicorn
- **Orchestration:** LangGraph (StateGraph) with custom Checkpointer
- **Database:** PostgreSQL (via async SQLAlchemy/Alembic)
- **Background Jobs:** Celery + Redis
- **Validation:** Pydantic v2
