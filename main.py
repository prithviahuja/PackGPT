from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from compress import router as compress_router
from extract import router as extract_router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Context Compression & Transfer Engine",
    version="1.0.0",
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


@app.get("/health")
async def health():
    return {"status": "ok", "service": "context-compression-engine"}
