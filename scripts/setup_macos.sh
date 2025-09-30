#!/bin/bash

# macOS Setup Script for AI Reader
echo "Setting up AI Reader for macOS..."

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Tesseract for OCR functionality
echo "Installing Tesseract..."
brew install tesseract

# Install Poppler for PDF to image conversion
echo "Installing Poppler..."
brew install poppler

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment template
if [ ! -f ../.env ]; then
    echo "Creating .env file from template..."
    cp ../.env.example ../.env
    echo "⚠️  Please edit .env file and add your Gemini API key!"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Gemini API key"
echo "2. To activate the virtual environment: source venv/bin/activate"
echo "3. To run the backend: ./scripts/run_backend.sh"
echo "4. To run the Streamlit app: ./scripts/run_streamlit.sh"
echo "5. To run the desktop app: ./scripts/run_desktop.sh"
