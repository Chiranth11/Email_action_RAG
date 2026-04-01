Built as part of a self-directed GenAI learning programme alongside an MBA, this project demonstrates end-to-end RAG pipeline design — from ingestion through retrieval, generation, and evaluation — applied to a real knowledge-worker productivity problem.

Email Action RAG (Sticky Notes)
1. Project Title

Email Action RAG — Turning Emails into Actionable Sticky Notes

2. Problem Statement (clear & relatable)

Modern inboxes are overloaded with informational emails, announcements, and tasks.
Important actions and deadlines are buried inside long email threads, leading to:

    - Missed deadlines

    - Cognitive overload

    - Constant inbox checking

Goal:
Create a system that extracts only what the user needs to do, prioritizes it, and shows it as a simple sticky-note style task list.

3. Solution Overview

   1. This project builds a Retrieval-Augmented Generation (RAG) system that:

   2. Ingests emails (static snapshots for privacy)

   3. Retrieves only relevant emails using embeddings

   4. Extracts actionable tasks using an LLM

   5. Ranks actions based on urgency and importance

   6. Displays them in a minimal sticky-note UI

The system is designed with clear separation of concerns:

    - Ingestion

    - Retrieval

    - Generation

    - Ranking

    - Presentation

4. Key Features

    - True RAG pipeline (retrieval before generation)

    - Action & deadline extraction (structured JSON)

    - Priority-based ranking

    - Minimal sticky-note UX

    - Privacy-first (no live inbox access required)

    - Modular ingestion (JSON / Gmail / Outlook-ready)

5. Architecture Overview
        High-level flow
        Email Source (JSON snapshots)
                ↓
        Email Loader / Normalizer
                ↓
        Embedding + FAISS Index
                ↓
        Retriever (top-K relevant emails)
                ↓
        LLM Action Extractor
                ↓
        Normalization + Validation
                ↓
        Ranking Engine
                ↓
        Sticky Notes UI (Streamlit)

6. Architecture Diagram 
        Logical Architecture
        ┌──────────────┐
        │ Email Source │
        │ (JSON)       │
        └──────┬───────┘
            ↓
        ┌──────────────┐
        │ Ingestion     │
        │ email_loader  │
        └──────┬───────┘
            ↓
        ┌──────────────┐
        │ Embeddings    │
        │ FAISS Index   │
        └──────┬───────┘
            ↓
        ┌──────────────┐
        │ Retrieval     │
        │ (Top-K)       │
        └──────┬───────┘
            ↓
        ┌──────────────┐
        │ LLM Action    │
        │ Extraction    │
        └──────┬───────┘
            ↓
        ┌──────────────┐
        │ Normalization │
        │ + Validation  │
        └──────┬───────┘
            ↓
        ┌──────────────┐
        │ Ranking       │
        │ Engine        │
        └──────┬───────┘
            ↓
        ┌──────────────┐
        │ Sticky Notes  │
        │ UI (Streamlit)│
        └──────────────┘


7. Tech Stack
    Layer			Technology
    Language			Python
    LLM				    Qwen2.5-7B (Ollama, local)
    Embeddings			Ollama embeddings
    Vector Store		FAISS
    RAG Framework		LangChain
    UI			        Streamlit
    Data		        Sanitized email snapshots (JSON)

8. Why Static Email Data?

Privacy-first design choice

Avoids exposing personal or institutional inboxes

Enables deterministic demos

Same interface works for Gmail / Outlook later

The ingestion layer is intentionally decoupled from the RAG core.

9. Example Output
• Sign up to cancel return journey if needed (by This Sunday)
  - Impact Expedition 2026 — Vivek Velamuri

• Read, sign and return the Ambassador Code of Conduct
  - Unibuddy Ambassador — Emilia Enderling

10. Design Decisions & Trade-offs

Why not live email integration?

OAuth & privacy risks outweigh MVP value

Why not parse natural language dates to timestamps?

Avoid hallucinations; treat deadline presence as signal

Why minimal UI?

Sticky notes optimize execution, not browsing

11. Future Enhancements

Gmail / Outlook ingestion (read-only)

RAG for abbreviation expansion

Notification system

Deadline normalization

Multi-language support

Limitations
1. String-based grounding may fail on paraphrased outputs.
2. Local LLM introduces slight non-determinism.
3. Deadline normalization currently rule-based.
