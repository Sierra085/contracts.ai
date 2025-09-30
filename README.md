# 🤖 contracts.ai - AI-Powered Contract Risk Analysis

**A sophisticated web application for analyzing contract risks using AI technology**

![contracts.ai](https://img.shields.io/badge/contracts.ai-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-yellow)
![Vercel](https://img.shields.io/badge/Deployment-Vercel-black)

## 🌟 Features

### 📄 **Document Processing**
- **Multi-format Support**: Upload PDF and DOCX files
- **Fast Text Extraction**: Efficient document processing
- **Real-time Progress**: Visual feedback during processing

### ⚠️ **Risk Analysis**
- **6 Risk Categories**: Financial, Performance, Legal/Compliance, Operational, Reputation, and IP risks
- **AI-Powered Analysis**: Uses Google Gemini AI for comprehensive contract assessment
- **Structured Output**: Detailed risk levels, specific clauses, and actionable recommendations

### 💬 **Interactive Chat**
- **Document Q&A**: Ask questions about uploaded contracts
- **Context-Aware**: AI understands your document content
- **Real-time Responses**: Instant answers powered by Gemini AI

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Professional Interface**: Clean, intuitive design with Bootstrap styling
- **Progressive Enhancement**: Works even without external dependencies

## 🚀 Quick Start

### Option 1: Deploy to Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Sierra085/contracts.ai)

1. Click the "Deploy with Vercel" button above
2. Import your GitHub repository
3. Add your `GEMINI_API_KEY` in environment variables
4. Deploy! 🎉

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sierra085/contracts.ai.git
   cd contracts.ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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
   uvicorn api.index:app --reload
   ```

6. **Open in browser**
   ```
   http://localhost:8000
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
3. Add it to your `.env` file or Vercel environment variables

## 📁 Project Structure

```
contracts.ai/
├── api/
│   └── index.py            # Main FastAPI application (Vercel-ready)
├── backend/
│   └── main.py             # Alternative backend (local development)
├── static/
│   ├── app.js              # Frontend JavaScript logic
│   └── style.css           # Custom CSS styles
├── templates/
│   └── index.html          # Main HTML template
├── app/
│   └── main.py             # Streamlit version
├── vercel.json             # Vercel configuration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── DEPLOYMENT.md          # Deployment instructions
└── README.md              # This file
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **AI Engine**: Google Gemini API
- **Document Processing**: PyPDF2, python-docx
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Deployment**: Vercel (serverless)
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
- Watch the progress during text extraction
- View extracted text preview

### 2. Analyze Risks
- Click "Analyze Contract Risks"
- Review comprehensive risk assessment
- See detailed categories and recommendations

### 3. Chat with Documents
- Ask questions about contract content
- Get AI-powered answers and insights
- Clear chat history as needed

## 🌐 Deployment

### Vercel Deployment (Recommended)

This application is optimized for Vercel deployment:

- ✅ Serverless-ready FastAPI application
- ✅ Embedded HTML/CSS/JS (no static file dependencies)
- ✅ Proper error handling for API limits
- ✅ Environment variable configuration
- ✅ Automatic Python runtime detection

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step deployment instructions.

### Other Deployment Options

- **Heroku**: Use `Procfile` with `web: uvicorn api.index:app --host=0.0.0.0 --port=${PORT:-5000}`
- **Railway**: Works out of the box with the current setup
- **DigitalOcean App Platform**: Deploy directly from GitHub
- **AWS Lambda**: Use Mangum adapter for ASGI compatibility

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
- **Rate Limits**: Free tier has rate limits; the app handles these gracefully
- **Data Privacy**: Documents are processed temporarily and not stored permanently
- **Vercel Limits**: Be aware of Vercel's function execution time limits for large documents

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/Sierra085/contracts.ai/issues) page
2. Review the troubleshooting section below
3. Create a new issue with detailed information

### Common Issues

- **API key errors**: Verify your Gemini API key in environment variables
- **Rate limit errors**: Wait a few minutes if you hit API limits
- **Large file uploads**: Vercel has file size limits for uploads
- **Function timeouts**: Large documents may take time to process

## 🎉 Acknowledgments

- Google Gemini AI for powerful language processing
- FastAPI for the excellent web framework
- Bootstrap for responsive UI components
- Vercel for seamless deployment platform
- The open-source community for amazing libraries

---

**Built with ❤️ by Sierra085**

*Transform your contract analysis workflow with AI-powered insights*

**🚀 Ready to deploy? [Click here to deploy to Vercel](https://vercel.com/new/clone?repository-url=https://github.com/Sierra085/contracts.ai)**
