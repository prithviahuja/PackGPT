import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes.compress import router as compress_router
from routes.extract import router as extract_router
from services.file_service import extract_text_from_file
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Pack GPT | Context Compression Engine",
    version="1.2.0",
    description="Compress long chat histories into structured, information-dense context packs"
)

# Restrict CORS to known frontend origins. Configure via the ALLOWED_ORIGINS env
# var (comma-separated list); falls back to local development origins.
_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()] or [
    "https://packgpt.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(compress_router, prefix="/compress", tags=["compress"])
app.include_router(extract_router, prefix="/extract", tags=["extract"])


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    try:
        text = await extract_text_from_file(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"text": text}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "context-compression-engine"}
