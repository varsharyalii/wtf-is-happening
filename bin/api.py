"""
FastAPI Backend - The API that powers the chat interface

This is the backend that the React frontend talks to. It handles:
- Receiving questions from users
- Searching through podcast transcripts
- Generating answers with AI
- Sending back results with sources

Why FastAPI? It's fast, has automatic API docs, and handles async stuff well.
Plus it validates requests automatically (no bad data gets through).
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio

from src.query_service import create_query_service


# Initialize FastAPI app
app = FastAPI(
    title="WTF Podcast RAG API",
    description="Query podcast transcripts with natural language",
    version="1.0.0"
)

# CORS middleware - lets the frontend talk to us from a different port
# Without this, browsers block the requests (security thing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (default)
        "http://localhost:8080",  # Vite alternate port
        "http://localhost:3000",  # Another common dev port
        "https://*.vercel.app",   # Vercel deployments
        "https://vercel.app",     # Vercel preview
        "*"  # Allow all origins for MVP (tighten this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Global query service - we create this once when the app starts
# (Creating it for every request would be super slow)
query_service = None


@app.on_event("startup")
async def startup_event():
    """
    Initialize the RAG system when the server starts up.
    
    This loads the vector database, embedding model, etc.
    Takes a few seconds, but only happens once.
    """
    global query_service
    try:
        query_service = create_query_service(
            provider="groq",
            model="llama-3.3-70b-versatile",
            use_conversation_memory=True  # Enable conversation memory
        )
        print("✅ RAG service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG service: {e}")
        raise


# Pydantic models - these define what data looks like
# FastAPI uses these to automatically validate requests and generate docs

class QueryRequest(BaseModel):
    """What the frontend sends us when asking a question."""
    question: str               # The actual question
    top_k: int = 3             # How many relevant chunks to find (default: 3)
    diversity: bool = True     # Try to get results from different episodes


class Source(BaseModel):
    """Information about where an answer came from."""
    guest: str                 # Who said it (e.g., "Sam Altman")
    guest_expertise: str       # What they're known for
    episode_id: str            # Which episode
    youtube_url: str           # Link to the video
    text: str                  # The actual text snippet
    industry_tags: List[str]   # What topics it covers
    episode_themes: List[str]  # Episode themes
    score: float              # How relevant it is (0-1)
    is_primary: bool = False  # Whether this is the featured/primary source


class QueryResponse(BaseModel):
    """What we send back to the frontend."""
    answer: str                # The AI-generated answer
    sources: List[Source]      # Where the answer came from
    query: str                 # Echo back the question


class HealthResponse(BaseModel):
    """System health info - is everything working?"""
    status: str               # "healthy" or "unhealthy"
    message: str              # Human-readable status
    episodes_loaded: int      # How many episodes we have
    total_chunks: int         # How many chunks in the database
    model: str               # Which LLM we're using


# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API info."""
    return {
        "name": "WTF Podcast RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if query_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Get actual counts from the vector store
    vector_store = query_service.retriever.vector_store
    collection_info = vector_store.client.get_collection("wtf_podcast")
    total_chunks = collection_info.points_count
    
    # Count unique episodes from the vector store
    scroll_result = vector_store.client.scroll(
        collection_name="wtf_podcast",
        limit=1000,
        with_payload=True
    )
    unique_episodes = len(set(point.payload.get("episode_id") for point in scroll_result[0]))
    
    return HealthResponse(
        status="healthy",
        message="RAG system is operational",
        episodes_loaded=unique_episodes,
        total_chunks=total_chunks,
        model="llama-3.3-70b-versatile (Groq)"
    )


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with a question.
    
    Returns the answer and sources.
    """
    if query_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Query the service
        response = query_service.query(
            question=request.question,
            top_k=request.top_k,
            diversity=request.diversity
        )
        
        # Only return the primary source (highest scoring one)
        sources = []
        if response.sources and response.retrieval_scores:
            source_dict = response.sources[0]
            score = response.retrieval_scores[0]
            sources.append(Source(
                guest=source_dict.get("guest", "Unknown"),
                guest_expertise=source_dict.get("guest_expertise", ""),
                episode_id=source_dict.get("episode_id", ""),
                youtube_url=source_dict.get("youtube_url", ""),
                text=source_dict.get("text", ""),
                industry_tags=source_dict.get("industry_tags", []),
                episode_themes=source_dict.get("episode_themes", []),
                score=score,
                is_primary=True  # This is the featured source
            ))
        
        return QueryResponse(
            answer=response.answer,
            sources=sources,
            query=response.query
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/query/stream")
async def query_rag_stream(request: QueryRequest):
    """
    Query the RAG system with streaming response.
    
    Returns Server-Sent Events (SSE) for real-time streaming.
    """
    if query_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    async def event_generator():
        """Generate SSE events for streaming response."""
        try:
            # Stream the answer
            for chunk in query_service.query_stream(
                question=request.question,
                top_k=request.top_k,
                diversity=request.diversity
            ):
                # Send text chunk
                yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
                await asyncio.sleep(0)  # Allow other tasks to run
            
            # After streaming is complete, send sources
            # (We need to query again to get sources - optimization opportunity)
            response = query_service.query(
                question=request.question,
                top_k=request.top_k,
                diversity=request.diversity
            )
            
            # Only return the primary source
            sources_data = []
            if response.sources and response.retrieval_scores:
                source_dict = response.sources[0]
                score = response.retrieval_scores[0]
                sources_data.append({
                    "guest": source_dict.get("guest", "Unknown"),
                    "guest_expertise": source_dict.get("guest_expertise", ""),
                    "episode_id": source_dict.get("episode_id", ""),
                    "youtube_url": source_dict.get("youtube_url", ""),
                    "text": source_dict.get("text", ""),
                    "industry_tags": source_dict.get("industry_tags", []),
                    "episode_themes": source_dict.get("episode_themes", []),
                    "score": score,
                    "is_primary": True
                })
            
            # Send sources
            yield f"data: {json.dumps({'type': 'sources', 'content': sources_data})}\n\n"
            
            # Send done signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    if query_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return {
        "episodes": 6,
        "total_chunks": 210,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "llm_model": "llama-3.3-70b-versatile",
        "llm_provider": "Groq",
        "vector_db": "Qdrant (local)",
        "guests": [
            "Dara Khosrowshahi",
            "Sam Altman",
            "Neal Mohan",
            "Bill Gates",
            "Yann LeCun",
            "Nikesh Arora"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    
    print("🚀 Starting WTF Podcast RAG API")
    print(f"📚 Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health check: http://localhost:{port}/health")
    print(f"💬 Query endpoint: http://localhost:{port}/query")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

