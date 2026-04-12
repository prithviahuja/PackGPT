# Context Compression & Transfer Engine (v1.1)

A high-performance system to transform thousands of lines of chat history into structured, information-dense context packs. Built with **Next.js 16** and **FastAPI**.

## Architecture

- **Frontend**: Next.js 16 (React 19, Tailwind CSS, Radix UI)
- **Backend**: FastAPI (Python 3.10+)
- **Storage**: Local session/localStorage for history

## Features

- **Context Compression**: Multi-stage extraction (Parse → Extract → Merge → Format).
- **File Support**: Extract text from `.pdf`, `.md`, and `.txt` files directly.
- **Structured Intelligence**: Preserves goals, tech stacks, decisions, problems, and code snippets mapping.
- **Multi-Model Support**: Optimized for Gemini 3 Flash and Llama 3.3.

## Project Structure

```
gpt-summarizer/
├── backend/
│   ├── main.py               # FastAPI Entry Point
│   ├── routes/
│   │   ├── compress.py       # Compression Endpoint
│   │   └── extract.py        # Extraction Endpoint
│   └── services/
│       ├── chat_parser.py    # Text segmenting logic
│       ├── file_service.py   # PDF/MD/TXT extraction
│       ├── compressor.py     # Async parallel processing
│       ├── llm_handler.py    # LLM Prompting & Logic
│       └── formatter.py      # Context Pack assembly
├── frontend/                 # Next.js Application
└── requirements.txt
```

## Setup & Run

### 1. Install Dependencies

```bash
# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
```

### 2. Start Services

**Backend (Port 8000):**
```bash
cd backend
uvicorn main:app --reload
```

**Frontend (Port 3000):**
```bash
cd frontend
npm run dev
```

## How to use

1. **Upload**: Use the "Upload File" button to extract text from a PDF, Markdown, or Text file.
2. **Edit**: Review and refine the extracted text in the textarea.
3. **Compress**: Select a model and click "Compress".
4. **Copy**: Grab the "Context Pack" and paste it into a new chat to continue your work with full context.
