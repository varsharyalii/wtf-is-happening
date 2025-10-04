# WTF Podcast Chat 🎙️

> Ask questions about Nikhil Kamath's WTF podcast and get answers with exact YouTube timestamps

I built this because I kept forgetting which episode had "that one thing" someone said. Now I can just ask.

## What It Does

It's a chatbot that's actually listened to the podcasts. You can ask stuff like:
- "What did Sam Altman say about AI safety?"
- "How does Uber think about the Indian market?"
- "Compare what different guests said about fundraising"

And it gives you the answer plus the exact YouTube timestamp to watch.

## Quick Start (5 minutes)

```bash
# 1. Clone and setup
git clone <your-repo>
cd wtf-is-happening
make setup

# 2. Get a free API key from Groq (30 seconds, no credit card)
#    Visit: https://console.groq.com
#    Then add it to .env file

# 3. Load the podcasts (takes ~2 minutes)
make ingest

# 4. Start the backend
make api

# 5. In another terminal, start the frontend
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 and start asking!

## How It Works

1. I downloaded 6 podcast transcripts from YouTube
2. Broke them into chunks (about 2-3 paragraphs each)
3. Converted chunks to vectors (math representation)
4. When you ask a question, it finds the most relevant chunks
5. Sends those to an AI (Groq) which generates an answer

The fancy name is "RAG" (Retrieval-Augmented Generation) but it's just search + AI.

## Why These Choices?

**Groq instead of OpenAI?**  
- Free. Actually free. No credit card.
- Fast (responses in ~0.5 seconds)
- Good quality (uses Llama 3.3 70B)

**Pre-loaded transcripts instead of real-time?**  
- Real-time transcription costs $400 for 5 episodes
- Pre-loading is free and I can fix errors
- Enables cross-episode search

**2000 character chunks?**  
- Tested 1000 (too small, lost context)
- Tested 2000 (goldilocks zone ✓)
- Tested 3000 (too big, search got worse)

**Local Qdrant vector DB?**  
- No ongoing costs
- Fast for development
- Easy to move to cloud later

## Project Structure

```
wtf-is-happening/
├── bin/                # Entry point scripts
│   ├── api.py         # FastAPI backend
│   ├── app.py         # Streamlit UI (alternative)
│   └── ingest.py      # Load podcasts into DB
├── src/                # Core RAG logic
│   ├── chunker.py      # Break transcripts into pieces
│   ├── embeddings.py   # Convert text to vectors
│   ├── llm.py          # Talk to Groq/OpenAI
│   ├── retriever.py    # Find relevant chunks
│   └── query_service.py # Orchestrate everything
├── frontend/           # React app
├── tests/              # Tests
├── data/               # Podcast transcripts
└── docs/               # Documentation
```

## Current Limitations (Being Honest)

- **Only 6 episodes** - Need to automate downloading more
- **No caching** - Same question twice = two API calls
- **Basic search** - Could add keyword search for exact names
- **Not deployed** - Runs locally only
- **Limited tests** - Covers core logic but not everything

## What I'd Do Next

**This weekend:**
- [ ] Deploy backend (Railway)
- [ ] Deploy frontend (Vercel)
- [ ] Add caching (Redis)

**Next week:**
- [ ] Load all 100+ episodes
- [ ] Better error handling
- [ ] Query analytics

**Eventually:**
- [ ] Hybrid search (semantic + keyword)
- [ ] Multi-podcast support
- [ ] Mobile app?

## Tech Stack

- **Backend:** Python, FastAPI, Qdrant
- **Frontend:** React, TypeScript, Tailwind
- **AI:** Groq (Llama 3.3), sentence-transformers
- **Database:** Qdrant (vector database)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). TL;DR: Fork it, fix something, send a PR.

## Lessons Learned

- RAG is 80% about good retrieval, 20% about the LLM
- Free tiers are amazing (built this for $0)
- Chunking strategy matters way more than I thought
- Just ship it - can always improve later
- Comments help future you (I forgot why I did things after 2 weeks)

## License

MIT - Do whatever you want with it

---

**Built in 2 days** with ☕ and frustration over not remembering which podcast said what

Questions? Open an issue or email me.
