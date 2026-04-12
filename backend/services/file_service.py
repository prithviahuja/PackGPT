import fitz  # PyMuPDF
import os
from typing import Optional

async def extract_text_from_file(file_content: bytes, filename: str) -> Optional[str]:
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ['.txt', '.md']:
        return file_content.decode('utf-8', errors='ignore')
        
    elif ext == '.pdf':
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
            
    else:
        raise ValueError(f"Unsupported file type: {ext}")
