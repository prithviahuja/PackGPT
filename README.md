# Context Compression & Transfer Engine

Transform thousands of lines of chat history into structured, reusable intelligence packs.

## What it does

This tool takes a long ChatGPT/Claude conversation, runs it through a multi-stage extraction pipeline, and outputs a dense **Context Pack** — a structured document that preserves all the important information (goals, decisions, errors, solutions, code) in a format that fits in a new chat's context window.

**This is NOT summarization.** It extracts structured intelligence with maximum information density.

## Architecture

```
Raw Chat Text
    │
    ▼
[Parser] → Detect roles, extract code blocks, chunk by token limit
    │
    ▼
[LLM Extraction] → Parallel async extraction per chunk (structured JSON)
    │
    ▼
[Merge/Dedup] → LLM-powered merge of all chunk extractions
    │
    ▼
[Formatter] → Convert JSON to LLM-friendly Context Pack
```

## Folder Structure

```
context-engine/
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── compress.py
│   │   └── extract.py
│   └── services/
│       ├── parser.py         # Chat parsing & chunking
│       ├── compressor.py     # Async parallel processing
│       ├── llm_handler.py    # Prompts & OpenAI calls
│       └── formatter.py      # Context Pack generator
├── frontend/
│   └── app.py                # Streamlit UI
└── requirements.txt
```

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Start the frontend (new terminal)

```bash
cd frontend
streamlit run app.py
```

### 4. Open browser

Go to: `http://localhost:8501`

## API Endpoints

### POST /compress
Input: `{ "chat_text": "...", "model": "gpt-4o-mini", "openai_api_key": "sk-..." }`
Output: `{ "structured": {...}, "context_pack": "...", "stats": {...} }`

### POST /extract
Input: `{ "chat_text": "...", "model": "gpt-4o-mini", "openai_api_key": "sk-..." }`
Output: `{ "structured": {...} }`

### GET /health
Output: `{ "status": "ok" }`

## Supported Chat Formats

The parser detects these role patterns:
- `User: ...` / `You: ...` / `Human: ...`
- `Assistant: ...` / `ChatGPT: ...` / `Claude: ...` / `AI: ...`

## Output Structure (Structured JSON)

```json
{
  "user_goal": "What the user was trying to accomplish",
  "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
  "decisions": ["Used async routes for performance", "..."],
  "problems": ["Error: Cannot connect to DB on port 5432", "..."],
  "solutions": ["Fixed by changing connection pool size to 10", "..."],
  "code_snippets": [{"label": "DB connection setup", "code": "..."}],
  "constraints": ["Must support 10k concurrent users", "..."],
  "notes": ["Auth token expires after 1 hour", "..."]
}
```

## Context Pack Output

```
=== CONTEXT PACK START ===

[GOAL]
Build a REST API for task management with auth

[STACK]
FastAPI, PostgreSQL, Redis, JWT

[DECISIONS MADE]
• Used JWT over sessions for stateless auth
• Redis for caching user sessions

[KNOWN ISSUES / ERRORS]
• sqlalchemy.exc.OperationalError on high concurrency

[SOLUTIONS / FIXES APPLIED]
• Increased connection pool to 20, added pool_pre_ping=True

[KEY CODE]
// Database session factory
```python
engine = create_async_engine(DATABASE_URL, pool_size=20)
```

[IMPORTANT NOTES]
• JWT secret must be rotated every 30 days

=== CONTEXT PACK END ===
```

## How to use the output

1. Copy the Context Pack
2. Start a new chat with ChatGPT or Claude
3. Paste the Context Pack as your first message with text like:

> "Here is the context from my previous conversation. Continue from where we left off: [paste context pack]"

## Notes

- Uses `gpt-4o-mini` by default (cheap and fast)
- Large chats are split into chunks and processed in parallel
- The merge step uses another LLM call to deduplicate across chunks
- Typical compression: 10,000 tokens → 500-800 tokens with no major info loss
