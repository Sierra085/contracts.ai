#!/bin/bash

# Start the FastAPI backend server
echo "Starting AI Reader Backend Server..."
echo "Make sure you have activated the virtual environment: source venv/bin/activate"
echo "Server will be available at: http://127.0.0.1:8000"
echo "API docs will be available at: http://127.0.0.1:8000/docs"
echo ""

# Change to project root directory
cd "$(dirname "$0")/.."

# Load environment variables and start server
source venv/bin/activate 2>/dev/null || echo "Virtual environment not found. Run ./scripts/setup_macos.sh first."
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
