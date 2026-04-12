from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from services.chat_parser import parse_chat
from services.compressor import compress_chunks

router = APIRouter()


class ExtractRequest(BaseModel):
    input_text: str = Field(..., alias="input")
    model: Optional[str] = "gemini-3-flash-preview"
    api_key: Optional[str] = None

    class Config:
        populate_by_name = True


@router.post("")
async def extract(req: ExtractRequest):
    if not req.input_text.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")

    chunks = parse_chat(req.input_text)
    structured = await compress_chunks(chunks, req.model, req.api_key)
    return {"structured": structured}
