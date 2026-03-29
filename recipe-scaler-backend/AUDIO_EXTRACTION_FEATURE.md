# Speech-to-Text Recipe Ingredient Extraction Feature

## Overview

This feature enables the Recipe Scaler application to extract ingredients directly from YouTube video audio using speech-to-text technology. When a video has no transcript or description available, users can now extract ingredients by analyzing the spoken content.

## Architecture

### Pipeline Flow

```
YouTube URL
    ↓
[Audio Download] - yt-dlp downloads best audio
    ↓
[Transcription] - Faster-Whisper converts speech → text
    ↓
[Filtering] - Filter for ingredient-related sentences
    ↓
[Parsing] - Extract structured ingredients
    ↓
[Database Cache] - Store transcript for future use
    ↓
Structured Ingredients + Transcript
```

## Backend Implementation

### 1. New Dependencies

**File:** `requirements.txt`

Added to the project:
- `yt-dlp==2023.12.30` - YouTube audio downloading
- `faster-whisper==0.10.0` - Speech-to-text transcription
- `ffmpeg-python==0.2.1` - Audio format conversion

**System Dependency:**
- `ffmpeg` - Audio processing utility (install via `apt-get`, `brew`, or `choco`)

### 2. New Service: Audio Download (`app/services/audio_service.py`)

**Main Function:**
```python
def download_youtube_audio(video_url: str) -> str
```

**Features:**
- Downloads best quality audio from YouTube videos
- Converts to WAV format for Whisper compatibility
- Saves to `/temp` directory
- Handles errors gracefully
- Cleans up files after processing

**Key Methods:**
- `ensure_temp_dir()` - Create temp directory if needed
- `cleanup_audio_file(file_path)` - Delete single audio file
- `cleanup_all_temp_files()` - Clean entire temp directory

### 3. New Service: Speech-to-Text (`app/services/speech_service.py`)

**Main Function:**
```python
def transcribe_audio(audio_path: str) -> str
```

**Features:**
- Uses Faster-Whisper for efficient transcription
- Lazy-loads model for first use
- Supports English language recognition
- Combines segments into full transcript
- Auto-detects GPU/CPU availability

**Model Configuration:**
- Model: `base` (small, fast, accurate)
- Language: English
- Device: Auto-detect GPU/CPU
- Temperature: 0.0 (greedy decoding)

### 4. New Service: Ingredient Filtering (`app/services/ingredient_filter_service.py`)

**Main Function:**
```python
def filter_ingredient_sentences(transcript: str) -> str
```

**Features:**
- Filters transcript to extract ingredient-related sentences
- Recognizes:
  - Measurement keywords (cup, gram, tablespoon, etc.)
  - Action keywords (add, mix, chop, slice, etc.)
  - Common ingredient names
  - Quality keywords (fresh, diced, chopped, etc.)

**Included Keywords:**

Measurements:
- cup, tablespoon, teaspoon, gram, ounce, pound, ml, liter
- pinch, dash, handful, splash

Actions:
- add, mix, combine, use, take, chop, slice, dice, mince, pour, stir, blend, etc.

Ingredients:
- flour, sugar, salt, pepper, butter, oil, water, milk, eggs, onion, garlic, tomato, chicken, beef, etc.

### 5. Database Model (`app/database/db.py`)

**New Table:** `YouTubeTranscriptDB`

```python
class YouTubeTranscriptDB(Base):
    __tablename__ = "youtube_transcripts"
    
    id: str (Primary Key)
    video_id: str (Unique)
    title: str
    transcript: Text
    transcript_segments: JSON (optional)
    duration: Float (optional)
    language: str (default: "en")
    extraction_method: str ("audio", "youtube_api", "manual")
    created_at: DateTime
    updated_at: DateTime
```

**Purpose:** Cache transcripts to avoid re-processing same videos

### 6. Pydantic Models (`app/models/schemas.py`)

**Request Model:**
```python
class AudioExtractionRequest(BaseModel):
    youtube_url: str
```

**Response Model:**
```python
class AudioExtractionResponse(BaseModel):
    video_id: str
    video_title: str
    transcript: str  # Full transcribed text
    ingredients: List[Ingredient]
    extraction_method: str = "audio"
    success: bool
```

### 7. New API Endpoint (`app/routes/youtube.py`)

**Endpoint:** `POST /api/youtube/extract-audio-ingredients`

**Request:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response (Success):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "video_title": "Easy Pasta Recipe",
  "transcript": "Today we'll make pasta. Start with 2 cups of flour...",
  "ingredients": [
    {
      "name": "flour",
      "quantity": 2.0,
      "unit": "cup",
      "notes": null
    },
    {
      "name": "water",
      "quantity": 0.5,
      "unit": "cup",
      "notes": null
    }
  ],
  "extraction_method": "audio",
  "success": true
}
```

**Response (Error):**
```json
{
  "detail": "Failed to download video audio: [error message]"
}
```

**Status Codes:**
- `200 OK` - Successfully extracted ingredients
- `400 Bad Request` - Invalid URL format
- `404 Not Found` - Video not found
- `500 Internal Server Error` - Download, transcription, or extraction failed

**Processing Steps:**
1. Validate YouTube URL
2. Extract video ID
3. Check if transcript cached (skip to step 7 if cached)
4. Download audio using yt-dlp
5. Transcribe audio using Faster-Whisper
6. Cache transcript in database
7. Filter transcript for ingredient sentences
8. Extract structured ingredients
9. Return response with video details and ingredients

## Frontend Implementation

### 1. UI Components (`index.html`)

**Audio Extraction Button:**
- Added to the YouTube Link tab
- Green secondary button with microphone icon
- Shows alongside "Fetch Ingredients" button
- Tooltip: "Extract ingredients from video audio when no description available"

**Extraction Stages Display:**
- Shows progress with three stages:
  1. Downloading video audio... ⏳
  2. Transcribing speech... 🎤
  3. Extracting ingredients... 🔍
- Appears during processing
- Auto-hides after 3 seconds
- Shows status icons (pending, complete, error)

### 2. JavaScript Functions

**Main Handler (`script.js`):**
```javascript
async function extractAudioIngredients()
```

**Features:**
- Validates YouTube URL
- Shows extraction stages UI
- Calls backend API
- Displays results or error
- Updates ingredient list
- Stores ingredients in session storage

**Stage Update Function:**
```javascript
function updateExtractionStage(stageName, status)
```

Updates UI stage indicators with:
- Icons: ⏳ (pending), ✅ (complete), ❌ (error)
- CSS classes for styling
- Animations (pulse, shake)

**API Client Method (`api-client.js`):**
```javascript
async extractAudioIngredients(youtubeUrl)
```

Calls the backend endpoint with proper error handling.

### 3. CSS Styling (`styles.css`)

**New Styles:**
- `.button-group` - Flex container for multiple buttons
- `.extraction-stages` - Container with green left border
- `.stage` - Individual stage item
- `.stage-icon` - Animated status icon
- `.stage.pending/complete/error` - Status variants
- `@keyframes pulse` - Pulsing animation for pending stages
- `@keyframes shake` - Shaking animation for error stages
- `@keyframes slideIn` - Slide-in animation for stages container
- `.secondary-btn` - Green button styling

## Error Handling

### Comprehensive Error Coverage

**Invalid URL:**
- Status: 400 Bad Request
- Message: "Invalid YouTube URL"

**Download Failure:**
- Status: 500 Internal Server Error
- Message: "Failed to download video audio: [error details]"
- Common causes:
  - Private/restricted video
  - No audio track available
  - Network issues

**Transcription Failure:**
- Status: 500 Internal Server Error
- Message: "Unable to transcribe video audio: [error details]"
- Common causes:
  - Audio is too short
  - Audio quality too low
  - Unsupported language

**No Ingredients Detected:**
- Status: 200 OK (but with warning)
- Message: "No ingredients detected in video audio"
- Occurs when:
  - Video content has no ingredient mentions
  - Transcript is empty
  - Filtering removed all content

### User Feedback

**Success:**
```
✅ Successfully extracted {count} ingredients from video audio!
```

**Errors:**
```
❌ Failed to download video audio. Check URL and try again.
❌ Unable to transcribe video audio. Audio may be unclear.
❌ No ingredients detected in video audio.
```

## Logging

Comprehensive logging with prefixes for debugging:

**Format:** `[AUDIO_EXTRACTION] <message>`

**Log Levels:**
- `INFO` - Major steps (download start, transcription start, etc.)
- `DEBUG` - Detailed progress (segments extracted, etc.)
- `WARNING` - Unexpected but handled situations
- `ERROR` - Failures with full traceback

**Key Log Points:**
- Processing start with video URL
- Video ID extraction
- Cache hit/miss
- Download start/completion
- Transcription start/completion
- Sentence filtering stats
- Ingredient extraction count
- Transcript caching status
- Final success/failure

## Performance Optimization

### Transcript Caching

**Benefits:**
- Skip expensive download + transcription for repeat videos
- Faster second-time processing
- Reduced bandwidth usage

**Implementation:**
- Check database for cached transcript before processing
- Store transcript + metadata after successful transcription
- Cache key: video_id (unique)

### Lazy Model Loading

**Whisper Model:**
- Loaded on first use (lazy loading)
- Kept in memory for subsequent requests
- Can be unloaded manually with `SpeechService.unload_model()`

**Benefits:**
- No memory overhead if feature not used
- Fast subsequent requests
- Can be unloaded to free memory

### Audio Format Optimization

**Download Strategy:**
- Download best available audio
- Convert to WAV format (Whisper-compatible)
- Cleaned up immediately after transcription

## Usage Examples

### Backend API Call

```bash
curl -X POST "http://localhost:8000/api/youtube/extract-audio-ingredients" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

### Frontend JavaScript Call

```javascript
// Manual invocation
extractAudioIngredients();

// From API client
const response = await apiClient.extractAudioIngredients(videoUrl);
console.log(response.ingredients);
```

## Requirements & Installation

### 1. Python Dependencies

```bash
pip install -r requirements.txt
```

Includes:
- yt-dlp
- faster-whisper
- ffmpeg-python

### 2. System Dependencies

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
choco install ffmpeg
```

### 3. Environment Setup

Create `.env` file with optional settings:
```env
# Audio extraction settings (optional)
TEMP_DIR=./temp
WHISPER_MODEL=base
WHISPER_DEVICE=auto
```

## Testing

### Manual Testing

1. **Start Backend:**
   ```bash
   python main.py
   ```

2. **Open Frontend:**
   - Navigate to `http://localhost:8000` or your frontend URL

3. **Test Audio Extraction:**
   - Enter a YouTube URL (e.g., cooking video)
   - Click "🎤 Audio" button
   - Watch stages update
   - Verify ingredients extracted

### Test Cases

**Success Case:**
- Input: YouTube cooking video with clear audio
- Expected: Ingredients extracted and displayed

**Error Cases:**
- Invalid URL: Should show "Invalid YouTube URL"
- Private video: Should show download failure
- No audio: Should show transcription failure
- No ingredients spoken: Should show no ingredients detected

## Troubleshooting

### Common Issues

**"ffmpeg is not installed"**
- Solution: Install ffmpeg using system package manager

**"yt-dlp download error"**
- Solution: Video may be private, geo-restricted, or unavailable
- Check video is publicly accessible

**"No speech detected in audio"**
- Solution: Audio may be too short or unclear
- Try video with clear, spoken ingredient list

**"Whisper model download fails"**
- Solution: Check internet connection
- Model (~140MB) needs to download on first use

**Memory issues with large videos**
- Solution: Restart backend between processing
- Or: Use smaller Whisper model (tiny, small instead of base)

## Future Enhancements

1. **Multi-Language Support**
   - Detect language automatically
   - Support for multiple languages

2. **Custom Ingredient Dictionary**
   - Allow users to define custom ingredient keywords
   - Learn from user corrections

3. **Timestamp-Based Extraction**
   - Return ingredient mentions with timestamps
   - Let users see exact moment in video

4. **Batch Processing**
   - Process multiple videos asynchronously
   - Queue management system

5. **Quality Settings**
   - Allow users to choose model size (tiny/small/base/medium)
   - Balance speed vs accuracy

6. **Audio Enhancement**
   - Pre-process audio to improve quality
   - Handle background music/noise

## Security Considerations

1. **API Key Protection**
   - YouTube API key in environment variables
   - Never expose in client-side code

2. **Temp File Cleanup**
   - Automatic cleanup of downloaded audio
   - No sensitive data stored in temp

3. **URL Validation**
   - Validate YouTube URLs before processing
   - Prevent injection attacks

4. **Database Caching**
   - Only cache metadata, not raw audio
   - Store in SQLite (local database)

## Files Modified/Created

### Backend

**Created:**
- `app/services/audio_service.py` - Audio download service
- `app/services/speech_service.py` - Speech-to-text service
- `app/services/ingredient_filter_service.py` - Ingredient filtering

**Modified:**
- `app/models/schemas.py` - Added AudioExtractionRequest/Response
- `app/database/db.py` - Added YouTubeTranscriptDB model
- `app/routes/youtube.py` - Added extract-audio-ingredients endpoint
- `requirements.txt` - Added dependencies

**Directories Created:**
- `temp/` - For storing downloaded audio files

### Frontend

**Modified:**
- `index.html` - Added audio button and stages display
- `script.js` - Added extractAudioIngredients() function and stage updater
- `api-client.js` - Added extractAudioIngredients() API method
- `styles.css` - Added audio extraction styles

## Performance Metrics

**Typical Processing Times (per video):**
- Audio Download: 5-30 seconds (depends on video length)
- Transcription: 10-60 seconds (depends on audio length and model)
- Filtering & Parsing: 1-2 seconds
- **Total:** 16-92 seconds

**Memory Usage:**
- Whisper Model: ~500MB (base model)
- Temp Audio Files: Depends on video (typically 10-50MB)
- Database: Negligible

## Support & Debugging

For detailed logs, set environment variable:
```bash
export DEBUG=true
```

Check backend logs for `[AUDIO_EXTRACTION]` prefix for feature-specific debugging.

---

**Version:** 1.0.0
**Created:** March 2026
**Status:** Production Ready
