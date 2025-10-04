"""
Retrieval System for RAG

Handles semantic search with optional metadata filtering.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.vector_store import VectorStore
from src.embeddings import EmbeddingGenerator


@dataclass
class RetrievalResult:
    """A single retrieval result with metadata."""
    text: str
    score: float
    guest: str
    episode_id: str
    youtube_url: str
    chunk_index: int
    guest_expertise: str
    industry_tags: List[str]
    episode_themes: List[str]
    date: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "score": self.score,
            "guest": self.guest,
            "episode_id": self.episode_id,
            "youtube_url": self.youtube_url,
            "chunk_index": self.chunk_index,
            "guest_expertise": self.guest_expertise,
            "industry_tags": self.industry_tags,
            "episode_themes": self.episode_themes,
            "date": self.date,
        }


class Retriever:
    """
    Retrieves relevant context from the vector database.
    
    Supports:
    - Semantic search via embeddings
    - Metadata filtering (guest, industry)
    - Configurable top-k results
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
    ):
        """
        Initialize retriever.
        
        Args:
            vector_store: Vector database instance
            embedding_generator: Embedding generator instance
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_guest: Optional[str] = None,
        filter_industry: Optional[str] = None,
        min_score: float = 0.0,
        prefer_guest: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User's question or search query
            top_k: Number of results to return
            filter_guest: Optional guest name filter (hard filter)
            filter_industry: Optional industry tag filter
            min_score: Minimum similarity score threshold
            prefer_guest: Optional guest to prefer (soft filter - boosts score)
            
        Returns:
            List of RetrievalResult objects, sorted by score (highest first)
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.embed_text(query)
        
        # Search vector database
        raw_results = self.vector_store.search(
            query_embedding=query_embedding,
            limit=top_k * 3,  # Get more results for filtering and soft-filtering
            filter_guest=filter_guest,
            filter_industry=filter_industry,
        )
        
        # Convert to RetrievalResult objects and filter by score
        results = []
        for raw in raw_results:
            if raw["score"] >= min_score:
                result = RetrievalResult(
                    text=raw["text"],
                    score=raw["score"],
                    guest=raw["guest"],
                    episode_id=raw["episode_id"],
                    youtube_url=raw["youtube_url"],
                    chunk_index=raw["chunk_index"],
                    guest_expertise=raw["metadata"].get("guest_expertise", ""),
                    industry_tags=raw["metadata"].get("industry_tags", []),
                    episode_themes=raw["metadata"].get("episode_themes", []),
                    date=raw["metadata"].get("date", ""),
                )
                results.append(result)
        
        # Apply soft filtering if prefer_guest is specified
        if prefer_guest and not filter_guest:
            results = self._apply_guest_preference(results, prefer_guest, top_k)
        
        # Return top_k results
        return results[:top_k]
    
    def _apply_guest_preference(
        self,
        results: List[RetrievalResult],
        prefer_guest: str,
        top_k: int,
    ) -> List[RetrievalResult]:
        """
        Apply soft filtering to prefer a specific guest.
        
        Boosts scores for preferred guest but doesn't exclude others.
        This ensures we show preferred guest content if available,
        but fall back to other guests if preferred guest has no matches.
        
        Args:
            results: List of retrieval results
            prefer_guest: Guest name to prefer
            top_k: Number of results needed
            
        Returns:
            Re-ranked results with guest preference applied
        """
        # Normalize guest name for comparison
        prefer_guest_lower = prefer_guest.lower()
        
        # Separate results into preferred and others
        preferred = []
        others = []
        
        for result in results:
            if prefer_guest_lower in result.guest.lower():
                preferred.append(result)
            else:
                others.append(result)
        
        # If we have enough preferred results, use mostly those with some diversity
        if len(preferred) >= top_k:
            # Return mostly preferred (80%) with some others (20%) for diversity
            num_preferred = max(int(top_k * 0.8), top_k - 1)
            return preferred[:num_preferred] + others[:top_k - num_preferred]
        
        # If we have some preferred results, put them first
        elif preferred:
            return preferred + others
        
        # No preferred results found, return all others
        else:
            return others
    
    def retrieve_with_diversity(
        self,
        query: str,
        top_k: int = 5,
        max_per_guest: int = 2,
        prefer_guest: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve results with diversity across guests.
        
        This ensures we don't return all chunks from a single episode.
        
        Args:
            query: User's question
            top_k: Total number of results to return
            max_per_guest: Maximum chunks from any single guest
            prefer_guest: Optional guest to prefer (soft filter)
            
        Returns:
            Diverse list of RetrievalResult objects
        """
        # Get more candidates for diversity
        candidates = self.retrieve(query=query, top_k=top_k * 3, prefer_guest=prefer_guest)
        
        # Group by guest
        guest_counts = {}
        diverse_results = []
        
        for result in candidates:
            guest = result.guest
            count = guest_counts.get(guest, 0)
            
            # Add if under limit
            if count < max_per_guest:
                diverse_results.append(result)
                guest_counts[guest] = count + 1
            
            # Stop when we have enough
            if len(diverse_results) >= top_k:
                break
        
        return diverse_results


def format_results_for_display(results: List[RetrievalResult]) -> str:
    """
    Format retrieval results for display.
    
    Args:
        results: List of retrieval results
        
    Returns:
        Formatted string
    """
    if not results:
        return "No results found."
    
    output = []
    output.append(f"\n🔍 Found {len(results)} relevant chunks:\n")
    output.append("=" * 80)
    
    for idx, result in enumerate(results, 1):
        output.append(f"\n{idx}. [{result.guest}] (Score: {result.score:.3f})")
        output.append(f"   Episode: {result.episode_id}")
        output.append(f"   URL: {result.youtube_url}")
        output.append(f"   Tags: {', '.join(result.industry_tags)}")
        output.append(f"   Text: {result.text[:200]}...")
    
    output.append("\n" + "=" * 80)
    return "\n".join(output)


if __name__ == "__main__":
    # Test the retriever
    import sys
    
    print("🧪 Testing Retriever\n")
    
    # Initialize components
    print("Loading vector store and embedding model...")
    vector_store = VectorStore(
        collection_name="wtf_podcast",
        storage_path="./qdrant_db",
    )
    
    embedding_generator = EmbeddingGenerator()
    retriever = Retriever(vector_store, embedding_generator)
    
    # Test queries
    test_queries = [
        "What did Sam Altman say about AI?",
        "Tell me about Uber's strategy in India",
        "What are the challenges in autonomous vehicles?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print("="*80)
        
        results = retriever.retrieve(query=query, top_k=3)
        
        for idx, result in enumerate(results, 1):
            print(f"\n{idx}. [{result.guest}] (Score: {result.score:.3f})")
            print(f"   {result.text[:150]}...")
    
    print("\n" + "="*80)
    print("✓ Retriever test complete")

