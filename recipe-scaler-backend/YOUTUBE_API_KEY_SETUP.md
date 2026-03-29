# YouTube API Key Configuration Guide

## Overview

The Recipe Scaler backend requires a **YouTube API Key** to enable the YouTube search functionality (`/api/youtube/search` endpoint). This guide provides step-by-step instructions for obtaining and configuring the API key securely.

---

## Part 1: Obtain a YouTube API Key

### Step 1.1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account (create one if needed)
3. Click on the **Project** dropdown (top left)
4. Click **NEW PROJECT**
5. Enter a project name (e.g., `Recipe Scaler`)
6. Click **CREATE**
7. Wait for the project to be created (may take a minute)

### Step 1.2: Enable YouTube Data API v3

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for `YouTube Data API v3`
3. Click on **YouTube Data API v3**
4. Click **ENABLE**
5. You'll be redirected to the API details page

### Step 1.3: Create an API Key

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** (top left)
3. Select **API Key**
4. A dialog will appear with your new API key
5. **COPY the API key** and save it somewhere safe
6. Click **CLOSE**

### Step 1.4: Restrict the API Key (Recommended)

⚠️ **Important:** Restricting your API key prevents unauthorized use and protects your quota.

1. In **Credentials** page, find your newly created API key in the list
2. Click on it to open its settings
3. Under **Application restrictions**, select:
   - **API restrictions** → **Restrict key**
   - Select **YouTube Data API v3** from the dropdown
4. Click **SAVE**

Your API key is now secure and restricted to YouTube Data API only.

---

## Part 2: Configure the API Key in Backend

### Option A: Using .env File (Recommended for Development)

1. Navigate to the backend directory:
   ```powershell
   cd c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend
   ```

2. Create a `.env` file (if it doesn't exist):
   ```powershell
   Copy-Item .env.example .env
   ```

3. Open `.env` in your text editor and find the line:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

4. Replace `your_api_key_here` with your actual API key:
   ```
   YOUTUBE_API_KEY=AIzaSyDm5R8ZQ7-4xX9z8x1y2z3a4b5c6d7e8f9g
   ```

5. **IMPORTANT:** Never commit `.env` to Git! It's already in `.gitignore`

### Option B: Using Environment Variables (For Production/Docker)

#### Windows (PowerShell)

```powershell
# Set environment variable for current session
$env:YOUTUBE_API_KEY = "your_api_key_here"

# Verify it's set
$env:YOUTUBE_API_KEY
```

#### Windows (Command Prompt)

```cmd
setx YOUTUBE_API_KEY your_api_key_here
```

After setting, restart your terminal or IDE for changes to take effect.

#### Linux/Mac

```bash
export YOUTUBE_API_KEY="your_api_key_here"

# Or permanently in ~/.bashrc or ~/.zshrc
echo 'export YOUTUBE_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Part 3: Verify the Backend Configuration

### Check if python-dotenv is Installed

Verify that `python-dotenv` is already in requirements.txt:

```powershell
Get-Content requirements.txt | Select-String "python-dotenv"
```

You should see:
```
python-dotenv==1.0.0
```

If not present, install it:
```powershell
pip install python-dotenv==1.0.0
```

### Verify main.py Loads .env

Check that `main.py` has the following import (at the top, after other imports):

```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

**Status:** ✅ Already implemented in your main.py (lines 10-12)

---

## Part 4: Restart the Backend

After configuring the API key, restart the FastAPI backend:

### Terminal 1: Stop Current Backend (if running)

```powershell
# Press Ctrl+C in the terminal running the backend
```

### Terminal 2: Start Backend with API Key Loaded

```powershell
cd c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend

# Start the backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

If the API key is configured, you should **NOT** see any warning about missing YouTube API key.

---

## Part 5: Verify the Fix

### Method 1: Browser Network Inspector (Recommended)

1. Open frontend: http://localhost:5500
2. Press **F12** to open Developer Tools
3. Go to **Network** tab
4. Search for a recipe (e.g., click "Fetch YouTube Video" or "Search YouTube")
5. Look for request to `POST /api/youtube/search`
6. Check the **Response** tab

**Expected Success Response:**
```json
{
  "results": [
    {
      "video_id": "...",
      "title": "Recipe Title",
      "channel": "Channel Name",
      "thumbnail_url": "https://...",
      "views": 123456,
      "duration_seconds": 600,
      "published_date": "2024-01-15",
      "relevance_score": 95.5
    }
  ],
  "success": true
}
```

**Expected Error Response (if API key missing):**
```json
{
  "detail": "YouTube API key not configured. Set YOUTUBE_API_KEY environment variable."
}
```

### Method 2: Backend Logs

Check the terminal running the backend:

✅ **Success (no errors):**
```
INFO:     POST http://localhost:5500 /api/youtube/search
INFO:     Returned status code 200
```

❌ **Error:**
```
ERROR: YouTube API key not configured
```

### Method 3: Direct API Test (curl)

Open PowerShell and test the API directly:

```powershell
# Test YouTube search endpoint
$body = @{
    query = "pasta recipe"
    max_results = 3
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://localhost:8000/api/youtube/search" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body | Select-Object -ExpandProperty Content
```

**Expected Output:**
```json
{
  "results": [...],
  "success": true
}
```

---

## Part 6: Troubleshooting

### Issue: "YouTube API key not configured" Error

**Cause:** The API key is not being loaded by the backend.

**Solutions:**
1. ✅ Verify `.env` file exists in backend directory
2. ✅ Verify `YOUTUBE_API_KEY=...` line is present and uncommented
3. ✅ Check for typos (exact match required)
4. ✅ Restart the backend after creating/modifying `.env`
5. ✅ Verify `python-dotenv` is installed: `pip show python-dotenv`

### Issue: "Invalid API Key" Error

**Cause:** The API key is invalid or doesn't have YouTube API v3 access.

**Solutions:**
1. ✅ Verify the API key was copied correctly (no extra spaces)
2. ✅ Check that YouTube Data API v3 is enabled in Google Cloud Console
3. ✅ Verify the API key has **API restrictions** set to YouTube Data API v3 only
4. ✅ Create a new API key if the current one is invalid

### Issue: "Quota Exceeded" Error

**Cause:** YouTube API quota limit reached (typically 10,000 units/day for free tier).

**Solutions:**
1. ✅ Check quota usage in Google Cloud Console → APIs & Services → YouTube Data API v3
2. ✅ Wait until the quota resets (typically daily at midnight Pacific Time)
3. ✅ Upgrade to a paid plan for higher quotas

### Issue: Backend Starts But No Changes

**Cause:** Backend process caching old environment.

**Solutions:**
1. ✅ Kill all Python processes: `Get-Process python | Stop-Process -Force`
2. ✅ Clear Python cache: `Remove-Item -Path "*/__pycache__" -Recurse`
3. ✅ Restart terminal/IDE to ensure environment variables are loaded
4. ✅ Restart the backend

---

## Part 7: Security Best Practices

### ✅ DO:

- ✅ Keep the API key in `.env` file (not in code)
- ✅ Add `.env` to `.gitignore` (already done)
- ✅ Restrict API key to YouTube Data API v3 only
- ✅ Rotate API key every 6-12 months
- ✅ Use environment variables in production

### ❌ DON'T:

- ❌ Commit `.env` to Git
- ❌ Share your API key in messages, issues, or documentation
- ❌ Use unrestricted API keys (without API restrictions)
- ❌ Leave API key in client-side code (frontend)
- ❌ Use a shared/public API key for production

---

## Part 8: Code Reference

### How the API Key is Loaded

**File:** [main.py](main.py#L10-L12)
```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

**File:** [youtube_search.py](app/routes/youtube_search.py#L17)
```python
# Get YouTube API key from environment
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
```

### How the API Key is Used

**File:** [youtube_search.py](app/routes/youtube_search.py#L267-L270)
```python
if not YOUTUBE_API_KEY:
    raise HTTPException(
        status_code=500,
        detail="YouTube API key not configured. Set YOUTUBE_API_KEY environment variable."
    )
```

The API key is then used in YouTube API requests:

```python
params = {
    'part': 'snippet',
    'q': search_term,
    'type': 'video',
    'key': YOUTUBE_API_KEY  # ← API key included here
}
```

---

## Summary Checklist

- [ ] Created Google Cloud project
- [ ] Enabled YouTube Data API v3
- [ ] Generated API key
- [ ] Restricted API key to YouTube Data API v3
- [ ] Created `.env` file from `.env.example`
- [ ] Added API key to `.env` file
- [ ] Restarted backend (with API key loaded)
- [ ] Verified API key works in browser DevTools
- [ ] Tested YouTube search functionality
- [ ] Confirmed no "API key not configured" errors
- [ ] .env file is in `.gitignore` (not committed to Git)

---

## Next Steps

✅ **YouTube search is now enabled!**

Your Recipe Scaler backend can now:
- Search YouTube for recipe videos
- Extract video metadata (title, channel, thumbnail)
- Filter and rank results by relevance
- Support pagination through search results

The frontend API client (`api-client.js`) already has support for this through the `searchYouTube()` method.

---

## Support

If you encounter issues:

1. Check the **Troubleshooting** section above (Part 6)
2. Review backend logs: `python main.py` in terminal
3. Check browser DevTools: Press F12 → Console tab
4. Verify `.env` file exists and has correct API key
5. Restart backend after any `.env` changes

---

## Files Modified

- ✅ `main.py` - Added `from dotenv import load_dotenv` and `load_dotenv()` call
- ✅ `.env.example` - Uncommented and documented `YOUTUBE_API_KEY` configuration
- ✅ `app/routes/youtube_search.py` - Already has proper error handling for missing API key

All changes are backward-compatible and non-breaking.

