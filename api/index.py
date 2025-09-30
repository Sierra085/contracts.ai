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
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="Contracts.AI", description="Contract Risk Analysis & Document Chat")

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Mount static files and templates - handle if directories don't exist
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # In Vercel, static files are handled differently
    pass

try:
    templates = Jinja2Templates(directory="templates")
except:
    templates = None

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
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        # Fallback HTML with embedded interface
        return HTMLResponse("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>contracts.ai - Contract Risk Analysis & Document Chat</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                html, body { height: 100%; }
                body { background-color: #f8f9fa; }
                .chat-container { overflow-y: auto; border: 1px solid #dee2e6; border-radius: 0.375rem; padding: 1rem; background-color: white; min-height: 200px; max-height: 60vh; }
                .text-preview { overflow-y: auto; font-size: 0.875rem; background-color: #f8f9fa; min-height: 100px; max-height: 150px; }
                .message { margin-bottom: 1rem; padding: 0.75rem; border-radius: 0.5rem; }
                .user-message { background-color: #e3f2fd; border-left: 4px solid #2196f3; margin-left: 2rem; }
                .ai-message { background-color: #f3e5f5; border-left: 4px solid #9c27b0; margin-right: 2rem; }
                .loading { display: inline-block; width: 1rem; height: 1rem; border: 2px solid #f3f3f3; border-top: 2px solid #007bff; border-radius: 50%; animation: spin 1s linear infinite; }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            </style>
        </head>
        <body>
            <div class="container-fluid vh-100 d-flex flex-column">
                <div class="row">
                    <div class="col-12 p-0">
                        <nav class="navbar navbar-dark bg-primary">
                            <div class="container-fluid">
                                <span class="navbar-brand mb-0 h1">
                                    <i class="fas fa-robot"></i> contracts.ai
                                </span>
                                <span class="navbar-text">Contract Risk Analysis & Document Chat with AI</span>
                            </div>
                        </nav>
                    </div>
                </div>
                <div class="row flex-grow-1 mt-2">
                    <div class="col-md-4 d-flex flex-column">
                        <div class="card mb-3">
                            <div class="card-header">
                                <h5><i class="fas fa-upload"></i> Upload Document</h5>
                            </div>
                            <div class="card-body">
                                <form id="uploadForm" enctype="multipart/form-data">
                                    <div class="mb-3">
                                        <label for="file" class="form-label">Choose PDF or DOCX file:</label>
                                        <input type="file" class="form-control" id="file" name="file" accept=".pdf,.docx" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">
                                        <i class="fas fa-upload"></i> Upload & Extract Text
                                    </button>
                                </form>
                                <div id="uploadStatus" class="mt-3"></div>
                                <div id="textPreview" class="mt-3" style="display: none;">
                                    <h6>Extracted Text Preview:</h6>
                                    <div class="border p-2 text-preview">
                                        <small id="extractedText" class="text-muted"></small>
                                    </div>
                                </div>
                                <div id="riskAnalysisSection" class="mt-3" style="display: none;">
                                    <button id="analyzeRisksBtn" class="btn btn-warning w-100">
                                        <i class="fas fa-exclamation-triangle"></i> Analyze Contract Risks
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card flex-grow-1 d-flex flex-column">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0"><i class="fas fa-comments"></i> Chat with Document</h5>
                                <button id="clearChat" class="btn btn-sm btn-outline-secondary">
                                    <i class="fas fa-trash"></i> Clear
                                </button>
                            </div>
                            <div class="card-body d-flex flex-column">
                                <div id="chatMessages" class="flex-grow-1 mb-3 chat-container">
                                    <div class="alert alert-info">
                                        <i class="fas fa-info-circle"></i> 
                                        Upload a document to start chatting with AI about its contents.
                                    </div>
                                </div>
                                <div id="chatInputSection" style="display: none;">
                                    <form id="chatForm">
                                        <div class="input-group">
                                            <input type="text" id="chatInput" class="form-control" placeholder="Ask a question about your document..." disabled>
                                            <button type="submit" id="sendButton" class="btn btn-success" disabled>
                                                <i class="fas fa-paper-plane"></i>
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8 d-flex flex-column">
                        <div id="riskAnalysisResults" class="card flex-grow-1" style="display: none;">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="fas fa-shield-alt"></i> Risk Analysis Results</h5>
                            </div>
                            <div class="card-body">
                                <div id="riskAnalysisContent"></div>
                            </div>
                        </div>
                        <div id="riskAnalysisPlaceholder" class="card flex-grow-1">
                            <div class="card-body d-flex align-items-center justify-content-center">
                                <div class="text-center text-muted">
                                    <i class="fas fa-shield-alt fa-3x mb-3"></i>
                                    <h5>Contract Risk Analysis</h5>
                                    <p>Upload a contract document and click "Analyze Contract Risks" to see detailed risk assessment results here.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                let extractedText = '';
                const uploadForm = document.getElementById('uploadForm');
                const chatForm = document.getElementById('chatForm');
                const uploadStatus = document.getElementById('uploadStatus');
                const textPreview = document.getElementById('textPreview');
                const extractedTextEl = document.getElementById('extractedText');
                const chatMessages = document.getElementById('chatMessages');
                const chatInput = document.getElementById('chatInput');
                const sendButton = document.getElementById('sendButton');
                const chatInputSection = document.getElementById('chatInputSection');
                const clearChatBtn = document.getElementById('clearChat');
                const riskAnalysisSection = document.getElementById('riskAnalysisSection');
                const analyzeRisksBtn = document.getElementById('analyzeRisksBtn');
                const riskAnalysisResults = document.getElementById('riskAnalysisResults');
                const riskAnalysisContent = document.getElementById('riskAnalysisContent');
                const riskAnalysisPlaceholder = document.getElementById('riskAnalysisPlaceholder');

                uploadForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const formData = new FormData();
                    const fileInput = document.getElementById('file');
                    const file = fileInput.files[0];
                    
                    if (!file) {
                        showStatus('Please select a file.', 'warning');
                        return;
                    }
                    
                    formData.append('file', file);
                    showStatus('Extracting text from document...', 'info');
                    
                    try {
                        const response = await fetch('/extract', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            extractedText = result.text;
                            showStatus(`✅ Successfully extracted text from ${file.name}`, 'success');
                            extractedTextEl.textContent = extractedText.substring(0, 300) + '...';
                            textPreview.style.display = 'block';
                            enableChat();
                            riskAnalysisSection.style.display = 'block';
                        } else {
                            showStatus(`❌ Error: ${result.error}`, 'danger');
                        }
                    } catch (error) {
                        showStatus(`❌ Error uploading file: ${error.message}`, 'danger');
                    }
                });

                chatForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const question = chatInput.value.trim();
                    if (!question) return;
                    
                    addMessage(question, 'user');
                    chatInput.value = '';
                    chatInput.disabled = true;
                    sendButton.disabled = true;
                    
                    const thinkingId = addMessage('<div class="loading"></div> AI is analyzing...', 'ai');
                    
                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: extractedText, question: question })
                        });
                        
                        const result = await response.json();
                        document.getElementById(thinkingId).remove();
                        
                        if (response.ok) {
                            addMessage(result.answer, 'ai');
                        } else {
                            addMessage(`<div class="alert alert-danger mb-0">${result.error}</div>`, 'ai');
                        }
                    } catch (error) {
                        document.getElementById(thinkingId).remove();
                        addMessage(`<div class="alert alert-danger mb-0">❌ Network Error: ${error.message}</div>`, 'ai');
                    }
                    
                    chatInput.disabled = false;
                    sendButton.disabled = false;
                    chatInput.focus();
                });

                analyzeRisksBtn.addEventListener('click', async () => {
                    if (!extractedText) {
                        showStatus('Please upload a document first.', 'warning');
                        return;
                    }
                    
                    analyzeRisksBtn.disabled = true;
                    analyzeRisksBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
                    
                    try {
                        const response = await fetch('/analyze-risks', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: extractedText })
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            displayRiskAnalysis(result.analysis);
                            riskAnalysisResults.style.display = 'block';
                            riskAnalysisPlaceholder.style.display = 'none';
                        } else {
                            showStatus(`<div class="alert alert-danger mb-0">${result.error}</div>`, 'danger');
                        }
                    } catch (error) {
                        showStatus(`<div class="alert alert-danger mb-0">❌ Network Error: ${error.message}</div>`, 'danger');
                    }
                    
                    analyzeRisksBtn.disabled = false;
                    analyzeRisksBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Analyze Contract Risks';
                });

                clearChatBtn.addEventListener('click', () => {
                    chatMessages.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle"></i> Chat cleared.</div>';
                });

                function showStatus(message, type) {
                    uploadStatus.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
                }

                function enableChat() {
                    chatMessages.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle"></i> Document loaded! Ask me anything.</div>';
                    chatInputSection.style.display = 'block';
                    chatInput.disabled = false;
                    sendButton.disabled = false;
                    chatInput.focus();
                }

                function addMessage(content, sender) {
                    const messageId = 'msg-' + Date.now();
                    const isUser = sender === 'user';
                    const icon = isUser ? 'fas fa-user' : 'fas fa-robot';
                    const className = isUser ? 'user-message' : 'ai-message';
                    const title = isUser ? 'You' : 'AI Assistant';
                    
                    const messageHtml = `
                        <div id="${messageId}" class="message ${className}">
                            <div><i class="${icon}"></i> <strong>${title}:</strong></div>
                            <div>${content}</div>
                        </div>
                    `;
                    
                    chatMessages.insertAdjacentHTML('beforeend', messageHtml);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    return messageId;
                }

                function displayRiskAnalysis(analysis) {
                    let html = '';
                    if (analysis.raw_analysis) {
                        html = `<div class="alert alert-info"><h6>Risk Analysis:</h6><pre style="white-space: pre-wrap;">${analysis.raw_analysis}</pre></div>`;
                    } else {
                        const riskLevelClass = getRiskLevelClass(analysis.overall_risk_level);
                        html = `<div class="alert alert-${riskLevelClass}"><h6>Overall Risk Level: ${analysis.overall_risk_level || 'Unknown'}</h6></div>`;
                        
                        if (analysis.key_concerns && analysis.key_concerns.length > 0) {
                            html += `<div class="alert alert-warning mb-3"><h6>Key Concerns</h6><ul class="mb-0">${analysis.key_concerns.map(concern => `<li>${concern}</li>`).join('')}</ul></div>`;
                        }
                        
                        if (analysis.risk_categories && analysis.risk_categories.length > 0) {
                            html += '<h6>Risk Categories</h6>';
                            analysis.risk_categories.forEach(category => {
                                const categoryClass = getRiskLevelClass(category.level);
                                html += `
                                    <div class="card mb-3">
                                        <div class="card-header"><h6 class="mb-0"><span class="badge bg-${categoryClass}">${category.level || 'Unknown'}</span> ${category.category || 'Unknown Category'}</h6></div>
                                        <div class="card-body"><p>${category.description || 'No description available'}</p></div>
                                    </div>
                                `;
                            });
                        }
                        
                        if (analysis.summary) {
                            html += `<div class="alert alert-secondary"><h6>Summary</h6><p class="mb-0">${analysis.summary}</p></div>`;
                        }
                    }
                    riskAnalysisContent.innerHTML = html;
                }

                function getRiskLevelClass(level) {
                    if (!level) return 'secondary';
                    switch (level.toLowerCase()) {
                        case 'low': return 'success';
                        case 'medium': return 'warning';
                        case 'high': return 'danger';
                        default: return 'secondary';
                    }
                }
            </script>
        </body>
        </html>
        """)

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    if not file:
        return JSONResponse({"error": "No file uploaded"}, status_code=400)
    
    suffix = os.path.splitext(file.filename)[-1].lower()
    
    if suffix not in [".pdf", ".docx"]:
        return JSONResponse({"error": "Unsupported file type. Only PDF and DOCX files are supported."}, status_code=400)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
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
    except Exception as e:
        return JSONResponse({"error": f"Error extracting text: {str(e)}"}, status_code=500)
    finally:
        try:
            os.unlink(file_path)
        except:
            pass
    
    return {"text": text}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not GEMINI_API_KEY:
        return JSONResponse(
            {"error": "Gemini API key not configured. Please check your environment variables."},
            status_code=500
        )
    
    try:
        prompt = f"""You are an expert document assistant. Here is the extracted document data:

{req.text}

User question: {req.question}

Please provide a helpful, accurate, and detailed answer based on the document content."""

        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        answer = response.text if hasattr(response, 'text') else str(response)
        return {"answer": answer}
    except Exception as e:
        error_message = str(e)
        
        # Handle specific API errors
        if "429" in error_message or "quota" in error_message.lower() or "rate limit" in error_message.lower():
            return JSONResponse(
                {"error": "🚫 API Rate Limit Exceeded: You've reached the free tier limit for Gemini API. Please wait a few minutes before trying again."},
                status_code=429
            )
        elif "401" in error_message or "unauthorized" in error_message.lower():
            return JSONResponse(
                {"error": "🔑 API Key Error: Please check that your Gemini API key is valid and properly configured."},
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
    if not GEMINI_API_KEY:
        return JSONResponse(
            {"error": "Gemini API key not configured. Please check your environment variables."},
            status_code=500
        )
    
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
                {"error": "🚫 API Rate Limit Exceeded: You've reached the free tier limit for Gemini API. Please wait a few minutes before trying again."},
                status_code=429
            )
        elif "401" in error_message or "unauthorized" in error_message.lower():
            return JSONResponse(
                {"error": "🔑 API Key Error: Please check that your Gemini API key is valid and properly configured."},
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

@app.get("/health")
async def health():
    return {"status": "healthy", "gemini_configured": bool(GEMINI_API_KEY)}

# For Vercel deployment
handler = app
