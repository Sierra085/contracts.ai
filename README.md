# 🤖 contracts.ai - AI-Powered Contract Risk Analysis

**A sophisticated web application for analyzing contract risks using AI technology**

![contracts.ai](https://img.shields.io/badge/contracts.ai-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-yellow)

## 🌟 Features

### 📄 **Document Processing**
- **Multi-format Support**: Upload PDF and DOCX files
- **OCR Technology**: Fallback text extraction using Tesseract OCR
- **Real-time Progress**: Visual progress bars during processing

### ⚠️ **Risk Analysis**
- **6 Risk Categories**: Financial, Performance, Legal/Compliance, Operational, Reputation, and IP risks
- **AI-Powered Analysis**: Uses Google Gemini AI for comprehensive contract assessment
- **Structured Output**: Detailed risk levels, specific clauses, and actionable recommendations

### 💬 **Interactive Chat**
- **Document Q&A**: Ask questions about uploaded contracts
- **Context-Aware**: AI understands your document content
- **Real-time Responses**: Instant answers powered by Gemini AI

### 📊 **Export & Reporting**
- **PDF Export**: Generate professional risk analysis reports
- **Comprehensive Reports**: Include all risk categories, recommendations, and summaries
- **Professional Formatting**: Clean, structured PDF output

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works on desktop and mobile devices
- **Progress Tracking**: Visual feedback for all operations
- **Professional Interface**: Clean, intuitive design with Bootstrap styling

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key
- Tesseract OCR (for PDF processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sierra085/contracts.ai.git
   cd contracts.ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application**
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
   ```

6. **Open in browser**
   ```
   http://127.0.0.1:8001
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### Getting a Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## 📁 Project Structure

```
contracts.ai/
├── backend/
│   └── main.py              # FastAPI server and API endpoints
├── static/
│   ├── app.js              # Frontend JavaScript logic
│   └── style.css           # Custom CSS styles
├── templates/
│   └── index.html          # Main HTML template
├── app/
│   └── main.py             # Alternative Streamlit version
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **AI Engine**: Google Gemini API
- **Document Processing**: PyPDF2, python-docx, Tesseract OCR
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **PDF Generation**: jsPDF
- **Development**: Uvicorn, Auto-reload

## 📊 Risk Categories

contracts.ai analyzes contracts across 6 key risk areas:

1. **💰 Financial Risk**: Payment terms, penalties, liability caps
2. **⚡ Performance Risk**: Delivery obligations, service levels, warranties
3. **⚖️ Legal/Compliance Risk**: Regulatory requirements, indemnification
4. **🔧 Operational Risk**: Termination clauses, force majeure, data security
5. **🏆 Reputation Risk**: Confidentiality, non-disparagement, publicity
6. **🔬 IP Risk**: Intellectual property ownership, licensing, infringement

## 🎯 Usage Examples

### 1. Upload a Contract
- Drag and drop or select PDF/DOCX files
- Watch the progress bar during text extraction
- View extracted text preview

### 2. Analyze Risks
- Click "Analyze Contract Risks"
- See detailed progress through analysis phases
- Review comprehensive risk assessment

### 3. Export Results
- Click "Export PDF" in the risk analysis header
- Download professional risk analysis report
- Share or archive results

### 4. Chat with Documents
- Ask questions about contract content
- Get AI-powered answers and insights
- Clear chat history as needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- **API Costs**: Google Gemini API usage may incur costs based on your usage
- **Rate Limits**: Free tier has rate limits; consider upgrading for production use
- **Data Privacy**: Documents are processed temporarily and not stored permanently
- **Dependencies**: Ensure Tesseract OCR is installed for PDF fallback processing

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/Sierra085/contracts.ai/issues) page
2. Review the troubleshooting section below
3. Create a new issue with detailed information

### Common Issues

- **Tesseract not found**: Install Tesseract OCR for your system
- **API key errors**: Verify your Gemini API key in `.env`
- **Port conflicts**: Change the port in the uvicorn command
- **Permission errors**: Ensure proper file permissions

## 🎉 Acknowledgments

- Google Gemini AI for powerful language processing
- FastAPI for the excellent web framework
- Bootstrap for responsive UI components
- The open-source community for amazing libraries

---

**Built with ❤️ by Sierra085**

*Transform your contract analysis workflow with AI-powered insights*
