# Email Action RAG — Turning Emails into Actionable Sticky Notes

> Built as part of a self-directed GenAI learning programme alongside an MBA at HHL Leipzig, this project addresses a real knowledge-worker problem: important action items and deadlines are buried inside overloaded email inboxes. The system reads your emails, extracts only what you need to act on, and surfaces it as a prioritised sticky-note list.

---

## The Problem

Modern inboxes mix announcements, newsletters, event invites, and genuine action requests. Important deadlines get lost. The cognitive overhead of triage is significant. The goal of this project is to extract only the actionable signal — what you need to do, by when, and how urgent — and present it in the simplest possible format.

---

## How It Works — Full Pipeline

```
Emails (JSON snapshots)
        ↓
Ingestion Layer
        │  email_loader.py
        │  Normalises fields, validates subject + body,
        │  standardises sender format
        ↓
Indexing Layer
        │  build_index.py
        │  Chunks email bodies (100 tokens, 20 overlap)
        │  Embeds with all-MiniLM-L6-v2 via Ollama
        │  Stores in FAISS index with metadata
        ↓
Retrieval Layer
        │  email_retriever.py
        │  Step 1: Similarity search → top-K matching chunks
        │  Step 2: Expand to ALL chunks for matched email IDs
        │  (ensures full email context, not just a fragment)
        ↓
Generation Layer
        │  action_extractor.py
        │  Groups chunks back by email
        │  Reconstructs full email body from chunks
        │  Calls Qwen2.5:7b-instruct via Ollama
        │  Extracts: action items, deadline, priority
        │  Output: structured ActionItem (Pydantic)
        ↓
Evaluation Layer
        │  action_evaluator.py
        │  TF-IDF cosine similarity: action text vs. email body
        │  Grounding check: similarity ≥ 0.35 = grounded
        │  Confidence score = grounding(50) + deadline(20)
        │                    + priority(20) + similarity bonus(10)
        ↓
Ranking Layer
        │  action_ranker.py
        │  Score = deadline presence(50) + deadline urgency(100 - days_left)
        │          + high-action verbs(50) + priority(50)
        │  High-action verbs: submit, upload, reply, attend, register
        ↓
Streamlit UI (app/sticky_notes_app.py)
        │  Filters: confidence score ≥ 30
        │  Displays ranked actions as sticky notes
        │  Auto-refreshes every 3 minutes
```

---

## Output Schema

Each extracted item is a structured `ActionItem`:

```python
class ActionItem(BaseModel):
    subject: str
    sender: Optional[str]
    action: List[str]           # list of action verbs extracted
    deadline: Optional[str]     # natural language or ISO date
    priority: str               # High | Medium | Low
    source_email_id: str
    grounded: Optional[bool]    # True if action is traceable to email body
    confidence_score: Optional[float]  # 0–100 weighted score
```

---

## Architecture Decisions

**Why chunk emails and then re-expand to full email context at retrieval?**
Chunking at 100 tokens with 20 overlap makes similarity search more precise — a query like "deadline submit assignment" finds the specific paragraph that matters rather than an entire long email. But extracting action items requires the full email context so the LLM understands the complete request. The retrieval layer does both: similarity search to find relevant emails, then chunk expansion to reconstruct the full email body for generation.

**Why all-MiniLM-L6-v2 for embeddings?**
Lightweight (22M parameters), fast, and well-suited for semantic similarity on short to medium text. Runs locally via Ollama — no API cost, no data egress. For production, a fine-tuned email-domain embedding model would likely improve retrieval precision.

**Why Qwen2.5:7b-instruct for extraction?**
Instruction-tuned, good at structured JSON output, and runs locally. Temperature is set to 0 for deterministic extraction. The prompt is locked — no creativity needed, just precise task extraction. The `safe_json_loads()` function handles the common failure modes of local LLMs (markdown fences, leading "json" text, malformed arrays).

**Why TF-IDF cosine similarity for grounding, not embedding similarity?**
TF-IDF is fast, interpretable, and lightweight — no additional model call needed. The grounding check is a safety net, not a precision tool. Its job is to flag when an extracted action has no lexical trace in the source email — a strong hallucination signal. Threshold of 0.35 was tuned empirically on the test emails.

**Why a confidence score rather than a binary pass/fail?**
The confidence score (0–100) is a weighted combination of four signals: grounding, deadline presence, priority level, and semantic similarity. This gives the Streamlit app a tunable filter threshold — currently set to ≥ 30 — rather than a hard cut that either misses real actions or passes hallucinated ones.

**Why privacy-first (local LLMs, JSON email snapshots)?**
The system never connects to a live mailbox. Email data stays on-device. The JSON snapshots in `/Emails` are real HHL MBA programme emails — used with awareness that they contain no sensitive personal or financial information. The ingestion interface is designed to accept Gmail or Outlook data in the same format without changes to downstream logic.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Embedding Model | all-MiniLM-L6-v2 via Ollama (local) |
| Vector Store | FAISS (LangChain wrapper) |
| LLM | Qwen2.5:7b-instruct via Ollama (local, temperature=0) |
| LLM Framework | LangChain + langchain-ollama |
| Optional LLMs | OpenAI, Groq, Google Gemini (via LangChain connectors, configure in `.env`) |
| Evaluation | TF-IDF cosine similarity (scikit-learn) |
| UI | Streamlit (auto-refresh every 3 minutes) |
| Data Schema | Pydantic `ActionItem` model |

---

## Project Structure

```
Email_RAG/
│
├── Emails/
│   ├── emails.json              # Email snapshots (input data)
│   └── msg_json_format.py       # Converts .msg files to JSON format
│
├── ingestion/
│   └── email_loader.py          # Load, validate, normalise emails from JSON
│
├── indexing/
│   └── build_index.py           # Chunk → embed → build FAISS index
│
├── retrieval/
│   └── email_retriever.py       # Similarity search + full email chunk expansion
│
├── generation/
│   └── action_extractor.py      # LLM extraction → structured ActionItem (Pydantic)
│
├── evaluation/
│   └── action_evaluator.py      # TF-IDF grounding check + confidence scoring
│
├── ranking/
│   └── action_ranker.py         # Multi-signal scoring + sticky note formatter
│
├── app/
│   └── sticky_notes_app.py      # Streamlit UI with confidence filter + auto-refresh
│
├── data/
│   └── email_faiss_index/       # Persisted FAISS index (index.faiss + index.pkl)
│
└── requirements.txt
```

---

## Running the Project

**Prerequisites:** Python 3.10+, [Ollama](https://ollama.ai) installed with required models pulled.

```bash
# Pull required models
ollama pull qwen2.5:7b-instruct
ollama pull mahonzhan/all-MiniLM-L6-v2

# Install dependencies
pip install -r requirements.txt

# Step 1: Build the FAISS index (run once)
python -m indexing.build_index

# Step 2: Launch the Streamlit app
streamlit run app/sticky_notes_app.py
```

**Using a cloud LLM instead of Ollama:** The `requirements.txt` includes `langchain-openai`, `langchain-groq`, and `langchain-google-genai`. Set your API key in `.env` and swap the LLM initialisation in `action_extractor.py` to the appropriate LangChain connector.

---

## Evaluation — How We Know It Works

The evaluation layer (`action_evaluator.py`) runs automatically as part of the pipeline and assigns every extracted action item a grounding flag and confidence score before it reaches the UI.

**Grounding check:** TF-IDF cosine similarity between the extracted action text and the source email body. Similarity ≥ 0.35 = grounded (action is traceable to the email). This catches the most common LLM failure mode — extracting plausible but invented actions.

**Confidence scoring (0–100):**
- Grounded: +50
- Has explicit deadline: +20
- Priority = High: +20
- Similarity bonus: up to +10

**UI filter:** Only actions with confidence ≥ 30 are shown. This tunable threshold lets you trade recall (show more, risk some noise) for precision (show fewer, higher confidence).

---

## Limitations (Honest Assessment)

- **Static email snapshots:** The system reads from a pre-built JSON file, not a live mailbox. Gmail/Outlook integration is the natural next step — the ingestion interface is already designed for it.
- **No date normalisation:** Deadlines are extracted as natural language strings ("this Sunday", "by end of week") and stored as-is. The ranking engine partially handles this but cannot compare natural language deadlines with ISO dates reliably.
- **TF-IDF grounding is approximate:** Cosine similarity on bag-of-words does not catch semantic paraphrases. An action item worded differently from the source email may be correctly grounded but score below the threshold. Embedding-based grounding would be more robust.
- **Single-query retrieval:** The current retrieval uses one hardcoded query in the Streamlit app ("deadline submit reply event registration"). A better approach would be multiple targeted queries or query expansion — one for deadline-sensitive actions, one for reply-required items, one for events.
- **Chunk size:** 100 tokens with 20 overlap was set without systematic tuning. For longer, more complex emails, larger chunks may preserve more context for the LLM.

---

## What I Would Add With More Time

- **Live mailbox integration:** Gmail API (OAuth, read-only) using the existing ingestion interface. No changes needed downstream.
- **Embedding-based grounding:** Replace TF-IDF with embedding cosine similarity for more robust hallucination detection on paraphrased actions.
- **Query expansion in retrieval:** Run multiple targeted queries and merge results — deadline queries, reply-required queries, event registration queries — before deduplication.
- **Date normalisation:** Parse natural language deadlines to ISO timestamps using a lightweight library (dateparser), enabling reliable deadline-based ranking.
- **Labelled evaluation set:** A manually verified set of email→action mappings to measure pipeline precision and recall systematically, rather than relying on the grounding heuristic alone.

---

## Context

This project was built independently alongside an MBA at HHL Leipzig Graduate School of Management. The test emails in `/Emails` are real HHL programme emails (event invites, course reminders, deadline notices) — which made the output immediately meaningful and testable rather than relying on synthetic data.

The modular architecture (separate ingestion, indexing, retrieval, generation, evaluation, ranking layers) was a deliberate design choice — each layer can be tested, swapped, or improved independently. This is the same separation of concerns you would apply in a production system.

Full code: [github.com/Chiranth11/Email_action_RAG](https://github.com/Chiranth11/Email_action_RAG)
