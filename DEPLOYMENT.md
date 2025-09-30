# Vercel Deployment Instructions

This application is now ready for deployment on Vercel! Here's how to deploy it:

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push this code to a GitHub repository
3. **Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Deployment Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Deploy on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect it's a Python project
5. Configure environment variables:
   - Add `GEMINI_API_KEY` with your actual API key value

### 3. Environment Variables

In Vercel dashboard, go to:
- Project Settings → Environment Variables
- Add: `GEMINI_API_KEY` = `your_actual_api_key_here`

## Application Features

✅ **Contract Risk Analysis**: Upload PDF/DOCX contracts and get AI-powered risk assessment
✅ **Document Chat**: Ask questions about uploaded documents  
✅ **Modern UI**: Bootstrap-based responsive interface
✅ **Error Handling**: Proper API error handling and user feedback
✅ **Vercel Ready**: Optimized for serverless deployment

## Local Development

1. Clone the repository:
```bash
git clone YOUR_REPO_URL
cd contracts.ai
```

2. Set up virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Run the application:
```bash
uvicorn api.index:app --reload
```

6. Open http://localhost:8000 in your browser

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **AI**: Google Gemini API
- **Document Processing**: PyPDF2, python-docx
- **Deployment**: Vercel

## Notes

- The application includes embedded HTML/CSS/JS so it works even if static files aren't available on Vercel
- Error handling includes specific messages for API rate limits and authentication issues
- The interface is fully responsive and works on mobile devices
- File uploads are processed server-side with proper cleanup

## Support

If you encounter any issues during deployment, check:
1. Environment variables are properly set
2. Gemini API key is valid and has proper permissions
3. Repository is properly connected to Vercel

Happy deploying! 🚀
