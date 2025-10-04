.PHONY: setup ingest run test clean reset help

help:
	@echo "🎙️  WTF Podcast RAG System - Quick Commands"
	@echo ""
	@echo "First time setup:"
	@echo "  make setup    - Install everything (creates venv, installs packages)"
	@echo ""
	@echo "Regular use:"
	@echo "  make ingest   - Load podcast episodes into database (run once)"
	@echo "  make run      - Start the Streamlit chat interface"
	@echo "  make api      - Start the FastAPI backend (for React frontend)"
	@echo "  make test     - Run the test suite"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean    - Remove build artifacts and logs"
	@echo "  make reset    - Nuclear option: delete everything and start over"

setup:
	@echo "🔧 Setting up environment..."
	@echo "   (This will take a minute...)"
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env; echo "📝 Created .env file"; fi
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "⚡ Next steps:"
	@echo "   1. Edit .env and add your GROQ_API_KEY (free at https://console.groq.com)"
	@echo "   2. Run: make ingest   (loads the podcasts)"
	@echo "   3. Run: make api      (starts the backend)"
	@echo "   4. In another terminal, cd frontend && npm run dev"
	@echo ""

ingest:
	@echo "📥 Ingesting episodes..."
	./venv/bin/python bin/ingest.py
	@echo "✓ Ingestion complete!"

run:
	@echo "🚀 Starting Streamlit app..."
	./venv/bin/streamlit run bin/app.py

api:
	@echo "🚀 Starting FastAPI backend..."
	./venv/bin/python bin/api.py

test:
	@echo "🧪 Running tests..."
	./venv/bin/pytest tests/ -v

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf qdrant_storage
	rm -rf logs/*.log
	@echo "✓ Clean complete!"

reset: clean
	@echo "⚠️  Resetting everything..."
	rm -rf venv
	rm -f .env
	@echo "✓ Reset complete. Run 'make setup' to start fresh"

