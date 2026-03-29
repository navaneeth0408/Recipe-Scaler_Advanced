# FastAPI Installation & Module Error - Diagnostic Guide

## Problem Analysis

**Error Encountered:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Root Cause:** FastAPI and other dependencies were not installed in the Python environment.

---

## Why This Error Occurs

| Reason | Explanation |
|--------|-------------|
| **Missing Installation** | Dependencies from requirements.txt were not installed |
| **Wrong Python Interpreter** | Running with global Python instead of virtual environment |
| **Broken Virtual Environment** | venv exists but packages weren't installed |
| **pip Not Updated** | Old pip version causing installation issues |

---

## Solution Applied

### Step 1: Configure Virtual Environment ✓
Your workspace has a virtual environment at:
```
.venv/Scripts/python.exe
```

### Step 2: Install All Dependencies ✓
Installed from requirements.txt:
- ✓ fastapi (0.128.0)
- ✓ uvicorn (0.40.0)
- ✓ sqlalchemy (2.0.46)
- ✓ pydantic (2.12.5)
- ✓ pydantic-settings
- ✓ python-dotenv
- ✓ httpx
- ✓ youtube-transcript-api
- ✓ google-api-python-client
- ✓ pymongo
- ✓ motor
- ✓ python-multipart
- ✓ python-cors

### Step 3: Verify Installation ✓
```
[OK] All critical dependencies installed successfully!
```

---

## How to Run Your FastAPI Backend

### Option 1: Direct Python Execution (Recommended for Development)

**Windows PowerShell:**
```powershell
# Activate virtual environment (optional - auto-used)
.\.venv\Scripts\Activate.ps1

# Run the application
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
```

### Option 2: Using Uvicorn Directly

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Parameters Explained:**
- `main:app` = module:app instance
- `--reload` = auto-restart on code changes
- `--host 0.0.0.0` = accessible from network
- `--port 8000` = runs on port 8000

### Option 3: Using Python Module Syntax

```powershell
python -m uvicorn main:app --reload
```

---

## Verification Steps

### 1. Check Virtual Environment is Active
```powershell
# In PowerShell, you should see (.venv) in prompt:
# (.venv) C:\Users\DELL\OneDrive\Desktop\recipe-scaler-backend>
```

### 2. Verify Each Package
```python
# Run in PowerShell
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
```

### 3. Check All Requirements Installed
```powershell
pip list
```

### 4. Verify Database Module
```python
python -c "from app.database.db import engine; print('Database configured correctly')"
```

---

## Test Your API

Once the backend is running at `http://localhost:8000`:

### Access API Documentation
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI JSON: `http://localhost:8000/api/openapi.json`

### Test Health Check
```powershell
# Using PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
```

Or use curl:
```powershell
curl http://localhost:8000/health
```

---

## Troubleshooting

### Issue 1: "Cannot find .venv folder"
**Solution:** Virtual environment doesn't exist
```powershell
# Create new virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Issue 2: "ModuleNotFoundError" still occurs
**Solution:** Wrong Python interpreter
```powershell
# Verify which Python is active
python --version
python -c "import sys; print(sys.executable)"

# Should show: C:\Users\DELL\OneDrive\Desktop\recipe-scaler-backend\.venv\Scripts\python.exe
```

### Issue 3: "Port 8000 already in use"
**Solution:** Use different port
```powershell
python main.py --port 8001
```

Or kill the process:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 4: "Permission denied" on .venv activation
**Solution:** Adjust PowerShell execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 5: "pip: command not found"
**Solution:** Use Python module syntax
```powershell
python -m pip install -r requirements.txt
```

---

## Virtual Environment Paths (Windows)

Your virtual environment structure:
```
.venv/
├── Scripts/
│   ├── python.exe          ← Python interpreter
│   ├── pip.exe             ← Package manager
│   ├── uvicorn.exe         ← ASGI server
│   └── activate.ps1        ← Activation script
├── Lib/
│   └── site-packages/      ← Installed packages
└── pyvenv.cfg
```

---

## Complete Startup Sequence

```powershell
# Step 1: Navigate to project
cd C:\Users\DELL\OneDrive\Desktop\recipe-scaler-backend

# Step 2: Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Step 3: Verify Python
python --version

# Step 4: Verify pip
pip --version

# Step 5: Install/Update dependencies
pip install -r requirements.txt

# Step 6: Run application
python main.py

# Expected: 
# INFO:     Uvicorn running on http://127.0.0.1:8000
# API ready to accept requests
```

---

## Production Considerations

### For Windows Server Deployment

**Option 1: Windows Service (NSSM)**
```powershell
# Install NSSM (Non-Sucking Service Manager)
choco install nssm

# Create service
nssm install RecipeScalerAPI "C:\path\to\.venv\Scripts\python.exe" "main.py"

# Start service
nssm start RecipeScalerAPI
```

**Option 2: Docker Container**
See your Dockerfile for containerized deployment.

**Option 3: Uvicorn with Gunicorn**
```powershell
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

---

## Summary of Commands

| Task | Command |
|------|---------|
| Activate venv | `.\.venv\Scripts\Activate.ps1` |
| Install deps | `pip install -r requirements.txt` |
| Run backend | `python main.py` |
| Run with uvicorn | `uvicorn main:app --reload` |
| Check FastAPI | `python -c "import fastapi; print(fastapi.__version__)"` |
| List packages | `pip list` |
| Freeze current | `pip freeze > requirements.txt` |

---

## Status

✓ **All dependencies installed successfully**
✓ **Virtual environment configured**
✓ **FastAPI module verified (0.128.0)**
✓ **Uvicorn ASGI server installed (0.40.0)**
✓ **Backend ready to run without module errors**

**Next Step:** Execute `python main.py` in your terminal to start the API server.
