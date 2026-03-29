# Backend Restart & API Key Verification - Reference Card

## Quick Start (Copy & Paste)

### Step 1: Get YouTube API Key
Go to https://console.cloud.google.com/ and follow these steps:
1. Create project → Enable YouTube Data API v3 → Create API Key → Restrict to YouTube Data API v3 → Copy key

### Step 2: Edit .env File
```powershell
# Open .env in VS Code
code c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend\.env
```

**Inside .env, find:**
```
YOUTUBE_API_KEY=your_api_key_here
```

**Replace with your actual key:**
```
YOUTUBE_API_KEY=AIzaSyDm5R8ZQ7-4xX8x1y2z3a4b5c6d7e8f9g0
```

### Step 3: Restart Backend
```powershell
cd c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

---

## Backend Commands

### Start Backend (Development)
```powershell
cd c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend
python main.py
```

### Stop Backend
In the terminal running the backend:
```
Ctrl+C
```

### Restart Backend (After .env Changes)
```powershell
# Press Ctrl+C in backend terminal to stop

cd c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend
python main.py
```

### Force Stop All Python Processes
```powershell
Get-Process python | Stop-Process -Force
```

### Check if Python is Running
```powershell
Get-Process python
```

---

## Verify Setup Works

### Method 1: Browser DevTools (Easiest)

1. **Open frontend:**
   ```
   http://localhost:5500
   ```

2. **Open Developer Tools:**
   ```
   Press F12
   ```

3. **Go to Network tab:**
   - Click Network tab in DevTools

4. **Make API call:**
   - Click "Search YouTube" button or similar
   - Or enter a recipe and click search

5. **Look for the request:**
   - Find `POST /api/youtube/search` in the requests list
   - Click on it

6. **Check Response:**
   - Click "Response" tab
   - Should see JSON with video results (title, channel, thumbnail, etc.)
   - OR see error message about invalid key

---

### Method 2: Backend Logs

**Check terminal where backend is running:**

✅ **Success** - You should see:
```
INFO:     POST http://localhost:5500 /api/youtube/search
INFO:     GET http://localhost:5500 /api/health
```

❌ **Failure** - You should NOT see:
```
ERROR:     YouTube API key not configured
ERROR:     Invalid API key
```

---

### Method 3: Direct API Test (PowerShell)

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

**Expected Output:** JSON with video results
```json
{
  "results": [
    {
      "video_id": "...",
      "title": "...",
      "channel": "...",
      "thumbnail_url": "...",
      "views": ...,
      "duration_seconds": ...,
      "published_date": "..."
    }
  ],
  "success": true
}
```

---

### Method 4: Health Check

```powershell
# Test backend is running
Invoke-WebRequest -Uri "http://localhost:8000/api/health" | Select-Object -ExpandProperty Content
```

**Expected Output:**
```json
{
  "status": "healthy",
  "message": "Recipe Scaler API is running"
}
```

---

## Environment File Locations

| File | Location | Purpose |
|------|----------|---------|
| `.env` | `recipe-scaler-backend/.env` | **YOUR** configuration (DO NOT commit) |
| `.env.example` | `recipe-scaler-backend/.env.example` | Template for team members |
| `main.py` | `recipe-scaler-backend/main.py` | Loads .env at startup |

---

## .env File Reference

**File:** `c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend\.env`

**Content:**
```env
# Recipe Scaler Backend Configuration

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Environment (development, staging, production)
ENVIRONMENT=development

# Debug Mode (true for development, false for production)
DEBUG=false

# Auto-reload on file changes (development only)
RELOAD=true

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# ============================================================================
# YouTube Data API Configuration (Required for YouTube Search)
# ============================================================================
YOUTUBE_API_KEY=your_api_key_here
```

**To edit:**
```powershell
code c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend\.env
```

---

## Error Messages & Solutions

### Error: "YouTube API key not configured"

```
Error: YouTube API key not configured. Set YOUTUBE_API_KEY environment variable.
Status: 500
```

**Solutions:**
1. ✅ Verify `.env` file exists
2. ✅ Verify `YOUTUBE_API_KEY=...` line is present (not commented)
3. ✅ Verify API key value is not empty
4. ✅ Restart backend: `python main.py`

---

### Error: "Invalid API Key"

```
Error: Invalid API key. Please check your API key is correct.
```

**Solutions:**
1. ✅ Verify API key is copied correctly (no extra spaces)
2. ✅ Verify YouTube Data API v3 is ENABLED
3. ✅ Create new API key from Google Cloud Console
4. ✅ Ensure key is restricted to YouTube Data API v3

---

### Error: "API Key Quota Exceeded"

```
Error: The request cannot be completed because you have exceeded your API quota.
```

**Solutions:**
1. ✅ Wait for quota reset (typically 24 hours)
2. ✅ Check quota usage: Google Cloud Console → APIs & Services → YouTube Data API v3 → Quota
3. ✅ Upgrade to paid plan for higher quota

---

## File Modifications Summary

### main.py (Lines 10-13 Added)

```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

### .env (New File Created)

```
YOUTUBE_API_KEY=your_api_key_here
```

### .env.example (Updated)

```
YOUTUBE_API_KEY=your_api_key_here
```

---

## Troubleshooting Checklist

- [ ] .env file exists in `recipe-scaler-backend/` directory
- [ ] YOUTUBE_API_KEY line is present in .env
- [ ] YOUTUBE_API_KEY line is NOT commented out (#)
- [ ] API key value is not empty
- [ ] API key is pasted without extra spaces
- [ ] Backend was restarted after .env creation
- [ ] No "YouTube API key not configured" errors in backend logs
- [ ] Browser DevTools shows 200 status for /api/youtube/search
- [ ] Network response contains video results (not error)

---

## Security Notes

✅ **DO:**
- ✅ Keep API key in `.env` file
- ✅ Add `.env` to `.gitignore` (already done)
- ✅ Restrict API key to YouTube Data API v3 only
- ✅ Use environment variables in production

❌ **DON'T:**
- ❌ Never hardcode API key in source code
- ❌ Never commit `.env` to Git
- ❌ Never share API key in messages or docs
- ❌ Never use unrestricted API keys

---

## Testing Checklist

After setup, verify these work:

- [ ] Backend starts without errors: `python main.py`
- [ ] Health check works: http://localhost:8000/api/health
- [ ] YouTube search endpoint responds: POST /api/youtube/search
- [ ] Frontend can search recipes: http://localhost:5500
- [ ] Browser DevTools shows no CORS errors
- [ ] Backend logs show successful API calls
- [ ] Video results include title, channel, thumbnail, views

---

## Full Documentation

For complete setup guide with screenshots:
- [YOUTUBE_API_KEY_SETUP.md](YOUTUBE_API_KEY_SETUP.md) - Detailed guide with screenshots
- [YOUTUBE_API_QUICK_START.md](YOUTUBE_API_KEY_QUICK_START.md) - Quick summary
- [YOUTUBE_API_CONFIGURATION_COMPLETE.md](YOUTUBE_API_CONFIGURATION_COMPLETE.md) - Technical details

---

## Summary

| Step | Command | Status |
|------|---------|--------|
| 1. Get API Key | https://console.cloud.google.com/ | ⏳ Manual |
| 2. Edit .env | `code recipe-scaler-backend\.env` | ⏳ Manual |
| 3. Restart | `python main.py` | ✅ Ready |
| 4. Verify | DevTools → Network → /api/youtube/search | ✅ Ready |

**All code changes are complete. Just add your API key and restart!** 🚀

