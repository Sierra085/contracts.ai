from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import tempfile
import os
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import uvicorn
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Get API key from environment variable for security
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required. Please check your .env file.")

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)

# Don't print or log the API key for security     
print("✓ Gemini API configured successfully")

class ChatRequest(BaseModel):
    text: str
    question: str

class RiskAnalysisRequest(BaseModel):
    text: str

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_pdf_ocr(file_path):
    try:
        images = convert_from_path(file_path)
        text = ""
        for img in images:
            if img.mode != "RGB":
                img = img.convert("RGB")
            text += pytesseract.image_to_string(img)
        return text
    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}. Make sure Tesseract and Poppler are installed.")

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        file_path = tmp.name
    try:
        if suffix == ".pdf":
            text = extract_text_from_pdf(file_path)
            if not text.strip():
                text = extract_text_from_pdf_ocr(file_path)
        elif suffix == ".docx":
            text = extract_text_from_docx(file_path)
        else:
            return JSONResponse({"error": "Unsupported file type."}, status_code=400)
    finally:
        os.unlink(file_path)
    return {"text": text}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        prompt = f"You are an expert document assistant. Here is the extracted document data:\n\n{req.text}\n\nUser question: {req.question}\n\nAnswer as helpfully as possible."
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        answer = response.text if hasattr(response, 'text') else str(response)
        return {"answer": answer}
    except Exception as e:
        error_message = str(e)
        
        # Handle specific API errors
        if "429" in error_message or "quota" in error_message.lower() or "rate limit" in error_message.lower():
            return JSONResponse(
                {"error": "🚫 API Rate Limit Exceeded: You've reached the free tier limit for Gemini API. Please wait a few minutes before trying again, or check your API quota at https://ai.google.dev/gemini-api/docs/rate-limits"},
                status_code=429
            )
        elif "401" in error_message or "unauthorized" in error_message.lower():
            return JSONResponse(
                {"error": "🔑 API Key Error: Please check that your Gemini API key is valid and properly configured in the .env file."},
                status_code=401
            )
        elif "403" in error_message or "forbidden" in error_message.lower():
            return JSONResponse(
                {"error": "🚫 API Access Denied: Your API key may not have permission to access the Gemini API."},
                status_code=403
            )
        else:
            return JSONResponse(
                {"error": f"🤖 AI Error: {error_message}"},
                status_code=500
            )

@app.post("/analyze-risks")
async def analyze_risks(req: RiskAnalysisRequest):
    try:
        prompt = f"""You are an expert legal analyst specializing in contract risk assessment. Analyze the following contract document and identify potential risk factors.

Contract Document:
{req.text}

Please provide a comprehensive risk analysis in the following JSON format:
{{
    "overall_risk_level": "Low/Medium/High",
    "risk_categories": [
        {{
            "category": "Financial Risk",
            "level": "Low/Medium/High",
            "description": "Brief description of the risk",
            "specific_clauses": ["List of specific problematic clauses or sections"],
            "recommendations": ["List of recommended actions or mitigations"]
        }}
    ],
    "key_concerns": ["List of the most critical issues"],
    "missing_protections": ["List of protections that should be included but are missing"],
    "summary": "Brief overall assessment and recommendations"
}}

Focus on these risk categories:
1. Financial Risk (payment terms, penalties, liability caps)
2. Performance Risk (delivery obligations, service levels, warranties)
3. Legal/Compliance Risk (regulatory requirements, indemnification, governing law)
4. Operational Risk (termination clauses, force majeure, data security)
5. Reputation Risk (confidentiality, non-disparagement, publicity)
6. Intellectual Property Risk (IP ownership, licensing, infringement)

Be thorough but concise. Only return valid JSON."""

        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        answer = response.text if hasattr(response, 'text') else str(response)
        
        # Try to parse as JSON, if it fails return as text
        try:
            import json
            # Clean the response to extract JSON
            answer = answer.strip()
            if answer.startswith("```json"):
                answer = answer[7:]
            if answer.endswith("```"):
                answer = answer[:-3]
            answer = answer.strip()
            
            parsed_response = json.loads(answer)
            return {"analysis": parsed_response}
        except json.JSONDecodeError:
            # If JSON parsing fails, return as structured text
            return {"analysis": {"raw_analysis": answer}}
            
    except Exception as e:
        error_message = str(e)
        
        # Handle specific API errors
        if "429" in error_message or "quota" in error_message.lower() or "rate limit" in error_message.lower():
            return JSONResponse(
                {"error": "🚫 API Rate Limit Exceeded: You've reached the free tier limit for Gemini API. Please wait a few minutes before trying again, or check your API quota at https://ai.google.dev/gemini-api/docs/rate-limits"},
                status_code=429
            )
        elif "401" in error_message or "unauthorized" in error_message.lower():
            return JSONResponse(
                {"error": "🔑 API Key Error: Please check that your Gemini API key is valid and properly configured in the .env file."},
                status_code=401
            )
        elif "403" in error_message or "forbidden" in error_message.lower():
            return JSONResponse(
                {"error": "🚫 API Access Denied: Your API key may not have permission to access the Gemini API."},
                status_code=403
            )
        else:
            return JSONResponse(
                {"error": f"🤖 AI Error: {error_message}"},
                status_code=500
            )

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
