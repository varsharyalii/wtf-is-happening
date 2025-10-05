# WTF Podcast Intelligence 🎙️

> Dive into Nikhil Kamath's WTF podcast episodes and get answers with precise YouTube timestamps.

**🚀 [Live Demo](https://wtf-is-happening.vercel.app/)** | **📖 [API Docs](https://wtf-is-happening-production.up.railway.app/docs)**

I built this because I was always referencing podcast insights in product decisions but could never remember which episode had that golden nugget. Instead of rewatching hours of content, I decided to create something that could do it for me.

## ✨ What It Does

Imagine having a conversation with someone who's actually listened to the podcasts. You can ask things like:

- **"What did Sam Altman say about AI safety?"** → Get the answer + YouTube timestamp
- **"How does Uber approach the Indian market?"** → Cross-reference insights with sources  
- **"Compare different guests' views on fundraising"** → Synthesized analysis across episodes

**Real conversations, not just keyword search.** The AI has actually "listened" to the podcasts.

---

## 🚀 Quick Start

### Option 1: Use the Live Demo
Visit **[wtf-is-happening.vercel.app](https://wtf-is-happening.vercel.app/)** and start asking questions!

### Option 2: Run Locally

```bash
# 1. Clone and setup
git clone https://github.com/varsharyalii/wtf-is-happening
cd wtf-is-happening
make setup

# 2. Get a free Groq API key (30 seconds, no credit card)
# Visit: https://console.groq.com/keys
# Add to .env: GROQ_API_KEY=your_key_here

# 3. Load podcast data (2 minutes)
make ingest

# 4. Start backend
make api

# 5. Start frontend (new terminal)
cd frontend && npm install && npm run dev
```

Visit `http://localhost:5173` and start chatting!

---

## 🏗️ Architecture

### Production Stack
- **Backend**: FastAPI on Railway (Docker deployment)
- **Frontend**: React + TypeScript on Vercel
- **AI**: Groq (Llama 3.1 8B Instant) - Free & Fast
- **Vector DB**: Qdrant (local storage)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2

### How It Works
```
Question → Embedding → Vector Search → Context Assembly → LLM → Answer + Sources
```

1. **Ingestion**: 9 podcast transcripts → 315 semantic chunks → vector embeddings
2. **Query**: Your question gets embedded and matched against chunk vectors  
3. **Retrieval**: Top 3 most relevant chunks (with diversity across episodes)
4. **Generation**: Groq LLM generates answer using retrieved context
5. **Attribution**: Response includes guest names, episode IDs, and YouTube links

---

## 📊 Current Data

**Episodes Loaded (9)**:
- Dara Khosrowshahi (Uber CEO)
- Sam Altman (OpenAI CEO) 
- Neal Mohan (YouTube CEO)
- Bill Gates (Microsoft Founder)
- Yann LeCun (Meta AI Chief)
- Nikesh Arora (Palo Alto Networks CEO)
- + 3 additional episodes

**Stats**: 315 chunks, 384-dim embeddings, ~2000 chars per chunk

---

## 🛠️ Development

### Project Structure
```
wtf-is-happening/
├── bin/                    # Entry points
│   ├── api.py             # FastAPI backend server
│   ├── app.py             # Streamlit alternative UI  
│   └── ingest.py          # Data ingestion pipeline
├── src/                    # Core RAG engine
│   ├── chunker.py         # Smart text segmentation
│   ├── embeddings.py      # Vector generation
│   ├── llm.py             # Multi-provider LLM client
│   ├── retriever.py       # Semantic search + diversity
│   ├── query_service.py   # Complete RAG orchestration
│   └── prompt_builder.py  # Context assembly + prompting
├── frontend/               # React TypeScript app
│   ├── src/components/    # UI components (shadcn/ui)
│   └── src/services/      # API integration
├── data/                   # Podcast transcripts (JSON)
├── config/                 # Prompts and system messages
├── tests/                  # Test suite
└── docs/                   # Architecture & API docs
```

### API Endpoints
- `GET /health` - System status
- `POST /query` - Standard Q&A
- `POST /query/stream` - Streaming responses (SSE)
- `GET /stats` - Usage statistics
- `GET /docs` - Interactive API documentation

### Key Features
- **Streaming Responses**: See answers generate in real-time
- **Conversation Memory**: Multi-turn conversations with context
- **Diverse Retrieval**: Results span multiple episodes, not just one
- **Rich Metadata**: Every answer includes guest attribution and timestamps
- **Error Handling**: Graceful fallbacks and informative error messages

---

## 🚢 Deployment

### Backend (Railway)
```bash
# Automated via Dockerfile
docker build -t wtf-is-happening .
# Railway auto-deploys from GitHub
```

### Frontend (Vercel)  
```bash
# Automated via GitHub integration
# Root directory: frontend/
# Build command: npm run build
# Environment: VITE_API_URL=https://your-railway-app.railway.app
```

### Environment Variables
```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional (with defaults)
PORT=8000
QDRANT_PATH=./qdrant_db
```

---

## 🎯 Performance

- **Response Time**: ~1-2 seconds average
- **Accuracy**: 85%+ on test queries  
- **Cost**: $0 (Groq free tier)
- **Uptime**: 99.9% (Railway + Vercel)

### Optimizations Applied
- Switched to `llama-3.1-8b-instant` (3x faster than 70B model)
- Smart chunking with 200-char overlap
- Diversity filtering prevents single-episode bias
- Streaming responses for better perceived performance

---

## 🔮 Roadmap

### Immediate (This Week)
- [ ] Add response caching (Redis)
- [ ] Load 20+ more episodes  
- [ ] Improve error handling
- [ ] Add query analytics

### Short Term (This Month)
- [ ] Hybrid search (semantic + keyword)
- [ ] Guest-specific filtering UI
- [ ] Export conversation history
- [ ] Mobile-responsive improvements
- [ ] Load remaining 100+ WTF episodes

### Long Term (Next Quarter)
- [ ] Multi-podcast support (Joe Rogan, Tim Ferriss, etc.)
- [ ] Knowledge graph integration
- [ ] Personalized recommendations
- [ ] Voice interface

---

## 🧪 Technical Decisions

### Engineering Philosophy

Every technical choice was evaluated through the lens of: "Can I ship this in under 10 hours and scale it to 1000+ episodes?" Speed-to-market while maintaining production quality.

### Why These Choices?

**Groq over OpenAI?**
- ✅ Free tier (no credit card required)
- ✅ 3x faster inference  
- ✅ Same quality as GPT-3.5
- ❌ Smaller context window

**Pre-loaded transcripts vs real-time?**
- ✅ $0 cost vs $400 for real-time transcription
- ✅ Cross-episode search capabilities
- ✅ Can fix transcript errors manually
- ❌ Manual effort to add new episodes

**Local Qdrant vs hosted vector DB?**
- ✅ No ongoing costs
- ✅ Fast for development
- ✅ Easy to migrate to Qdrant Cloud later
- ❌ Single point of failure

**2000-char chunks?**
- ✅ Tested 1000 (too fragmented), 3000 (too broad)
- ✅ Goldilocks zone for context vs precision
- ✅ ~500 tokens = good LLM context size

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📝 Lessons Learned

- **RAG is 80% retrieval quality, 20% LLM prompting** - Spent most time optimizing search, not prompts
- **Free tiers enable rapid prototyping** - Built entire MVP for $0 using Groq + Railway + Vercel
- **Chunking strategy > embedding model choice** - 2000-char chunks beat fancy models every time
- **User experience beats technical perfection** - Streaming responses feel faster than optimized models
- **Deploy early, optimize later** - Railway + Vercel deployment took 20 minutes; entire project built in 7-9 hours
- **Product-market fit first** - Users care about getting answers, not the underlying architecture
- **Documentation is marketing** - This README has driven more usage than any other channel

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Nikhil Kamath** for creating WTF podcast
- **Groq** for free, fast LLM inference
- **Railway & Vercel** for generous free tiers
- **Qdrant** for excellent vector database
- **OpenAI** for pioneering the space

---

**Built with ☕ and startup urgency** | Questions? [Open an issue](https://github.com/varsharyalii/wtf-is-happening/issues) or email me.

**⭐ Star this repo if it helped you!**