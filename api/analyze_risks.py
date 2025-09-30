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
            
            if not text:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Missing document text"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            prompt = f"""You are an expert legal analyst specializing in contract risk assessment. Analyze the following contract document and identify potential risk factors.

Contract Document:
{text}

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
            response_obj = model.generate_content(prompt)
            answer = response_obj.text if hasattr(response_obj, 'text') else str(response_obj)
            
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
                analysis = parsed_response
            except json.JSONDecodeError:
                # If JSON parsing fails, return as structured text
                analysis = {"raw_analysis": answer}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"analysis": analysis}
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