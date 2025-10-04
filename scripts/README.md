# Scripts

Helper scripts for working with WTF Podcast data.

## download_transcript.py

Downloads YouTube transcripts and adds them to `data/episodes.json`.

### Usage

```bash
# Make sure you've installed dependencies first
# pip install -r requirements.txt

# Download a transcript by video ID
python scripts/download_transcript.py VIDEO_ID

# Or by full URL
python scripts/download_transcript.py "https://youtube.com/watch?v=VIDEO_ID"
```

### Example Workflow

1. **Find WTF podcast episodes on YouTube:**
   - Channel: https://www.youtube.com/@NikhilKamathClips
   - Pick 3-5 episodes you want to start with

2. **Download transcripts:**
   ```bash
   python scripts/download_transcript.py "https://youtube.com/watch?v=abc123"
   python scripts/download_transcript.py "https://youtube.com/watch?v=def456"
   python scripts/download_transcript.py "https://youtube.com/watch?v=ghi789"
   ```

3. **Edit `data/episodes.json`:**
   - Fill in the TODO fields for each episode:
     - `title`: Episode title
     - `guest`: Guest name
     - `guest_expertise`: Their background/expertise
     - `industry_tags`: Relevant industries (e.g., ["fintech", "consumer"])
     - `episode_themes`: Main topics discussed
     - `date`: Episode release date (YYYY-MM-DD format)
     - `duration_minutes`: Approximate duration

4. **Run ingestion:**
   ```bash
   make ingest
   ```

### Tips

- **Start with diverse episodes** to test cross-episode queries
- **Good variety:** 1 fintech + 1 EV/manufacturing + 1 other industry
- **Check transcript quality** after download - auto-generated can have errors
- **Manual edits welcome** - fix any obvious transcription mistakes

### Troubleshooting

**"Transcripts are disabled for this video"**
- Some videos don't have captions enabled
- Try a different episode

**"No English transcript found"**
- Video might only have Hindi captions
- You can try downloading Hindi and translating (advanced)

**Import errors**
- Make sure you've run: `pip install -r requirements.txt`

