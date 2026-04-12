import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from services.chat_parser import parse_chat
from services.compressor import compress_chunks
from services.formatter import format_context_pack

router = APIRouter()


class CompressRequest(BaseModel):
    input_text: str = Field(..., alias="input")
    model: Optional[str] = "gemini-3-flash-preview"
    api_key: Optional[str] = None

    class Config:
        populate_by_name = True


@router.post("")
async def compress(req: CompressRequest):
    start_time = time.time()
    
    if not req.input_text.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")

    chunks = parse_chat(req.input_text)
    structured = await compress_chunks(chunks, req.model, req.api_key)
    context_pack = format_context_pack(structured)
    
    end_time = time.time()
    processing_time = end_time - start_time

    return {
        "structured": structured,
        "context_pack": context_pack,
        "token_count": len(req.input_text) // 4,  # Simple heuristic for token count
        "compression_ratio": round(len(req.input_text) / max(len(context_pack), 1), 2),
        "processing_time": round(processing_time, 2),
        "stats": {
            "input_chars": len(req.input_text),
            "output_chars": len(context_pack),
            "chunks_processed": len(chunks),
        }
    }
