from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from parser import parse_chat
from compressor import compress_chunks

router = APIRouter()


class ExtractRequest(BaseModel):
    chat_text: str
    model: str = None
    api_key: str = None  # Renamed from openai_api_key


@router.post("")
async def extract(req: ExtractRequest):
    if not req.chat_text.strip():
        raise HTTPException(status_code=400, detail="chat_text cannot be empty")

    chunks = parse_chat(req.chat_text)
    structured = await compress_chunks(chunks, req.model, req.api_key)
    return {"structured": structured}
