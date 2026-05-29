import os
import base64
import io
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from dotenv import load_dotenv
# NEW LINE (Fixed for Uvicorn environment context)
# from week_2.src.prompt_model import prompt_model

# from src.week_2.src.prompt_model import prompt_model
from week_2.src.prompt_model import prompt_model
# from week_2.src.prompt_model import prompt_model
# from week_2.src.prompt_model import prompt_model

# Absolute import path based on your verified workspace file tree structure
# from src.week_2.src.prompt_model import prompt_model

# Load environment configurations from the repository root
load_dotenv(dotenv_path="../../.env")

app = FastAPI(title="Resume Helper Backend")

# Enable CORS so your frontend network interface can securely exchange payloads
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Strict Pydantic parsing layout matching your JavaScript frontend schema
class ChatRequest(BaseModel):
    message: str
    pdf_data: str | None = None  # Holds raw Base64 document data strings
    pdf_name: str | None = None


def extract_pdf_text_from_base64(base64_str: str) -> str:
    """
    Decodes an incoming base64 payload block back into binary data stream matrices,
    then processes text extraction out of the resulting PDF pages.
    """
    try:
        # Revert Base64 encoding structure back to binary format
        pdf_bytes = base64.b64decode(base64_str)
        pdf_file = io.BytesIO(pdf_bytes)
        
        # Scrape character matrices using pypdf parser engine
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid PDF attachment matrix processing error: {str(e)}"
        )


@app.post("/chat")
async def chat(payload: ChatRequest):
    """
    Main API endpoint intercepted privately by the frontend reverse proxy server.
    """
    context_text = ""
    
    # 1. Look for uploaded file strings to perform RAG layout injection text parsing
    if payload.pdf_data:
        context_text = extract_pdf_text_from_base64(payload.pdf_data)
    
    # 2. Hand off execution control directly to your week_2 prompt_model engine layer
    try:
        # Default model tag parameter hardcoded to "ds" for DeepSeek-R1 processing.
        # Change this string identifier parameter to "gem" to seamlessly pivot to Gemini cloud processing!
        ai_reply = prompt_model(model_identifier="ds", prompt=payload.message, context=context_text)
        
        return {"response": ai_reply}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"response": f"[Backend Module Failure] Failed executing integrated prompt_model script: {str(e)}"}
        )

@app.get("/")
async def root():
    return {
        "message": "Resume Helper Backend API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "root": "GET /"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "timestamp": "2024-01-01T00:00:00Z"
    }