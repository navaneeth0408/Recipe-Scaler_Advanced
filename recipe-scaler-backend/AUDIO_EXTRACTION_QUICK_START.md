# Audio Extraction Feature - Quick Start Guide

## 🎯 What This Feature Does

Extract ingredients directly from YouTube video **audio** when the video has no description or transcript available.

```
YouTube Video Audio → Whisper STT → Ingredient Detection → Structured Ingredients
```

## 🚀 Quick Setup (5 minutes)

### 1. Install System Dependencies

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
```bash
choco install ffmpeg
```

### 2. Install Python Dependencies

```bash
cd recipe-scaler-backend
pip install -r requirements.txt
```

New packages added:
- `yt-dlp` - Download YouTube audio
- `faster-whisper` - Speech-to-text
- `ffmpeg-python` - Audio processing

### 3. Start Backend

```bash
python main.py
```

Should start on `http://localhost:8000`

### 4. Test Feature

1. Open frontend in browser
2. Enter a YouTube cooking video URL
3. Click **🎤 Audio** button
4. Watch the extraction stages:
   - ⏳ Downloading video audio...
   - 🎤 Transcribing speech...
   - 🔍 Extracting ingredients...
5. View extracted ingredients

## 📝 Usage Examples

### Example 1: Simple Cooking Video
- **Video:** Any cooking tutorial on YouTube
- **Action:** Click "🎤 Audio" button
- **Result:** Ingredients spoken in video are extracted

### Example 2: Videos Without Descriptions
- **Scenario:** Video has no description text
- **Solution:** Use audio extraction instead of description
- **Result:** Same ingredient extraction, different method

### Example 3: Testing
```bash
# Test with a public cooking video
# E.g., "Easy Pasta Recipe" or "Chocolate Chip Cookies"
```

## 🔧 Configuration Options

### Optional Environment Variables

Create `.env` file:
```env
# Whisper model size (tiny, base, small, medium, large)
# base = good balance of speed and accuracy
WHISPER_MODEL=base

# Device (auto, cpu, cuda)
WHISPER_DEVICE=auto

# Temp directory for audio files
TEMP_DIR=./temp
```

## 🎬 Feature Walkthrough

### On Frontend

1. **Button Location**
   - YouTube Link tab
   - Next to "Fetch Ingredients" button
   - Green button with microphone icon

2. **Processing Stages**
   - Real-time progress display
   - Three stages with emoji icons
   - Auto-hides after completion

3. **Results**
   - Video title displayed
   - Full transcript shown (optional)
   - Ingredients extracted and listed
   - Can scale recipe immediately

### API Endpoint

```
POST /api/youtube/extract-audio-ingredients

Request:
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}

Response:
{
  "video_id": "...",
  "video_title": "...",
  "transcript": "...",
  "ingredients": [
    {"name": "flour", "quantity": 2.0, "unit": "cup"},
    ...
  ],
  "success": true
}
```

## 🛑 Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid YouTube URL" | Bad URL format | Check URL is valid YouTube link |
| "Failed to download audio" | Private/restricted video | Use public cooking video |
| "Unable to transcribe" | Audio too unclear | Try video with clear spoken ingredients |
| "No ingredients detected" | No ingredient mentions | Video must mention ingredients |

## ⚡ Performance Tips

### Faster Processing
- Use shorter videos (under 30 minutes)
- Videos with clear spoken ingredients
- Minimal background music/noise

### Reduce Memory Usage
- Restart backend between heavy processing
- Use `tiny` or `small` Whisper model instead of `base`

### Bandwidth Optimization
- Cached transcripts skip download on repeat
- Audio auto-deleted after processing

## 📊 How It Works (Technical)

```
1. URL Validation
   ↓
2. Check if cached (yes → skip to 7)
   ↓
3. Download video audio (yt-dlp)
   ↓
4. Convert to WAV format
   ↓
5. Transcribe speech (Whisper)
   ↓
6. Cache transcript in database
   ↓
7. Filter for ingredient sentences
   ↓
8. Parse structured ingredients
   ↓
9. Return response
```

## 🔍 What Gets Recognized

### Measurement Units
- Cups, tablespoons, teaspoons
- Grams, ounces, pounds
- Milliliters, liters
- Pinch, dash, handful

### Actions
- "Add 2 cups flour"
- "Mix in the eggs"
- "Chop the onions"
- "Use olive oil"

### Ingredients
- Flour, sugar, salt, pepper
- Butter, oil, water, milk
- Chicken, beef, eggs
- Vegetables, herbs, spices

## 💾 Database Caching

Transcripts are cached automatically:
- **Key:** YouTube video ID
- **Stored:** Full transcript + metadata
- **Benefit:** Skip expensive processing for repeated videos
- **Storage:** SQLite local database

## 🐛 Troubleshooting

### Issue: "ffmpeg not installed"
```bash
# Check if installed
ffmpeg -version

# If not, install:
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: choco install ffmpeg
```

### Issue: "Whisper model download failed"
- Check internet connection
- First use downloads ~140MB model
- Takes 1-2 minutes first time

### Issue: "No ingredients detected"
- Video may not mention ingredients
- Try another cooking video
- Check video has clear audio

### Issue: "Memory error"
- Restart backend
- Use smaller model (`tiny` instead of `base`)
- Process shorter videos

## 📚 Additional Resources

- **Main Documentation:** `AUDIO_EXTRACTION_FEATURE.md`
- **API Docs:** `http://localhost:8000/api/docs` (after starting backend)
- **Backend Logs:** Check console for `[AUDIO_EXTRACTION]` prefix

## ✅ Checklist

- [ ] ffmpeg installed
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend running (`python main.py`)
- [ ] Frontend accessible
- [ ] YouTube URL entered
- [ ] "🎤 Audio" button clicked
- [ ] Stages show processing
- [ ] Ingredients extracted successfully

## 🎉 You're All Set!

The audio extraction feature is ready to use. Start with any public cooking video and extract ingredients directly from the audio!

---

**Need Help?**
- Check backend logs for `[AUDIO_EXTRACTION]` messages
- Verify all dependencies installed: `pip list`
- Test with different videos to isolate issues
- Check `AUDIO_EXTRACTION_FEATURE.md` for detailed docs
