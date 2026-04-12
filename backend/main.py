from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from routes.compress import router as compress_router
from routes.extract import router as extract_router
from services.file_service import extract_text_from_file
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Context Compression & Transfer Engine",
    version="1.1.0",
    description="Compress long chat histories into structured, information-dense context packs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compress_router, prefix="/compress", tags=["compress"])
app.include_router(extract_router, prefix="/extract", tags=["extract"])


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    text = await extract_text_from_file(content, file.filename)
    return {"text": text}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "context-compression-engine"}
