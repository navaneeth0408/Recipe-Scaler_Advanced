# Recipe Scaler Backend - Setup & Deployment Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Installation Steps

### 1. Clone/Navigate to Project
```bash
cd recipe-scaler-backend
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **youtube-transcript-api**: YouTube transcript fetching
- **yt-dlp**: YouTube metadata extraction
- **python-multipart**: Form data handling
- **python-dotenv**: Environment variable loading

### 4. Create Environment File (Optional)
```bash
# Create .env file
cat > .env << EOF
HOST=0.0.0.0
PORT=8000
DEBUG=false
RELOAD=true
ENVIRONMENT=development
EOF
```

### 5. Run the Server
```bash
# Option 1: Direct Python
python main.py

# Option 2: Using Uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Using python -m
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at: `http://localhost:8000`

## Accessing the API

1. **Interactive Documentation**: http://localhost:8000/api/docs
2. **ReDoc Documentation**: http://localhost:8000/api/redoc
3. **OpenAPI JSON**: http://localhost:8000/api/openapi.json
4. **Health Check**: http://localhost:8000/api/health

## Quick Test

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test ingredient extraction
curl -X POST "http://localhost:8000/api/ingredients/extract" \
  -H "Content-Type: application/json" \
  -d '{"text":"2 cups flour, 1 cup sugar","serving_size":4}'
```

## Frontend Integration

### Connecting Frontend to Backend

Update your frontend code to call the backend API:

```javascript
// Replace localhost:8000 with your backend URL
const API_URL = 'http://localhost:8000';

// Example: Extract ingredients
async function extractIngredients(text, servingSize = 4) {
  const response = await fetch(`${API_URL}/api/ingredients/extract`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      serving_size: servingSize
    })
  });
  
  return response.json();
}

// Example: Scale recipe
async function scaleRecipe(ingredients, originalServings, targetServings) {
  const response = await fetch(`${API_URL}/api/scaling/scale`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ingredients: ingredients,
      original_servings: originalServings,
      target_servings: targetServings
    })
  });
  
  return response.json();
}
```

### CORS Configuration

The backend allows requests from:
- `http://localhost:3000` (dev frontend)
- `http://localhost:5000` (dev frontend)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5000`
- `file://` (Electron/desktop apps)

To add more origins, edit `main.py`:
```python
ALLOWED_ORIGINS = [
    "http://yourdomain.com",
    "https://yourdomain.com",
    # Add more origins here
]
```

## Deployment Options

### Option 1: Local Development Server
```bash
python main.py
```
Best for: Local development and testing

### Option 2: Uvicorn with Multiple Workers
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
Best for: Production with multiple cores

### Option 3: Docker
```bash
# Build image
docker build -t recipe-scaler-api .

# Run container
docker run -p 8000:8000 recipe-scaler-api
```

### Option 4: Docker Compose
```bash
docker-compose up
```

### Option 5: Cloud Deployment

#### Heroku
```bash
heroku create your-app-name
git push heroku main
```

#### AWS EC2
1. Launch EC2 instance
2. Install Python and dependencies
3. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`
4. Use Nginx as reverse proxy
5. Set up SSL with Let's Encrypt

#### PythonAnywhere
1. Upload code to PythonAnywhere
2. Set up virtualenv
3. Configure web app with WSGI
4. Reload web app

#### Railway, Render, or Heroku Alternative
1. Connect GitHub repo
2. Set Python 3.11 as runtime
3. Command: `uvicorn main:app --host 0.0.0.0 --port 8000`
4. Deploy

## Production Deployment Checklist

### Security
- [ ] Set `DEBUG=false`
- [ ] Use HTTPS only
- [ ] Configure CORS properly (whitelist specific origins)
- [ ] Add authentication if needed
- [ ] Validate all inputs
- [ ] Use environment variables for secrets

### Performance
- [ ] Use Gunicorn or similar for production server
- [ ] Enable gzip compression
- [ ] Set up caching headers
- [ ] Use CDN for static files
- [ ] Database query optimization
- [ ] Monitor response times

### Reliability
- [ ] Set up error logging (Sentry, etc.)
- [ ] Database backups (daily)
- [ ] Uptime monitoring
- [ ] Load balancing if needed
- [ ] Rate limiting
- [ ] Graceful error handling

### Monitoring
- [ ] Application logs
- [ ] Error tracking
- [ ] Performance metrics
- [ ] Database health
- [ ] API endpoint monitoring

## Configuration Examples

### Development
```
HOST=0.0.0.0
PORT=8000
DEBUG=true
RELOAD=true
ENVIRONMENT=development
```

### Staging
```
HOST=0.0.0.0
PORT=8000
DEBUG=false
RELOAD=false
ENVIRONMENT=staging
FRONTEND_URL=https://staging.example.com
```

### Production
```
HOST=0.0.0.0
PORT=8000
DEBUG=false
RELOAD=false
ENVIRONMENT=production
FRONTEND_URL=https://example.com
```

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Module Not Found
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Database Errors
```bash
# Delete and recreate database
rm app/recipe_scaler.db
python main.py
```

### YouTube API Issues
```bash
# Update youtube libraries
pip install --upgrade youtube-transcript-api yt-dlp
```

### CORS Errors
- Check frontend URL in CORS configuration
- Ensure frontend and backend are on different ports
- Use browser console to see exact error

## Updating Dependencies

```bash
# View outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package_name

# Update all packages
pip install --upgrade -r requirements.txt
```

## Backup and Restore

### Backup Database
```bash
cp app/recipe_scaler.db app/recipe_scaler.db.backup
```

### Backup Everything
```bash
# Create archive
tar -czf recipe-scaler-backup.tar.gz recipe-scaler-backend/

# Or on Windows
# Use 7-Zip, WinRAR, or Windows Backup
```

### Restore Database
```bash
cp app/recipe_scaler.db.backup app/recipe_scaler.db
```

## Performance Tuning

### Enable Connection Pooling
Edit `app/database/db.py`:
```python
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=20,
    max_overflow=40
)
```

### Add Caching Headers
Add to relevant routes:
```python
from fastapi.responses import JSONResponse

@app.get("/api/recipes/{recipe_id}")
def get_recipe(recipe_id: str):
    # ... your logic
    return JSONResponse(
        content=recipe,
        headers={"Cache-Control": "max-age=3600"}
    )
```

### Database Indexing
Already configured for common queries:
- recipes: name, source
- ingredients: recipe_id, name
- youtube_cache: video_id

## Logging

Check logs in console output or configure file logging:
```python
# In main.py
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
```

## Monitoring with Docker

```bash
# View container logs
docker logs container_name

# Monitor container stats
docker stats container_name

# SSH into container
docker exec -it container_name /bin/bash
```

## Support & Documentation

- **API Docs**: http://localhost:8000/api/docs
- **Code Documentation**: See docstrings in each file
- **API Guide**: See API_DOCUMENTATION.md
- **Issues**: Check error messages in response

## Next Steps

1. ✅ Start the server
2. ✅ Test endpoints with Swagger UI
3. ✅ Integrate with frontend
4. ✅ Deploy to production
5. ✅ Monitor and optimize

