# 🚀 Quick Start Guide

## Your Lovable UI + FastAPI Backend

Everything is integrated and ready to test!

### ✅ What's Done:
- ✅ API service created (`src/services/api.ts`)
- ✅ Index page updated with real API calls
- ✅ Sources display with YouTube links
- ✅ Error handling
- ✅ Beautiful UI preserved

### 🏃 Run Locally

**Terminal 1 - Backend:**
```bash
cd /Users/varsha.ryali/wtf-is-happening
./venv/bin/python api.py
```
API at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd /Users/varsha.ryali/wtf-is-happening/frontend-integration
npm install
npm run dev
```
Frontend at: http://localhost:5173

### 🧪 Test It:
1. Open http://localhost:5173
2. Ask: "What did Sam Altman say about AI?"
3. See real answers + sources!

### 🚀 Deploy:
- Backend → Railway/Render (set `GROQ_API_KEY`)
- Frontend → Push to your Lovable repo (auto-deploys to Vercel)

