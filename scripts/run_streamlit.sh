#!/bin/bash

# Start the Streamlit web app
echo "Starting AI Reader Web App..."
echo "Make sure you have activated the virtual environment: source venv/bin/activate"
echo "App will be available at: http://localhost:8501"
echo ""

# Change to project root directory
cd "$(dirname "$0")/.."

# Load environment variables and start app
source venv/bin/activate 2>/dev/null || echo "Virtual environment not found. Run ./scripts/setup_macos.sh first."
streamlit run app/main.py
