# Audio Extraction Feature - FAQ

## Frequently Asked Questions

---

## Installation & Setup

### Q: How do I install the required dependencies?

**A:**
1. **System dependency (ffmpeg):**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows (with Chocolatey)
   choco install ffmpeg
   ```

2. **Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

The requirements.txt now includes:
- yt-dlp (YouTube audio download)
- faster-whisper (speech-to-text)
- ffmpeg-python (audio conversion)

---

### Q: What if ffmpeg is not installed?

**A:** You'll get an error like:
```
FileNotFoundError: ffmpeg not found
```

**Solution:** Install ffmpeg using your system package manager (see above).

---

### Q: Do I need a YouTube API key for audio extraction?

**A:** No. The audio extraction uses yt-dlp and Whisper, which don't require API keys. However, if you want to use the description extraction feature, you still need the YouTube API key configured.

---

## Feature Usage

### Q: How do I extract ingredients from YouTube audio?

**A:**
1. Open the Recipe Scaler frontend
2. Enter a YouTube video URL
3. Click the **🎤 Audio** button
4. Wait for three processing stages:
   - ⏳ Downloading video audio...
   - 🎤 Transcribing speech...
   - 🔍 Extracting ingredients...
5. View extracted ingredients

---

### Q: What types of videos work best?

**A:** Best results with:
- Cooking/recipe tutorial videos
- Clear, spoken ingredient lists
- English language content
- Minimal background music/noise
- Videos under 30 minutes (for speed)

---

### Q: Can it extract ingredients from non-English videos?

**A:** Currently, the Whisper model is configured for English. Future versions can support multiple languages by:
1. Detecting language automatically
2. Loading language-specific models
3. Configuring via environment variable

---

### Q: Why is the first use slower than subsequent uses?

**A:** Two reasons:
1. **Whisper model download:** ~140MB model downloads on first use (~1-2 minutes)
2. **Caching:** Subsequent requests for the same video are cached, skipping expensive download and transcription steps

---

## Performance

### Q: How long does processing take?

**A:**
- **First time:** 17-94 seconds (average 45s)
  - Audio download: 5-30s
  - Transcription: 10-60s
  - Filtering & parsing: 2-4s

- **Cached (repeat video):** < 3 seconds

---

### Q: How much memory does this feature use?

**A:**
- **Whisper model:** ~500MB (loaded once, reused)
- **Temp audio:** 10-50MB per video (auto-cleaned)
- **Database:** Negligible

---

### Q: Can I process multiple videos at once?

**A:** Currently, one at a time. The feature is designed for single-video extraction. Batch processing is a potential future enhancement.

---

## Error Handling

### Q: What does "Invalid YouTube URL" mean?

**A:** The URL format is not recognized as a valid YouTube link.

**Solution:** Make sure the URL is one of:
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- https://m.youtube.com/watch?v=VIDEO_ID
- https://www.youtube.com/embed/VIDEO_ID

---

### Q: Why can't I extract from a video I know?

**A:** Common reasons:
1. **Video is private/restricted:** Only public videos work
2. **Video has no audio:** (rare, but possible)
3. **Audio is in non-English language:** Model only recognizes English
4. **Audio quality is very poor:** Heavy background noise, low volume

**Solution:** Try another video to test the feature

---

### Q: What does "No ingredients detected in video audio" mean?

**A:** The audio was transcribed successfully, but no ingredient-related sentences were found.

**Possible causes:**
- Video doesn't mention ingredients (e.g., technique video)
- Ingredients mentioned too quietly
- Ingredients mentioned in a different language
- Transcript filtered out all content

**Solution:** Ensure video explicitly mentions ingredients (quantities, names, units)

---

### Q: How do I debug transcription failures?

**A:** Check backend logs for `[AUDIO_EXTRACTION]` messages:
```bash
# Look for lines like:
[AUDIO_EXTRACTION] Starting speech-to-text transcription
[AUDIO_EXTRACTION] Transcription completed, X characters
[AUDIO_EXTRACTION] ERROR: Unexpected error during transcription
```

---

## Technical Questions

### Q: Where are downloaded audio files stored?

**A:** In `/temp` directory within the backend folder.

**Important:** These files are automatically deleted after processing. If processing is interrupted, you may have orphaned files that can be manually deleted.

---

### Q: Are transcripts stored permanently?

**A:** Yes, in the SQLite database (`youtube_transcripts` table).

**Benefits:**
- Cached for future use
- Avoid re-processing same video
- Faster response for repeat videos

**Stored fields:**
- Transcript text
- Video ID, title, duration
- Language, extraction method
- Creation/update timestamps

---

### Q: Can I delete cached transcripts?

**A:** Yes, via direct database access:
```sql
-- Delete specific video transcript
DELETE FROM youtube_transcripts WHERE video_id = 'VIDEO_ID';

-- Delete all transcripts
DELETE FROM youtube_transcripts;
```

Or via backend code (if exposed as endpoint in future versions).

---

### Q: How does ingredient filtering work?

**A:** The system looks for keywords in several categories:

1. **Measurement keywords:** cup, gram, tablespoon, etc.
2. **Action keywords:** add, mix, chop, slice, etc.
3. **Ingredient names:** flour, sugar, butter, etc.
4. **Quality keywords:** fresh, chopped, diced, etc.

A sentence is included if it contains:
- Measurements + actions + ingredients, OR
- Measurements + ingredient names, OR
- Ingredient names + quality keywords

---

### Q: What Whisper model is used?

**A:** The `base` model by default.

**Available models:**
- tiny (smallest, fastest, least accurate)
- **base** (good balance) ← default
- small (more accurate, slower)
- medium (very accurate, slower)
- large (most accurate, slowest)

**Change via environment variable:**
```env
WHISPER_MODEL=small
```

---

### Q: Can I use GPU acceleration?

**A:** Yes, Whisper automatically detects and uses GPU if available (CUDA-compatible).

**Configuration:**
```env
WHISPER_DEVICE=auto     # Auto-detect (default)
WHISPER_DEVICE=cuda     # Force GPU
WHISPER_DEVICE=cpu      # Force CPU
```

---

## Database & Storage

### Q: Does this feature require database migrations?

**A:** No. The new `youtube_transcripts` table is created automatically on first run via SQLAlchemy's `Base.metadata.create_all()`.

---

### Q: How does caching work?

**A:** Simple and efficient:

```
1. Check database for video_id
2. If found → return cached transcript (skip steps 3-5)
3. If not found → download audio
4. Transcribe audio
5. Store in database
6. Extract ingredients from transcript
```

**Cache key:** `video_id` (unique per video)

---

### Q: Can I disable caching?

**A:** Not via configuration (would require code modification). However, caching provides significant speed benefits (17-94s → <3s on repeat).

---

## Troubleshooting

### Q: "ffmpeg not installed" error

**Error:**
```
ffmpeg not found on system
```

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
```

---

### Q: Whisper model download takes too long

**Issue:** First use downloads ~140MB model

**Solution:**
- Wait 1-2 minutes
- Check internet connection
- Or use smaller model (`tiny` or `small`)

---

### Q: Processing times out

**Issue:** Video processing takes > 30 seconds

**Solution:**
- Use shorter videos (under 30 min)
- Use smaller Whisper model
- Restart backend to free memory

---

### Q: "Memory error" or out of memory

**Issue:** Running out of RAM

**Solution:**
- Restart backend
- Use smaller Whisper model (`tiny`)
- Process shorter videos
- Close other applications

---

### Q: Empty ingredients list returned

**Issue:** No ingredients extracted

**Possible causes:**
- Video doesn't mention ingredients
- Ingredients filtered out
- Transcription failed silently

**Solution:**
- Check backend logs
- Try another video
- Look at full transcript to debug

---

## API & Integration

### Q: Can I call this from my own application?

**A:** Yes! The endpoint is REST-based:

```bash
curl -X POST "http://localhost:8000/api/youtube/extract-audio-ingredients" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
  }'
```

---

### Q: What's the API response format?

**A:**

Success (200 OK):
```json
{
  "video_id": "dQw4w9WgXcQ",
  "video_title": "Recipe Name",
  "transcript": "Full transcribed text...",
  "ingredients": [
    {
      "name": "flour",
      "quantity": 2.0,
      "unit": "cup",
      "notes": null,
      "original_quantity": null,
      "original_unit": null
    }
  ],
  "extraction_method": "audio",
  "success": true
}
```

Error (400/500):
```json
{
  "detail": "Error message describing the issue"
}
```

---

### Q: What HTTP status codes can be returned?

**A:**
- `200 OK` - Success
- `400 Bad Request` - Invalid URL or request
- `404 Not Found` - Video not found
- `500 Internal Server Error` - Processing failed

---

## Development & Contributing

### Q: Where is the feature documented?

**A:**
1. **AUDIO_EXTRACTION_FEATURE.md** - Complete technical documentation
2. **AUDIO_EXTRACTION_QUICK_START.md** - Quick start guide
3. **IMPLEMENTATION_SUMMARY_AUDIO_EXTRACTION.md** - Implementation details
4. **FILE_STRUCTURE_AUDIO_EXTRACTION.md** - File organization
5. **Inline code comments** - Within each service file

---

### Q: How can I contribute improvements?

**A:** Areas for enhancement:
- Multi-language support
- Custom keyword dictionary
- Audio quality pre-processing
- Timestamp-based extraction
- Batch processing
- UI improvements

See AUDIO_EXTRACTION_FEATURE.md for detailed enhancement suggestions.

---

### Q: How is code organized?

**A:**
- **Services:** `app/services/` - Business logic
- **Routes:** `app/routes/` - API endpoints
- **Models:** `app/models/` - Data validation
- **Database:** `app/database/` - Data persistence
- **Frontend:** `recipe scaler/` - UI components

---

## Support & Help

### Q: Where do I get help?

**A:**
1. Check this FAQ
2. Read AUDIO_EXTRACTION_QUICK_START.md
3. Review AUDIO_EXTRACTION_FEATURE.md
4. Check backend logs (`[AUDIO_EXTRACTION]` prefix)
5. Review inline code comments

---

### Q: How do I report a bug?

**A:** Include:
1. Error message (exact text)
2. Backend logs (around the error)
3. Video URL (if possible, use public video)
4. System info (OS, Python version)
5. Steps to reproduce

---

### Q: What's the roadmap?

**A:** See AUDIO_EXTRACTION_FEATURE.md "Future Enhancements" section for:
- Multi-language support
- Custom ingredient dictionary
- Timestamp extraction
- Batch processing
- Quality settings
- Audio enhancement

---

## More Questions?

**Check these resources in order:**
1. This FAQ
2. AUDIO_EXTRACTION_QUICK_START.md
3. AUDIO_EXTRACTION_FEATURE.md (detailed docs)
4. Backend logs with `[AUDIO_EXTRACTION]` prefix
5. Inline code comments in service files

---

**Last Updated:** March 2026
**Feature Version:** 1.0.0
**Status:** Production Ready
