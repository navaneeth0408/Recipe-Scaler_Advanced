# YouTube API Key - Quick Reference Card

## ✅ What Was Done For You

```
✅ main.py         → Added: from dotenv import load_dotenv
                    Added: load_dotenv()

✅ .env            → Created: Ready for your API key
                    Placeholder: YOUTUBE_API_KEY=your_api_key_here

✅ .env.example    → Updated: Shows how to configure

✅ Documentation   → 6 comprehensive guides created

✅ Error Handling  → Already works in youtube_search.py
```

---

## ⏳ What You Need To Do (5 Minutes)

### 1️⃣ Get API Key (3 minutes)
```
https://console.cloud.google.com/

Steps:
1. Create project: "Recipe Scaler"
2. Enable: YouTube Data API v3
3. Create: API Key
4. Restrict: YouTube Data API v3 only
5. Copy: Your API key
```

### 2️⃣ Configure .env (1 minute)
```
File: recipe-scaler-backend/.env

Find:  YOUTUBE_API_KEY=your_api_key_here
Replace: YOUTUBE_API_KEY=AIzaSyDm5R8ZQ7-...

Save: Ctrl+S
```

### 3️⃣ Restart Backend (1 minute)
```powershell
cd recipe-scaler-backend
python main.py
```

---

## ✅ Verify It Works (Pick One)

### Method 1: Browser
1. Open: http://localhost:5500
2. Press: F12 → Network tab
3. Search: YouTube recipe
4. Check: Response has videos (not error)

### Method 2: Logs
Check terminal running backend:
- ✅ Should see: INFO posts to /api/youtube/search
- ❌ Should NOT see: ERROR about API key

### Method 3: PowerShell
```powershell
$body = @{query="pasta"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/youtube/search" `
  -Method POST -Headers @{"Content-Type"="application/json"} -Body $body `
  | Select-Object -ExpandProperty Content
```

---

## 🔧 Restart Command

```powershell
cd c:\Users\DELL\OneDrive\Desktop\Recipe\recipe-scaler-backend
python main.py
```

Expected:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## 📁 Key Files

| File | Location | What to Do |
|------|----------|-----------|
| .env | backend/ | **Edit this** - Add your API key |
| main.py | backend/ | **Already modified** - No action |
| youtube_search.py | backend/app/routes/ | **Already works** - No action |

---

## 🚨 Common Issues

### "YouTube API key not configured"
```
Fix:
1. Verify .env file exists
2. Verify YOUTUBE_API_KEY=... line (not commented)
3. Restart backend
```

### "Invalid API Key"
```
Fix:
1. Create new API key from Google Cloud
2. Verify YouTube Data API v3 enabled
3. Update .env with new key
4. Restart backend
```

### Changes Don't Work
```
Fix:
Get-Process python | Stop-Process -Force
cd recipe-scaler-backend
python main.py
```

---

## 📚 Documentation

| Need | File |
|------|------|
| Quick start | YOUTUBE_API_QUICK_START.md |
| Full setup | YOUTUBE_API_KEY_SETUP.md |
| Technical | YOUTUBE_API_CONFIGURATION_COMPLETE.md |
| Verify steps | YOUTUBE_API_RESTART_VERIFICATION.md |
| Summary | YOUTUBE_API_SUMMARY.md |
| Final report | YOUTUBE_API_FINAL_COMPLETION_REPORT.md |

---

## 🔐 Security

✅ **What's Secure:**
- API key in .env (not in code)
- .env in .gitignore (not committed)
- API key restricted to YouTube only
- No hardcoded secrets

❌ **What to Avoid:**
- Don't share .env file
- Don't commit .env to Git
- Don't hardcode API keys
- Don't share API key in messages

---

## 📊 Status

| Item | Status |
|------|--------|
| Code ready | ✅ YES |
| Documentation | ✅ YES |
| Error handling | ✅ YES |
| Security | ✅ YES |
| Testing | ✅ READY |
| Your API key | ⏳ TODO |

---

## 🎯 Next Steps

1. [ ] Get YouTube API key
2. [ ] Add to .env file
3. [ ] Restart backend
4. [ ] Test (optional)

**Then you're done!** 🎉

---

## 💡 Pro Tips

- Keep API key secret (like a password)
- Rotate key every 6-12 months
- Monitor quota usage
- Use quotas to prevent abuse

---

## ⚡ Quick Commands

```powershell
# Edit .env
code recipe-scaler-backend\.env

# Start backend
cd recipe-scaler-backend; python main.py

# Test API
curl -X POST http://localhost:8000/api/youtube/search `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"pasta\"}"

# Check health
curl http://localhost:8000/api/health
```

---

## 📞 Help

If stuck, see:
- YOUTUBE_API_KEY_SETUP.md (detailed guide)
- Google Cloud Console (get API key)
- Backend logs (check for errors)

---

**Status:** ✅ Ready for API key configuration

Add your API key and restart!
