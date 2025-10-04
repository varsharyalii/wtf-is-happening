#!/bin/bash
# Startup script for Railway deployment

echo "🚀 Starting WTF Podcast RAG API..."

# Run ingestion first (to populate vector DB)
echo "📊 Running data ingestion..."
python bin/ingest.py

# Start the API server
echo "🌐 Starting API server..."
python bin/api.py

