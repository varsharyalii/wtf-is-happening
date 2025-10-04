# 🚀 FastAPI Backend - Complete Setup Guide

## ✅ What We Built

A **production-ready REST API** for your React frontend to query the WTF Podcast RAG system.

### Files Created:
- **`api.py`**: FastAPI backend with REST endpoints
- **`frontend/README.md`**: Integration guide for your Lovable app

---

## 📦 Architecture

```
React Frontend (Lovable)     →     FastAPI Backend     →     RAG System
   http://localhost:5173            http://localhost:8000        (Groq + Qdrant)
```

---

## 🎯 API Endpoints

### 1. `POST /query` - Standard Query
**Request:**
```json
{
  "question": "What did Sam Altman say about AI?",
  "top_k": 5,
  "diversity": true
}
```

**Response:**
```json
{
  "answer": "Sam Altman discussed...",
  "sources": [
    {
      "guest": "Sam Altman",
      "guest_expertise": "CEO, OpenAI",
      "episode_id": "ep_SfOaZIGJ",
      "youtube_url": "https://youtube.com/watch?v=...",
      "text": "...",
      "industry_tags": ["AI", "technology"],
      "episode_themes": ["innovation"],
      "score": 0.87
    }
  ],
  "query": "What did Sam Altman say about AI?"
}
```

### 2. `POST /query/stream` - Streaming Response
Returns Server-Sent Events for real-time token streaming.

### 3. `GET /health` - Health Check
```json
{
  "status": "healthy",
  "episodes_loaded": 6,
  "total_chunks": 210,
  "model": "llama-3.3-70b-versatile (Groq)"
}
```

### 4. `GET /stats` - System Statistics
Returns info about loaded episodes, models, guests, etc.

---

## 🏃 Quick Start

### 1. Start the Backend

```bash
# From wtf-is-happening/
./venv/bin/python api.py
```

API runs at: http://localhost:8000  
Docs at: http://localhost:8000/docs

### 2. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What did Sam Altman say about AI?"}'
```

### 3. Connect Your React Frontend

In your Lovable project, create a service file:

```typescript
// src/services/api.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface QueryRequest {
  question: string;
  top_k?: number;
  diversity?: boolean;
}

export interface Source {
  guest: string;
  guest_expertise: string;
  episode_id: string;
  youtube_url: string;
  text: string;
  industry_tags: string[];
  episode_themes: string[];
  score: number;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
  query: string;
}

export async function queryPodcast(
  question: string, 
  top_k: number = 5
): Promise<QueryResponse> {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k, diversity: true })
  });
  
  if (!response.ok) {
    throw new Error('Query failed');
  }
  
  return response.json();
}

// For streaming (optional)
export function queryPodcastStream(
  question: string,
  onChunk: (chunk: string) => void,
  onSources: (sources: Source[]) => void
) {
  const eventSource = new EventSource(
    `${API_URL}/query/stream?question=${encodeURIComponent(question)}`
  );
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'text') {
      onChunk(data.content);
    } else if (data.type === 'sources') {
      onSources(data.content);
      eventSource.close();
    }
  };
  
  return eventSource;
}
```

### 4. Use in Your React Components

```typescript
// Example component
import { useState } from 'react';
import { queryPodcast, QueryResponse } from './services/api';

function Chat() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await queryPodcast(question);
      setResponse(result);
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about the podcasts..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </form>

      {response && (
        <div>
          <p>{response.answer}</p>
          
          <h3>Sources:</h3>
          {response.sources.map((source, i) => (
            <div key={i}>
              <strong>{source.guest}</strong> - {source.guest_expertise}
              <br />
              <a href={source.youtube_url} target="_blank">Watch Episode</a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 🚀 Deployment

### Backend (Railway/Render)

1. **Push to GitHub** (this repo)
2. **Connect to Railway/Render**
3. **Set environment variable:**
   ```
   GROQ_API_KEY=your_key_here
   ```
4. **Deploy command:**
   ```
   python api.py
   ```

### Frontend (Vercel - Auto)

Your Lovable repo already auto-deploys to Vercel!

1. **Set environment variable in Vercel:**
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```
2. **Redeploy** - done!

---

## 🐛 Troubleshooting

### CORS Errors
Add your frontend URL to `api.py`:
```python
allow_origins=[
    "https://your-app.vercel.app",
]
```

### Database Lock
Only run **either** Streamlit OR API, not both (they share Qdrant).

### Groq API Key
Make sure `.env` file has:
```
GROQ_API_KEY=your_key_here
```

---

## 📚 Next Steps

1. Copy your Lovable repo into `frontend/`
2. Integrate the API service
3. Test locally
4. Deploy both separately
5. Enjoy your production RAG system!

**Questions?** Check `/docs` endpoint for interactive API documentation.

