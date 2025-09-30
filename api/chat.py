from http.server import BaseHTTPRequestHandler
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            if not GEMINI_API_KEY:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Gemini API key not configured"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            text = data.get('text', '')
            question = data.get('question', '')
            
            if not text or not question:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Missing text or question"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            prompt = f"""You are an expert document assistant. Here is the extracted document data:

{text}

User question: {question}

Please provide a helpful, accurate, and detailed answer based on the document content."""

            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            response_obj = model.generate_content(prompt)
            answer = response_obj.text if hasattr(response_obj, 'text') else str(response_obj)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"answer": answer}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_message = str(e)
            
            # Handle specific API errors
            status_code = 500
            if "429" in error_message or "quota" in error_message.lower() or "rate limit" in error_message.lower():
                status_code = 429
                error_message = "🚫 API Rate Limit Exceeded: You've reached the free tier limit for Gemini API. Please wait a few minutes before trying again."
            elif "401" in error_message or "unauthorized" in error_message.lower():
                status_code = 401
                error_message = "🔑 API Key Error: Please check that your Gemini API key is valid and properly configured."
            elif "403" in error_message or "forbidden" in error_message.lower():
                status_code = 403
                error_message = "🚫 API Access Denied: Your API key may not have permission to access the Gemini API."
            else:
                error_message = f"🤖 AI Error: {error_message}"
            
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": error_message}
            self.wfile.write(json.dumps(response).encode())
