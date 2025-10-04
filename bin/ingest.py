#!/usr/bin/env python
"""
Ingestion Pipeline - Load podcasts into the database

This script takes podcast transcripts and prepares them for searching:
1. Loads episodes from data/episodes.json
2. Breaks them into chunks (2000 chars each)
3. Converts chunks to vectors (embeddings)
4. Stores everything in Qdrant (our vector database)

You only need to run this once, or when you add new episodes.
Takes about 2 minutes for 9 episodes.

Usage:
    python ingest.py
    or
    make ingest
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path so we can import from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chunker import TranscriptChunker, print_chunking_stats
from src.embeddings import EmbeddingGenerator, print_embedding_stats
from src.vector_store import VectorStore


def load_episodes(episodes_file: Path) -> List[Dict[str, Any]]:
    """Load episodes from JSON file."""
    if not episodes_file.exists():
        print(f"❌ Episodes file not found: {episodes_file}")
        sys.exit(1)
    
    with open(episodes_file, 'r', encoding='utf-8') as f:
        episodes = json.load(f)
    
    if not episodes:
        print("❌ No episodes found in episodes.json")
        sys.exit(1)
    
    return episodes


def main():
    """
    Main ingestion pipeline - the big kahuna.
    
    This is where all the magic happens. We load episodes, chunk them,
    create embeddings, and store everything in the database.
    """
    print("\n" + "="*80)
    print("🎙️  WTF PODCAST RAG - INGESTION PIPELINE")
    print("="*80 + "\n")
    
    # Configuration - change these if you want different settings
    EPISODES_FILE = Path("data/episodes.json")       # Where the transcripts are
    COLLECTION_NAME = "wtf_podcast"                   # Name in the database
    STORAGE_PATH = "./qdrant_db"                      # Where to save the database
    
    # Step 1: Load episodes
    print("📚 Step 1: Loading Episodes")
    print("-" * 80)
    episodes = load_episodes(EPISODES_FILE)
    print(f"✓ Loaded {len(episodes)} episodes")
    
    for ep in episodes:
        guest = ep.get("guest", "Unknown")
        ep_id = ep.get("id", "Unknown")
        transcript_len = len(ep.get("transcript", ""))
        print(f"  - {ep_id}: {guest} ({transcript_len:,} chars)")
    
    # Step 2: Chunk transcripts
    print("\n📝 Step 2: Chunking Transcripts")
    print("-" * 80)
    chunker = TranscriptChunker(
        chunk_size=2000,  # ~500 tokens
        overlap=200,      # ~50 tokens
    )
    chunks = chunker.chunk_all_episodes(episodes)
    print_chunking_stats(chunks)
    
    # Convert chunks to dicts for embedding
    chunk_dicts = [chunk.to_dict() for chunk in chunks]
    chunk_texts = [chunk.text for chunk in chunks]
    
    # Step 3: Generate embeddings
    print("🧠 Step 3: Generating Embeddings")
    print("-" * 80)
    generator = EmbeddingGenerator()
    print(f"Processing {len(chunk_texts)} chunks...")
    embeddings = generator.embed_batch(
        chunk_texts,
        batch_size=32,
        show_progress=True
    )
    print_embedding_stats(embeddings)
    
    # Step 4: Store in vector database
    print("💾 Step 4: Storing in Vector Database")
    print("-" * 80)
    vector_store = VectorStore(
        collection_name=COLLECTION_NAME,
        storage_path=STORAGE_PATH,
        embedding_dim=generator.get_embedding_dim(),
    )
    
    vector_store.add_chunks(
        chunks=chunk_dicts,
        embeddings=embeddings,
        batch_size=100,
    )
    
    # Step 5: Verify
    print("\n✅ Step 5: Verification")
    print("-" * 80)
    info = vector_store.get_collection_info()
    print(f"Collection: {COLLECTION_NAME}")
    print(f"  Total vectors: {info['vector_count']}")
    print(f"  Embedding dimension: {info['embedding_dim']}")
    print(f"  Distance metric: {info['distance_metric']}")
    
    # Quick search test
    print("\n🔍 Testing Search...")
    test_query = "Tell me about artificial intelligence and the future of technology"
    test_embedding = generator.embed_text(test_query)
    results = vector_store.search(test_embedding, limit=3)
    
    print(f"\nTest Query: '{test_query}'")
    print(f"Top Result:")
    if results:
        top_result = results[0]
        print(f"  Guest: {top_result['guest']}")
        print(f"  Score: {top_result['score']:.4f}")
        print(f"  Text: {top_result['text'][:150]}...")
    
    # Success!
    print("\n" + "="*80)
    print("🎉 INGESTION COMPLETE!")
    print("="*80)
    print("\n✓ Your podcast knowledge base is ready!")
    print(f"✓ {len(episodes)} episodes processed")
    print(f"✓ {len(chunks)} chunks created")
    print(f"✓ {info['vector_count']} vectors stored")
    print("\nNext steps:")
    print("  1. Run 'make run' to start the chat interface")
    print("  2. Try queries like:")
    print("     - 'What did Sam Altman say about AI?'")
    print("     - 'Tell me about Uber's strategy in India'")
    print("     - 'What are the key themes in these podcasts?'")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

