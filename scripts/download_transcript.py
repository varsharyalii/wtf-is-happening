#!/usr/bin/env python3
"""
Helper script to download YouTube transcripts for WTF podcast episodes.

Usage:
    python scripts/download_transcript.py VIDEO_ID

Example:
    python scripts/download_transcript.py dQw4w9WgXcQ
"""

import sys
import json
from pathlib import Path
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
except ImportError:
    print("❌ youtube-transcript-api not installed")
    print("Run: pip install youtube-transcript-api")
    sys.exit(1)


def get_video_id_from_url(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        # Extract ID from various YouTube URL formats
        if "v=" in url_or_id:
            return url_or_id.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url_or_id:
            return url_or_id.split("youtu.be/")[1].split("?")[0]
    return url_or_id


def download_transcript(video_id: str) -> str:
    """
    Download transcript for a YouTube video.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Full transcript as a single string
        
    Raises:
        TranscriptsDisabled: If transcripts are disabled for this video
        NoTranscriptFound: If no transcript is available
    """
    print(f"📥 Downloading transcript for video: {video_id}")
    
    try:
        # Create API instance and fetch transcript
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        # Try to get English transcript
        transcript_data = transcript_list.find_transcript(['en', 'en-US'])
        fetched_data = transcript_data.fetch()
        print("✓ Found English transcript")
        
        # Combine all text segments from snippets
        full_text = " ".join([snippet.text for snippet in fetched_data.snippets])
        
        # Clean up the text
        full_text = full_text.replace('\n', ' ')
        full_text = ' '.join(full_text.split())  # Remove extra whitespace
        
        print(f"✓ Downloaded {len(full_text)} characters")
        return full_text
        
    except TranscriptsDisabled:
        print("❌ Transcripts are disabled for this video")
        raise
    except NoTranscriptFound:
        print("❌ No English transcript found for this video")
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


def create_episode_template(video_id: str, transcript: str) -> dict:
    """Create an episode template with the transcript."""
    return {
        "id": f"ep_{video_id[:8]}",
        "title": "TODO: Add episode title",
        "guest": "TODO: Add guest name",
        "guest_expertise": "TODO: Add guest expertise/background",
        "industry_tags": ["TODO", "ADD", "TAGS"],
        "episode_themes": ["TODO", "ADD", "THEMES"],
        "date": "YYYY-MM-DD",
        "youtube_url": f"https://youtube.com/watch?v={video_id}",
        "youtube_video_id": video_id,
        "duration_minutes": 0,
        "transcript": transcript
    }


def add_to_episodes_file(episode: dict):
    """Add episode to data/episodes.json."""
    episodes_file = Path(__file__).parent.parent / "data" / "episodes.json"
    
    # Load existing episodes
    if episodes_file.exists():
        with open(episodes_file, 'r') as f:
            episodes = json.load(f)
    else:
        episodes = []
    
    # Check if episode already exists
    video_id = episode['youtube_video_id']
    if any(ep.get('youtube_video_id') == video_id for ep in episodes):
        print(f"⚠️  Episode with video ID {video_id} already exists")
        return False
    
    # Add new episode
    episodes.append(episode)
    
    # Save
    with open(episodes_file, 'w') as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Added episode to {episodes_file}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/download_transcript.py VIDEO_ID_OR_URL")
        print("\nExample:")
        print("  python scripts/download_transcript.py dQw4w9WgXcQ")
        print("  python scripts/download_transcript.py https://youtube.com/watch?v=dQw4w9WgXcQ")
        sys.exit(1)
    
    video_input = sys.argv[1]
    video_id = get_video_id_from_url(video_input)
    
    print(f"🎙️  WTF Podcast Transcript Downloader")
    print(f"Video ID: {video_id}")
    print("-" * 50)
    
    try:
        # Download transcript
        transcript = download_transcript(video_id)
        
        # Create episode template
        episode = create_episode_template(video_id, transcript)
        
        # Add to episodes.json
        if add_to_episodes_file(episode):
            print("\n✓ Success!")
            print("\nNext steps:")
            print("1. Edit data/episodes.json and fill in the TODO fields:")
            print("   - title, guest, guest_expertise, industry_tags, episode_themes, date")
            print("2. Repeat for 2-4 more episodes")
            print("3. Run: make ingest")
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

