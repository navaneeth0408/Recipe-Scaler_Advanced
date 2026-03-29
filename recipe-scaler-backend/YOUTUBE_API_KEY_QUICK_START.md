# YouTube API Key - Quick Setup Guide

## 🚀 Quick Summary

Your Recipe Scaler backend is now configured to **safely load YouTube API keys from environment variables**. Here's what was changed:

### What Changed:
1. ✅ `main.py` - Added `from dotenv import load_dotenv` and `load_dotenv()` call
2. ✅ `.env` file - Created with placeholder for your API key
3. ✅ `.env.example` - Updated with clear instructions
4. ✅ Error handling - Already in place in `youtube_search.py`

### What DIDN'T Change:
- ✅ No hardcoded API keys in source code
- ✅ No breaking changes to any features
- ✅ All other endpoints work normally
- ✅ `.env` is in `.gitignore` (not committed to Git)

---

## 📋 Setup Checklist (5 Minutes)

### Step 1: Get a YouTube API Key (3 minutes)

Go to [Google Cloud Console](https://console.cloud.google.com/) and:

1. Create a new project (name: "Recipe Scaler")
2. Go to **APIs & Services → Library**
3. Search for and enable **YouTube Data API v3**
4. Go to **Credentials → + Create Credentials → API Key**
5. Copy your API key
6. **Restrict it:** In Credentials, select your key → **API restrictions** → YouTube Data API v3 only → **Save**

### Step 2: Add API Key to .env File (2 minutes)

Open the `.env` file in the backend directory:
```
c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend\.env
```

Find this line:
```
YOUTUBE_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual API key:
```
YOUTUBE_API_KEY=AIzaSyDm5R8ZQ7-4xX9z8x1y2z3a4b5c6d7e8f9g
```

**Save the file.** ✅

### Step 3: Restart Backend (1 minute)

```powershell
cd c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend

# Stop old process (Ctrl+C if running), then:
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## ✅ Verify It Works

### Test 1: Browser DevTools (Easiest)

1. Open frontend: http://localhost:5500
2. Press **F12** → **Network** tab
3. Make any API call (Search YouTube, Fetch Video, etc.)
4. Look for `/api/youtube/search` request
5. Click it → **Response** tab → Should see video results, NOT an error

### Test 2: Backend Logs

Check the terminal running `python main.py`:
- ✅ Should see POST requests to `/api/youtube/search` returning HTTP 200
- ❌ Should NOT see "YouTube API key not configured" error

### Test 3: Direct API Test

```powershell
$body = @{ query = "pasta recipe"; max_results = 3 } | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://localhost:8000/api/youtube/search" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

Should return video results with titles, channels, thumbnails, etc.

---

## 🔧 Technical Details

### Environment Variable Loading (main.py)

```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

This call loads all variables from `.env` into `os.environ`.

### How the API Key is Used (youtube_search.py)

```python
# Get API key from environment
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# Check if configured
if not YOUTUBE_API_KEY:
    raise HTTPException(
        status_code=500,
        detail="YouTube API key not configured. Set YOUTUBE_API_KEY environment variable."
    )
```

### How It's Passed to YouTube API

```python
params = {
    'part': 'snippet',
    'q': search_term,
    'type': 'video',
    'key': YOUTUBE_API_KEY  # ← Safely passed here
}
```

---

## ❌ Troubleshooting

### "YouTube API key not configured" Error

**Cause:** `.env` file not found or API key not set

**Fix:**
1. Verify `.env` exists in `recipe-scaler-backend/`
2. Verify `YOUTUBE_API_KEY=...` line (not commented)
3. Restart backend (`Ctrl+C` then `python main.py`)

### "Invalid API Key" Error

**Cause:** API key is wrong or doesn't have YouTube API enabled

**Fix:**
1. Copy API key again from Google Cloud Console
2. Verify YouTube Data API v3 is ENABLED
3. Verify API key is RESTRICTED to YouTube Data API v3

### Backend Starts But Changes Don't Take Effect

**Cause:** Python caching old environment

**Fix:**
```powershell
Get-Process python | Stop-Process -Force
cd recipe-scaler-backend
python main.py
```

---

## 🔐 Security Notes

### ✅ What You're Doing Right:

- ✅ API key in `.env` (not in code)
- ✅ `.env` in `.gitignore` (not committed)
- ✅ Using restricted API key (YouTube Data API only)
- ✅ Key only loaded at runtime (not compiled into binary)

### ❌ Avoid:

- ❌ Never commit `.env` to Git
- ❌ Never hardcode API key in `main.py` or any source file
- ❌ Never share API key in messages or documentation
- ❌ Never use unrestricted API keys

---

## 📚 Full Documentation

For complete setup instructions with screenshots, see:
[YOUTUBE_API_KEY_SETUP.md](YOUTUBE_API_KEY_SETUP.md)

---

## What's Next?

✅ YouTube search is now enabled!

Your backend endpoints now work:
- `POST /api/youtube/search` - Search YouTube for recipes
- `POST /api/youtube/extract` - Extract video metadata
- `POST /api/ingredients/parse` - Parse ingredients
- `POST /api/recipes/scale` - Scale recipes
- And all other endpoints...

The frontend can now fetch and search recipes from YouTube without errors!

---

## Files Changed

| File | Change | Why |
|------|--------|-----|
| `main.py` | Added `load_dotenv()` import/call | Enable .env loading |
| `.env` | Created with API key placeholder | Store sensitive config |
| `.env.example` | Updated with instructions | Guide for setup |

No other files modified. All changes are safe and non-breaking. ✅

