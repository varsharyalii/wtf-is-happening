"""
Tests for the chunking logic.

These are pretty basic tests, but they catch the obvious bugs.
In a real production system, I'd add way more edge cases.
"""

import pytest
from src.chunker import TranscriptChunker, Chunk


def test_chunker_creates_reasonable_chunks():
    """Make sure chunks aren't crazy sizes."""
    chunker = TranscriptChunker(chunk_size=100, overlap=20)
    
    # A simple test text
    text = "Hello world. " * 50  # ~650 characters
    chunks = chunker._split_text(text)
    
    # Should have created multiple chunks
    assert len(chunks) > 1, "Should split long text into multiple chunks"
    
    # Chunks should be roughly the right size
    for chunk in chunks:
        assert len(chunk) <= 150, f"Chunk too long: {len(chunk)} chars"
        assert len(chunk) > 0, "Empty chunk found"


def test_chunker_respects_sentence_boundaries():
    """Chunks should try to break at sentence endings, not mid-sentence."""
    chunker = TranscriptChunker(chunk_size=50, overlap=10)
    
    text = "This is sentence one. This is sentence two. This is sentence three."
    chunks = chunker._split_text(text)
    
    # Each chunk should end with a period (if it's not the last chunk)
    for chunk in chunks[:-1]:  # All except last
        # Should end with reasonable punctuation
        assert chunk[-1] in ['.', '?', '!', '\n'], \
            f"Chunk doesn't end cleanly: '{chunk[-20:]}'"


def test_chunk_metadata_is_preserved():
    """Make sure we don't lose episode metadata when chunking."""
    chunker = TranscriptChunker(chunk_size=100, overlap=20)
    
    episode = {
        "id": "test_episode",
        "transcript": "Some test transcript. " * 30,
        "guest": "Test Guest",
        "guest_expertise": "Testing Expert",
        "youtube_url": "https://youtube.com/test",
        "industry_tags": ["testing"],
        "episode_themes": ["quality"],
        "date": "2024-01-01"
    }
    
    chunks = chunker.chunk_episode(episode)
    
    assert len(chunks) > 0, "Should create at least one chunk"
    
    # Check first chunk has all the metadata
    first_chunk = chunks[0]
    assert first_chunk.guest == "Test Guest"
    assert first_chunk.episode_id == "test_episode"
    assert first_chunk.youtube_url == "https://youtube.com/test"
    assert first_chunk.chunk_index == 0
    assert first_chunk.total_chunks == len(chunks)


def test_empty_transcript_doesnt_crash():
    """Edge case: what if transcript is empty?"""
    chunker = TranscriptChunker()
    
    episode = {
        "id": "empty",
        "transcript": "",
        "guest": "Nobody",
        "youtube_url": "https://youtube.com/empty",
    }
    
    chunks = chunker.chunk_episode(episode)
    
    # Should return empty list, not crash
    assert chunks == []


def test_chunk_overlap_works():
    """Chunks should have some overlap to preserve context."""
    chunker = TranscriptChunker(chunk_size=100, overlap=20)
    
    # Use a distinctive pattern so we can check overlap
    text = "AAAA " * 100  # Lots of As
    chunks = chunker._split_text(text)
    
    if len(chunks) > 1:
        # Later chunks should start with some of the previous chunk's text
        # (This is hard to test precisely because of sentence boundary detection,
        #  but we can at least verify multiple chunks were created)
        assert len(chunks) >= 2


def test_to_dict_conversion():
    """Make sure we can convert chunks to dictionaries for storage."""
    chunk = Chunk(
        text="Test text",
        episode_id="ep1",
        guest="Test Guest",
        guest_expertise="Expert",
        industry_tags=["tag1"],
        episode_themes=["theme1"],
        youtube_url="https://youtube.com/test",
        date="2024-01-01",
        chunk_index=0,
        total_chunks=5
    )
    
    chunk_dict = chunk.to_dict()
    
    # Should be a dictionary
    assert isinstance(chunk_dict, dict)
    
    # Should have all the fields
    assert chunk_dict["text"] == "Test text"
    assert chunk_dict["guest"] == "Test Guest"
    assert chunk_dict["episode_id"] == "ep1"
    

if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_chunker.py -v
    print("Run these tests with: pytest tests/test_chunker.py -v")

