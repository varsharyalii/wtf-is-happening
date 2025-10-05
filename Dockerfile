# Multi-stage Dockerfile for WTF Podcast RAG System
# Optimized for Railway deployment on linux/amd64

# Explicitly target linux/amd64 platform
FROM --platform=linux/amd64 python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies for compiling Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install ALL Python dependencies in builder stage (including sentence-transformers)
# This prevents the 2-3 minute runtime installation that happens in start.sh
RUN pip install --no-cache-dir --user -r requirements.txt

# Pre-download sentence-transformers model to avoid download on first run
# Use smaller cache to save space
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" && \
    rm -rf /tmp/* /var/tmp/*

# Stage 2: Runtime image
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage (models are included in .local)
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY bin/ ./bin/
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/
COPY start.sh ./start.sh

# Make start script executable
RUN chmod +x start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV QDRANT_PATH=./qdrant_db

# Create directory for vector database with proper permissions
RUN mkdir -p ./qdrant_db && chmod 755 ./qdrant_db

# Expose the port (Railway will set PORT automatically)
EXPOSE $PORT

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run startup script
CMD ["./start.sh"]