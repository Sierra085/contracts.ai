# Force rebuild
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

from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>contracts.ai - AI Contract Analysis</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-lg-8">
                        <div class="text-center mb-5">
                            <h1 class="display-4 text-primary">
                                <i class="fas fa-robot"></i> contracts.ai
                            </h1>
                            <p class="lead text-muted">AI-Powered Contract Risk Analysis & Document Chat</p>
                        </div>
                        
                        <div class="card shadow">
                            <div class="card-header bg-primary text-white">
                                <h5 class="mb-0"><i class="fas fa-upload"></i> Upload Contract Document</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="fileInput" class="form-label">Choose PDF or DOCX file:</label>
                                    <input type="file" class="form-control" id="fileInput" accept=".pdf,.docx">
                                </div>
                                <button onclick="uploadFile()" class="btn btn-primary btn-lg w-100">
                                    <i class="fas fa-upload"></i> Upload & Analyze
                                </button>
                                <div id="status" class="mt-3"></div>
                            </div>
                        </div>
                        
                        <div id="resultsCard" class="card shadow mt-4" style="display: none;">
                            <div class="card-header bg-success text-white">
                                <h5 class="mb-0"><i class="fas fa-check-circle"></i> Analysis Complete</h5>
                            </div>
                            <div class="card-body">
                                <div id="extractedText" class="mb-4">
                                    <h6>Extracted Text Preview:</h6>
                                    <div class="border p-3 bg-light" style="max-height: 200px; overflow-y: auto;">
                                        <small id="textContent"></small>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <button onclick="analyzeRisks()" class="btn btn-warning w-100 mb-3">
                                            <i class="fas fa-exclamation-triangle"></i> Analyze Risks
                                        </button>
                                    </div>
                                    <div class="col-md-6">
                                        <button onclick="startChat()" class="btn btn-info w-100 mb-3">
                                            <i class="fas fa-comments"></i> Chat with Document
                                        </button>
                                    </div>
                                </div>
                                
                                <div id="analysisResults" style="display: none;"></div>
                                <div id="chatInterface" style="display: none;">
                                    <hr>
                                    <h6>Chat with your document:</h6>
                                    <div id="chatMessages" class="border p-3 mb-3" style="height: 300px; overflow-y: auto;"></div>
                                    <div class="input-group">
                                        <input type="text" id="chatInput" class="form-control" placeholder="Ask a question...">
                                        <button onclick="sendMessage()" class="btn btn-success">Send</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center mt-5">
                            <p class="text-muted">
                                <i class="fas fa-shield-alt text-success"></i> 
                                Powered by Google Gemini AI | 
                                <i class="fas fa-lock text-primary"></i> 
                                Your documents are processed securely
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                let extractedText = '';

                function showStatus(message, type = 'info') {
                    const alertClass = type === 'error' ? 'danger' : type;
                    document.getElementById('status').innerHTML = 
                        `<div class="alert alert-${alertClass}">${message}</div>`;
                }

                async function uploadFile() {
                    const fileInput = document.getElementById('fileInput');
                    const file = fileInput.files[0];
                    
                    if (!file) {
                        showStatus('Please select a file first.', 'error');
                        return;
                    }
                    
                    if (!file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.docx')) {
                        showStatus('Please select a PDF or DOCX file.', 'error');
                        return;
                    }
                    
                    showStatus('<i class="fas fa-spinner fa-spin"></i> Uploading and extracting text...', 'info');
                    
                    try {
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        const response = await fetch('/api/extract', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            extractedText = result.text;
                            showStatus('✅ Text extracted successfully!', 'success');
                            document.getElementById('textContent').textContent = 
                                extractedText.substring(0, 500) + (extractedText.length > 500 ? '...' : '');
                            document.getElementById('resultsCard').style.display = 'block';
                        } else {
                            showStatus('❌ Error: ' + result.error, 'error');
                        }
                    } catch (error) {
                        showStatus('❌ Upload failed: ' + error.message, 'error');
                    }
                }

                async function analyzeRisks() {
                    if (!extractedText) return;
                    
                    showStatus('<i class="fas fa-spinner fa-spin"></i> Analyzing contract risks...', 'info');
                    
                    try {
                        const response = await fetch('/api/analyze-risks', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: extractedText })
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            displayRiskAnalysis(result.analysis);
                            showStatus('✅ Risk analysis complete!', 'success');
                        } else {
                            showStatus('❌ Analysis failed: ' + result.error, 'error');
                        }
                    } catch (error) {
                        showStatus('❌ Analysis failed: ' + error.message, 'error');
                    }
                }

                function displayRiskAnalysis(analysis) {
                    let html = '<hr><h6><i class="fas fa-shield-alt"></i> Risk Analysis Results:</h6>';
                    
                    if (analysis.raw_analysis) {
                        html += `<div class="alert alert-info"><pre style="white-space: pre-wrap; font-size: 0.9em;">${analysis.raw_analysis}</pre></div>`;
                    } else {
                        if (analysis.overall_risk_level) {
                            const levelClass = analysis.overall_risk_level.toLowerCase() === 'high' ? 'danger' : 
                                             analysis.overall_risk_level.toLowerCase() === 'medium' ? 'warning' : 'success';
                            html += `<div class="alert alert-${levelClass}"><strong>Overall Risk Level: ${analysis.overall_risk_level}</strong></div>`;
                        }
                        
                        if (analysis.key_concerns && analysis.key_concerns.length > 0) {
                            html += '<div class="alert alert-warning"><h6>Key Concerns:</h6><ul class="mb-0">';
                            analysis.key_concerns.forEach(concern => {
                                html += `<li>${concern}</li>`;
                            });
                            html += '</ul></div>';
                        }
                        
                        if (analysis.summary) {
                            html += `<div class="alert alert-info"><h6>Summary:</h6><p class="mb-0">${analysis.summary}</p></div>`;
                        }
                    }
                    
                    document.getElementById('analysisResults').innerHTML = html;
                    document.getElementById('analysisResults').style.display = 'block';
                }

                function startChat() {
                    document.getElementById('chatInterface').style.display = 'block';
                    document.getElementById('chatMessages').innerHTML = 
                        '<div class="alert alert-info"><i class="fas fa-robot"></i> Hello! I\'ve analyzed your document. What would you like to know?</div>';
                    document.getElementById('chatInput').focus();
                }

                async function sendMessage() {
                    const input = document.getElementById('chatInput');
                    const question = input.value.trim();
                    
                    if (!question) return;
                    
                    addChatMessage(question, 'user');
                    input.value = '';
                    
                    const thinkingMsg = addChatMessage('<i class="fas fa-spinner fa-spin"></i> Thinking...', 'ai');
                    
                    try {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: extractedText, question: question })
                        });
                        
                        const result = await response.json();
                        
                        thinkingMsg.remove();
                        
                        if (response.ok) {
                            addChatMessage(result.answer, 'ai');
                        } else {
                            addChatMessage('❌ ' + result.error, 'ai');
                        }
                    } catch (error) {
                        thinkingMsg.remove();
                        addChatMessage('❌ Error: ' + error.message, 'ai');
                    }
                }

                function addChatMessage(content, sender) {
                    const chatMessages = document.getElementById('chatMessages');
                    const isUser = sender === 'user';
                    const bgClass = isUser ? 'bg-light' : 'bg-primary text-white';
                    const icon = isUser ? '👤' : '🤖';
                    
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `mb-2 p-2 rounded ${bgClass}`;
                    messageDiv.innerHTML = `<strong>${icon} ${isUser ? 'You' : 'AI'}:</strong><br>${content}`;
                    
                    chatMessages.appendChild(messageDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    
                    return messageDiv;
                }

                // Allow enter key to send message
                document.addEventListener('DOMContentLoaded', function() {
                    document.getElementById('chatInput').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            sendMessage();
                        }
                    });
                });
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode('utf-8'))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        # Simple fallback HTML
        return HTMLResponse("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>contracts.ai</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <div class="row">
                    <div class="col-12">
                        <h1 class="text-center mb-4">
                            <i class="fas fa-robot text-primary"></i> contracts.ai
                        </h1>
                        <p class="text-center text-muted mb-4">Contract Risk Analysis & Document Chat with AI</p>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mx-auto">
                        <div class="card">
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
                                    <div class="border p-2" style="max-height: 150px; overflow-y: auto;">
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
                        
                        <div class="card mt-3">
                            <div class="card-header">
                                <h5><i class="fas fa-comments"></i> Chat with Document</h5>
                            </div>
                            <div class="card-body">
                                <div id="chatMessages" style="height: 300px; overflow-y: auto; border: 1px solid #dee2e6; padding: 1rem; margin-bottom: 1rem;">
                                    <div class="alert alert-info">
                                        <i class="fas fa-info-circle"></i> Upload a document to start chatting.
                                    </div>
                                </div>
                                <div id="chatInputSection" style="display: none;">
                                    <form id="chatForm">
                                        <div class="input-group">
                                            <input type="text" id="chatInput" class="form-control" placeholder="Ask a question...">
                                            <button type="submit" class="btn btn-success">
                                                <i class="fas fa-paper-plane"></i>
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                        
                        <div id="riskAnalysisResults" class="card mt-3" style="display: none;">
                            <div class="card-header">
                                <h5><i class="fas fa-shield-alt"></i> Risk Analysis Results</h5>
                            </div>
                            <div class="card-body">
                                <div id="riskAnalysisContent"></div>
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
                const chatInputSection = document.getElementById('chatInputSection');
                const riskAnalysisSection = document.getElementById('riskAnalysisSection');
                const analyzeRisksBtn = document.getElementById('analyzeRisksBtn');
                const riskAnalysisResults = document.getElementById('riskAnalysisResults');
                const riskAnalysisContent = document.getElementById('riskAnalysisContent');

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
                    showStatus('Extracting text...', 'info');
                    
                    try {
                        const response = await fetch('/extract', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            extractedText = result.text;
                            showStatus('✅ Text extracted successfully!', 'success');
                            extractedTextEl.textContent = extractedText.substring(0, 300) + '...';
                            textPreview.style.display = 'block';
                            enableChat();
                            riskAnalysisSection.style.display = 'block';
                        } else {
                            showStatus('❌ Error: ' + result.error, 'danger');
                        }
                    } catch (error) {
                        showStatus('❌ Upload failed: ' + error.message, 'danger');
                    }
                });

                chatForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const question = chatInput.value.trim();
                    if (!question) return;
                    
                    addMessage(question, 'user');
                    chatInput.value = '';
                    
                    const thinkingId = addMessage('🤔 AI is thinking...', 'ai');
                    
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
                            addMessage('❌ ' + result.error, 'ai');
                        }
                    } catch (error) {
                        document.getElementById(thinkingId).remove();
                        addMessage('❌ Error: ' + error.message, 'ai');
                    }
                });

                analyzeRisksBtn.addEventListener('click', async () => {
                    if (!extractedText) return;
                    
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
                        } else {
                            showStatus('❌ ' + result.error, 'danger');
                        }
                    } catch (error) {
                        showStatus('❌ Error: ' + error.message, 'danger');
                    }
                    
                    analyzeRisksBtn.disabled = false;
                    analyzeRisksBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Analyze Contract Risks';
                });

                function showStatus(message, type) {
                    uploadStatus.innerHTML = '<div class="alert alert-' + type + '">' + message + '</div>';
                }

                function enableChat() {
                    chatMessages.innerHTML = '<div class="alert alert-success">✅ Document loaded! Ask questions below.</div>';
                    chatInputSection.style.display = 'block';
                }

                function addMessage(content, sender) {
                    const messageId = 'msg-' + Date.now();
                    const isUser = sender === 'user';
                    const bgClass = isUser ? 'bg-light' : 'bg-primary text-white';
                    
                    const messageHtml = '<div id="' + messageId + '" class="mb-2 p-2 rounded ' + bgClass + '">' +
                        '<strong>' + (isUser ? '👤 You:' : '🤖 AI:') + '</strong><br>' + content + '</div>';
                    
                    chatMessages.insertAdjacentHTML('beforeend', messageHtml);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    return messageId;
                }

                function displayRiskAnalysis(analysis) {
                    let html = '';
                    if (analysis.raw_analysis) {
                        html = '<div class="alert alert-info"><h6>Risk Analysis:</h6><pre>' + analysis.raw_analysis + '</pre></div>';
                    } else {
                        html = '<div class="alert alert-warning"><h6>Overall Risk: ' + (analysis.overall_risk_level || 'Unknown') + '</h6></div>';
                        
                        if (analysis.key_concerns && analysis.key_concerns.length > 0) {
                            html += '<div class="alert alert-danger"><h6>Key Concerns:</h6><ul>';
                            analysis.key_concerns.forEach(concern => {
                                html += '<li>' + concern + '</li>';
                            });
                            html += '</ul></div>';
                        }
                        
                        if (analysis.summary) {
                            html += '<div class="alert alert-info"><h6>Summary:</h6><p>' + analysis.summary + '</p></div>';
                        }
                    }
                    riskAnalysisContent.innerHTML = html;
                }
            </script>
        </body>
        </html>
        ")

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
from mangum import Mangum

handler = Mangum(app)