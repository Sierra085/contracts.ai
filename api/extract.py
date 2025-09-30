from http.server import BaseHTTPRequestHandler
import json
import os
import tempfile
import base64
from docx import Document
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse multipart form data (simplified)
            if b'Content-Disposition: form-data; name="file"' in post_data:
                # Extract file data from multipart
                boundary = post_data.split(b'\r\n')[0]
                parts = post_data.split(boundary)
                
                for part in parts:
                    if b'filename=' in part:
                        # Extract filename and file content
                        lines = part.split(b'\r\n')
                        file_content = b'\r\n'.join(lines[4:-1])  # Remove headers and boundary
                        
                        # Determine file type from filename
                        filename_line = [line for line in lines if b'filename=' in line][0]
                        filename = filename_line.decode().split('filename="')[1].split('"')[0]
                        
                        # Save to temp file and extract text
                        suffix = os.path.splitext(filename)[-1].lower()
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(file_content)
                            tmp.flush()
                            file_path = tmp.name
                        
                        try:
                            if suffix == ".pdf":
                                text = extract_text_from_pdf(file_path)
                            elif suffix == ".docx":
                                text = extract_text_from_docx(file_path)
                            else:
                                raise ValueError("Unsupported file type")
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            response = {"text": text}
                            self.wfile.write(json.dumps(response).encode())
                            
                        except Exception as e:
                            self.send_response(500)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            response = {"error": str(e)}
                            self.wfile.write(json.dumps(response).encode())
                        finally:
                            try:
                                os.unlink(file_path)
                            except:
                                pass
                        break
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "No file uploaded"}
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())
