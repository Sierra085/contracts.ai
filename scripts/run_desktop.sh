#!/bin/bash

# Start the Desktop app
echo "Starting AI Reader Desktop App..."
echo "Make sure you have activated the virtual environment: source venv/bin/activate"
echo "Make sure the backend server is running first: ./scripts/run_backend.sh"
echo ""

# Change to project root directory
cd "$(dirname "$0")/.."

# Load environment variables and start app
source venv/bin/activate 2>/dev/null || echo "Virtual environment not found. Run ./scripts/setup_macos.sh first."
python desktop/main.py
