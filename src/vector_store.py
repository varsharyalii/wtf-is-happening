"""
Vector Store using Qdrant

Manages the vector database for efficient similarity search.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)


class VectorStore:
    """
    Qdrant vector database wrapper for RAG system.
    
    Handles:
    - Collection creation
    - Vector insertion with metadata
    - Similarity search with filters
    """
    
    def __init__(
        self,
        collection_name: str = "wtf_podcast",
        storage_path: str = "./qdrant_db",
        embedding_dim: int = 384,
    ):
        """
        Initialize Qdrant client and collection.
        
        Args:
            collection_name: Name of the Qdrant collection
            storage_path: Path to store Qdrant data
            embedding_dim: Dimension of embeddings (384 for all-MiniLM-L6-v2)
        """
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        
        # Create storage directory
        Path(storage_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize client (local storage)
        print(f"🔌 Connecting to Qdrant (local storage: {storage_path})")
        self.client = QdrantClient(path=storage_path)
        
        # Create collection if it doesn't exist
        self._init_collection()
    
    def _init_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            print(f"📦 Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,  # Cosine similarity
                ),
            )
            print(f"✓ Collection created")
        else:
            print(f"✓ Collection '{self.collection_name}' already exists")
    
    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: np.ndarray,
        batch_size: int = 100,
    ) -> None:
        """
        Add chunks with embeddings to the vector store.
        
        Args:
            chunks: List of chunk dicts with metadata
            embeddings: Numpy array of embeddings (num_chunks, embedding_dim)
            batch_size: Number of points to upload at once
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must have same length")
        
        print(f"\n📤 Uploading {len(chunks)} chunks to Qdrant...")
        
        # Create points
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=idx,
                vector=embedding.tolist(),
                payload={
                    "text": chunk["text"],
                    "episode_id": chunk["episode_id"],
                    "guest": chunk["guest"],
                    "guest_expertise": chunk["guest_expertise"],
                    "industry_tags": chunk["industry_tags"],
                    "episode_themes": chunk["episode_themes"],
                    "youtube_url": chunk["youtube_url"],
                    "date": chunk["date"],
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks": chunk["total_chunks"],
                }
            )
            points.append(point)
        
        # Upload in batches
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )
            print(f"  Uploaded batch {i // batch_size + 1}/{(len(points) + batch_size - 1) // batch_size}")
        
        print(f"✓ Upload complete")
    
    def search(
        self,
        query_embedding: np.ndarray,
        limit: int = 5,
        filter_guest: Optional[str] = None,
        filter_industry: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query vector
            limit: Number of results to return
            filter_guest: Optional guest name filter
            filter_industry: Optional industry tag filter
            
        Returns:
            List of search results with metadata and scores
        """
        # Build filter
        filter_conditions = []
        if filter_guest:
            filter_conditions.append(
                FieldCondition(
                    key="guest",
                    match=MatchValue(value=filter_guest)
                )
            )
        if filter_industry:
            filter_conditions.append(
                FieldCondition(
                    key="industry_tags",
                    match=MatchValue(value=filter_industry)
                )
            )
        
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=limit,
            query_filter=search_filter,
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "score": result.score,
                "text": result.payload["text"],
                "guest": result.payload["guest"],
                "episode_id": result.payload["episode_id"],
                "youtube_url": result.payload["youtube_url"],
                "chunk_index": result.payload["chunk_index"],
                "metadata": result.payload,
            })
        
        return formatted_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        info = self.client.get_collection(collection_name=self.collection_name)
        return {
            "name": info.config.params.vectors.size,
            "vector_count": info.points_count,
            "embedding_dim": info.config.params.vectors.size,
            "distance_metric": info.config.params.vectors.distance,
        }
    
    def clear_collection(self):
        """Delete and recreate the collection (careful!)."""
        print(f"⚠️  Clearing collection: {self.collection_name}")
        self.client.delete_collection(collection_name=self.collection_name)
        self._init_collection()
        print(f"✓ Collection cleared")


def print_search_results(results: List[Dict[str, Any]], query: str = "") -> None:
    """Pretty print search results."""
    if query:
        print(f"\n🔍 Query: '{query}'")
    
    print(f"\n📋 Search Results ({len(results)} found)")
    print(f"{'='*80}")
    
    for idx, result in enumerate(results, 1):
        print(f"\n{idx}. [{result['guest']}] (Score: {result['score']:.4f})")
        print(f"   Episode: {result['episode_id']}")
        print(f"   URL: {result['youtube_url']}")
        print(f"   Chunk: {result['chunk_index'] + 1}")
        print(f"   Text: {result['text'][:200]}...")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Test vector store
    print("🧪 Testing Vector Store\n")
    
    # Create dummy data
    dummy_chunks = [
        {
            "text": "We discussed artificial intelligence and its impact on society.",
            "episode_id": "ep_test_01",
            "guest": "Test Guest 1",
            "guest_expertise": "AI Researcher",
            "industry_tags": ["AI", "technology"],
            "episode_themes": ["innovation"],
            "youtube_url": "https://youtube.com/watch?v=test1",
            "date": "2024-01-01",
            "chunk_index": 0,
            "total_chunks": 1,
        },
        {
            "text": "Machine learning is transforming how we build products.",
            "episode_id": "ep_test_02",
            "guest": "Test Guest 2",
            "guest_expertise": "ML Engineer",
            "industry_tags": ["ML", "technology"],
            "episode_themes": ["product"],
            "youtube_url": "https://youtube.com/watch?v=test2",
            "date": "2024-01-02",
            "chunk_index": 0,
            "total_chunks": 1,
        },
    ]
    
    # Create dummy embeddings (random for testing)
    dummy_embeddings = np.random.rand(2, 384).astype(np.float32)
    
    # Test store
    store = VectorStore(collection_name="test_collection", storage_path="./test_qdrant_db")
    
    # Add chunks
    store.add_chunks(dummy_chunks, dummy_embeddings)
    
    # Get info
    info = store.get_collection_info()
    print(f"\n📊 Collection Info:")
    print(f"  Vectors: {info['vector_count']}")
    print(f"  Dimension: {info['embedding_dim']}")
    
    # Test search
    query_embedding = dummy_embeddings[0]
    results = store.search(query_embedding, limit=2)
    
    print_search_results(results, query="Test query")
    
    # Cleanup
    store.clear_collection()
    print("✓ Test complete")

