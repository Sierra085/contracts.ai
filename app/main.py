import streamlit as st
import pandas as pd
import tempfile
import os
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("⚠️ GEMINI_API_KEY not found in .env file. Please check your configuration.")
    st.stop()

st.set_page_config(page_title="AI Reader", layout="wide")
st.title("🤖 AI Reader: Extract & Chat with Documents")

# Initialize session state for chat
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# File upload section
st.header("📄 Document Upload")
uploaded_file = st.file_uploader("Upload a PDF or Word file", type=["pdf", "docx"])

@st.cache_data
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_pdf_ocr(file):
    images = []
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp.flush()
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(tmp.name)
        except Exception as e:
            st.error(f"Error converting PDF to images: {e}")
            os.unlink(tmp.name)
            return ""
    text = ""
    for img in images:
        # Convert to RGB just in case
        if img.mode != "RGB":
            img = img.convert("RGB")
        try:
            text += pytesseract.image_to_string(img)
        except Exception as e:
            st.error(f"OCR error: {e}")
    os.unlink(tmp.name)
    return text

@st.cache_data
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def text_to_dataframe_with_header(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return pd.DataFrame()
    st.write("Preview of extracted lines:")
    for idx, line in enumerate(lines[:10]):
        st.write(f"{idx+1}: {line}")
    header_idx = st.number_input(
        "Select the line number to use as header (1-based)", min_value=1, max_value=len(lines), value=1, step=1
    ) - 1
    header = lines[header_idx]
    delimiter = st.selectbox(
        "Select delimiter to split columns:", ["\t (tab)", ", (comma)", "; (semicolon)", "| (pipe)", "Space (auto)"]
    )
    if delimiter.startswith("\t"):
        delim = "\t"
    elif delimiter.startswith(","):
        delim = ","
    elif delimiter.startswith(";"):
        delim = ";"
    elif delimiter.startswith("|"):
        delim = "|"
    else:
        delim = None
    if delim:
        columns = [h.strip() for h in header.split(delim)]
        data = [l.split(delim) for i, l in enumerate(lines) if i != header_idx]
    else:
        # Auto split on whitespace
        columns = [h.strip() for h in header.split()]
        data = [l.split() for i, l in enumerate(lines) if i != header_idx]
    df = pd.DataFrame(data, columns=columns)
    return df

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    
    with st.spinner("Extracting text from document..."):
        if file_type == "pdf":
            try:
                text = extract_text_from_pdf(uploaded_file)
                if not text.strip():
                    uploaded_file.seek(0)
                    text = extract_text_from_pdf_ocr(uploaded_file)
            except Exception:
                uploaded_file.seek(0)
                text = extract_text_from_pdf_ocr(uploaded_file)
        elif file_type == "docx":
            text = extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()
    
    # Store extracted text in session state
    st.session_state.extracted_text = text
    
    # Display success message
    st.success(f"✅ Successfully extracted text from {uploaded_file.name}")
    
    # Show extracted text in an expandable section
    with st.expander("📄 View Extracted Text", expanded=False):
        st.text_area("Extracted Text", text, height=300, key="extracted_text_display")

# AI Chat Section
if st.session_state.extracted_text:
    st.header("💬 Chat with Your Document")
    
    # Display chat history
    for i, (question, answer) in enumerate(st.session_state.chat_history):
        with st.container():
            st.markdown(f"**👤 You:** {question}")
            st.markdown(f"**🤖 AI:** {answer}")
            st.markdown("---")
    
    # Chat input
    question = st.text_input("Ask a question about your document:", 
                           placeholder="e.g., What is the main topic? Summarize the key points...")
    
    if st.button("🚀 Ask AI", type="primary"):
        if question.strip():
            with st.spinner("AI is analyzing your document..."):
                try:
                    # Create prompt for Gemini
                    prompt = f"""You are an expert document assistant. Here is the extracted document data:

{st.session_state.extracted_text}

User question: {question}

Please provide a helpful, accurate, and detailed answer based on the document content."""

                    # Generate response using Gemini
                    model = genai.GenerativeModel("gemini-1.5-flash-latest")
                    response = model.generate_content(prompt)
                    answer = response.text if hasattr(response, 'text') else str(response)
                    
                    # Add to chat history
                    st.session_state.chat_history.append((question, answer))
                    
                    # Rerun to show the new chat
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error getting AI response: {str(e)}")
        else:
            st.warning("Please enter a question.")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

else:
    st.info("👆 Please upload a document above to start chatting with AI about its contents.")

# Data extraction section (optional)
if st.session_state.extracted_text:
    with st.expander("📊 Extract Data as Table (Optional)", expanded=False):
        df = text_to_dataframe_with_header(st.session_state.extracted_text)
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No tabular data detected in the document.")

