"""
Embedding Generation using Sentence Transformers

Uses the all-MiniLM-L6-v2 model for fast, quality embeddings.
- 384 dimensions
- ~50ms per embedding on CPU
- Good balance of speed and quality
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """
    Generates vector embeddings for text chunks.
    
    Uses sentence-transformers for local embedding generation
    (no API calls required, free, fast on CPU).
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        print(f"📦 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"✓ Model loaded (embedding dim: {self.get_embedding_dim()})")
    
    def get_embedding_dim(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Numpy array of shape (embedding_dim,)
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of shape (num_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings
    
    def embed_with_metadata(
        self,
        text: str,
        metadata: dict
    ) -> dict:
        """
        Generate embedding and package with metadata.
        
        Args:
            text: Input text
            metadata: Metadata dict to attach
            
        Returns:
            Dict with 'embedding', 'text', and metadata fields
        """
        embedding = self.embed_text(text)
        
        return {
            "embedding": embedding,
            "text": text,
            **metadata
        }


def print_embedding_stats(embeddings: np.ndarray) -> None:
    """Print statistics about generated embeddings."""
    print(f"\n📊 Embedding Statistics")
    print(f"{'='*60}")
    print(f"Number of embeddings: {embeddings.shape[0]}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"Total size: {embeddings.nbytes / 1024 / 1024:.2f} MB")
    
    # Basic stats
    print(f"\n📈 Value Distribution:")
    print(f"  Mean: {embeddings.mean():.4f}")
    print(f"  Std: {embeddings.std():.4f}")
    print(f"  Min: {embeddings.min():.4f}")
    print(f"  Max: {embeddings.max():.4f}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Test embedding generation
    print("🧪 Testing Embedding Generation\n")
    
    generator = EmbeddingGenerator()
    
    # Test single embedding
    test_text = "This is a test of the embedding system."
    embedding = generator.embed_text(test_text)
    
    print(f"✓ Generated single embedding")
    print(f"  Input: '{test_text}'")
    print(f"  Shape: {embedding.shape}")
    print(f"  First 5 values: {embedding[:5]}")
    
    # Test batch embedding
    test_texts = [
        "Artificial intelligence is transforming technology.",
        "Machine learning models require large datasets.",
        "Natural language processing enables human-computer interaction.",
    ]
    
    print(f"\n🔄 Testing batch embedding...")
    embeddings = generator.embed_batch(test_texts, show_progress=False)
    
    print_embedding_stats(embeddings)
    
    # Test similarity
    print("🔍 Testing Similarity:")
    from numpy.linalg import norm
    
    # Cosine similarity between first two embeddings
    sim = np.dot(embeddings[0], embeddings[1]) / (norm(embeddings[0]) * norm(embeddings[1]))
    print(f"  Similarity between text 1 and 2: {sim:.4f}")
    
    sim = np.dot(embeddings[0], embeddings[2]) / (norm(embeddings[0]) * norm(embeddings[2]))
    print(f"  Similarity between text 1 and 3: {sim:.4f}")

