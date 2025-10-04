"""
Text Chunking - Breaking up podcasts into bite-sized pieces

The problem: Podcast transcripts are LONG (like 15,000+ words). If we send the whole
thing to the AI, it gets overwhelmed and gives bad answers.

The solution: Break them into smaller "chunks" that are easier to search through.
Think of it like cutting a long article into paragraphs.

We tried different chunk sizes (1000, 2000, 3000 chars) and 2000 worked best.
Big enough to have context, small enough to stay focused.

The overlap (200 chars) is important - prevents cutting sentences in half.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Chunk:
    """
    A chunk of text with all the metadata we need to make sense of it.
    
    Each chunk is like a snippet from the podcast, but we also store WHO said it,
    WHICH episode it's from, and WHERE to find it on YouTube.
    """
    text: str                      # The actual transcript text
    episode_id: str                # Which episode this came from
    guest: str                     # Who was speaking (e.g., "Sam Altman")
    guest_expertise: str           # What they're known for (e.g., "CEO, OpenAI")
    industry_tags: List[str]       # Topics they discussed (e.g., ["AI", "startups"])
    episode_themes: List[str]      # Main themes of the episode
    youtube_url: str               # Link to the YouTube video
    date: str                      # When the episode aired
    chunk_index: int               # This is chunk #X out of Y
    total_chunks: int              # Total number of chunks in this episode
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary so we can store it in the database."""
        return {
            "text": self.text,
            "episode_id": self.episode_id,
            "guest": self.guest,
            "guest_expertise": self.guest_expertise,
            "industry_tags": self.industry_tags,
            "episode_themes": self.episode_themes,
            "youtube_url": self.youtube_url,
            "date": self.date,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
        }


class TranscriptChunker:
    """
    Breaks up long transcripts into manageable chunks.
    
    Why 2000 characters?
    - I tested 1000 (too small, lost context)
    - I tested 2000 (goldilocks zone ✓)
    - I tested 3000 (too big, search quality dropped)
    
    Why 200 character overlap?
    - Prevents cutting sentences in half
    - Gives each chunk a bit of context from the previous one
    - Surprisingly important for getting good search results
    """
    
    def __init__(
        self,
        chunk_size: int = 2000,  # ~500 tokens, about 2-3 paragraphs
        overlap: int = 200,      # ~50 tokens, keeps context flowing
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_episode(self, episode: Dict[str, Any]) -> List[Chunk]:
        """
        Chunk a single episode's transcript.
        
        Args:
            episode: Episode dict from episodes.json
            
        Returns:
            List of Chunk objects with metadata
        """
        transcript = episode["transcript"]
        
        # Calculate chunks
        chunks_text = self._split_text(transcript)
        total_chunks = len(chunks_text)
        
        # Create Chunk objects with metadata
        chunks = []
        for idx, text in enumerate(chunks_text):
            chunk = Chunk(
                text=text,
                episode_id=episode["id"],
                guest=episode["guest"],
                guest_expertise=episode.get("guest_expertise", ""),
                industry_tags=episode.get("industry_tags", []),
                episode_themes=episode.get("episode_themes", []),
                youtube_url=episode["youtube_url"],
                date=episode.get("date", ""),
                chunk_index=idx,
                total_chunks=total_chunks,
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks, trying to break at natural points.
        
        We don't just cut at exactly 2000 characters - that would slice sentences
        in half. Instead, we look for good break points like periods or line breaks.
        
        It's like cutting a sandwich - you want to cut between ingredients, not
        through the middle of the cheese.
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Figure out where this chunk should end
            end = start + self.chunk_size
            
            # If we're not at the very end, try to break at a sentence
            if end < text_length:
                # Look around the target boundary for a good break point
                # (we search ±100 chars to find a period, question mark, etc.)
                search_start = max(start, end - 100)
                search_text = text[search_start:end + 100]
                
                # Try to find a sentence ending
                # Priority: period > question mark > exclamation > paragraph break
                for separator in ['. ', '? ', '! ', '\n\n']:
                    pos = search_text.rfind(separator)
                    if pos != -1:
                        # Found one! Adjust the end point
                        end = search_start + pos + len(separator)
                        break
            
            # Extract the chunk and clean up whitespace
            chunk_text = text[start:end].strip()
            if chunk_text:  # Only add non-empty chunks
                chunks.append(chunk_text)
            
            # Move forward, but overlap a bit so we don't lose context
            start = end - self.overlap
        
        return chunks
    
    def chunk_all_episodes(self, episodes: List[Dict[str, Any]]) -> List[Chunk]:
        """
        Chunk all episodes.
        
        Args:
            episodes: List of episode dicts from episodes.json
            
        Returns:
            List of all chunks from all episodes
        """
        all_chunks = []
        for episode in episodes:
            chunks = self.chunk_episode(episode)
            all_chunks.extend(chunks)
        
        return all_chunks


def print_chunking_stats(chunks: List[Chunk]) -> None:
    """Print statistics about the chunking process."""
    if not chunks:
        print("No chunks created")
        return
    
    # Group by episode
    episodes = {}
    for chunk in chunks:
        ep_id = chunk.episode_id
        if ep_id not in episodes:
            episodes[ep_id] = []
        episodes[ep_id].append(chunk)
    
    print(f"\n📊 Chunking Statistics")
    print(f"{'='*60}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Total episodes: {len(episodes)}")
    print(f"Average chunks per episode: {len(chunks) / len(episodes):.1f}")
    
    print(f"\n📝 Per-Episode Breakdown:")
    for ep_id, ep_chunks in episodes.items():
        guest = ep_chunks[0].guest if ep_chunks else "Unknown"
        print(f"  {ep_id} ({guest}): {len(ep_chunks)} chunks")
    
    # Chunk size stats
    chunk_sizes = [len(chunk.text) for chunk in chunks]
    avg_size = sum(chunk_sizes) / len(chunk_sizes)
    min_size = min(chunk_sizes)
    max_size = max(chunk_sizes)
    
    print(f"\n📏 Chunk Size Distribution:")
    print(f"  Average: {avg_size:.0f} characters")
    print(f"  Min: {min_size} characters")
    print(f"  Max: {max_size} characters")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Test chunking on local episodes
    import json
    from pathlib import Path
    
    episodes_file = Path("data/episodes.json")
    if not episodes_file.exists():
        print("❌ data/episodes.json not found")
        exit(1)
    
    with open(episodes_file, 'r', encoding='utf-8') as f:
        episodes = json.load(f)
    
    print(f"📚 Loading {len(episodes)} episodes...")
    
    chunker = TranscriptChunker()
    chunks = chunker.chunk_all_episodes(episodes)
    
    print_chunking_stats(chunks)
    
    # Show sample chunk
    if chunks:
        print("📄 Sample Chunk:")
        print(f"{'='*60}")
        sample = chunks[0]
        print(f"Guest: {sample.guest}")
        print(f"Episode: {sample.episode_id}")
        print(f"Chunk {sample.chunk_index + 1}/{sample.total_chunks}")
        print(f"\nText preview (first 300 chars):")
        print(f"{sample.text[:300]}...")
        print(f"{'='*60}")

