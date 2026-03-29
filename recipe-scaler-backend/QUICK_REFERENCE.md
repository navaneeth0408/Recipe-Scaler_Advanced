# Quick Reference Guide - Recipe Scaler Backend API

## 🚀 Getting Started (30 seconds)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run
python main.py

# 3. Visit
http://localhost:8000/api/docs
```

## 📍 API Base URL
```
http://localhost:8000
```

## 🔌 Core Endpoints (Quick Reference)

### Extract Ingredients
```bash
POST /api/ingredients/extract
Body: { "text": "2 cups flour, 1 cup sugar", "serving_size": 4 }
```

### Scale Recipe
```bash
POST /api/scaling/scale
Body: {
  "ingredients": [{"name": "flour", "quantity": 2.0, "unit": "cup"}],
  "original_servings": 4,
  "target_servings": 8
}
```

### Create Recipe
```bash
POST /api/recipes/create
Body: {
  "name": "Cookie Recipe",
  "ingredients": [...],
  "servings": 24,
  "source": "manual"
}
```

### Get YouTube Data
```bash
POST /api/youtube/extract
Body: {
  "url": "https://www.youtube.com/watch?v=...",
  "extract_ingredients": true
}
```

### Convert Units
```bash
POST /api/scaling/convert-unit?quantity=16&from_unit=tablespoon&to_unit=cup
```

### List Recipes
```bash
GET /api/recipes?skip=0&limit=50
```

## 📊 Data Formats

### Ingredient
```json
{
  "name": "flour",
  "quantity": 2.0,
  "unit": "cup",
  "notes": "all-purpose"
}
```

### Recipe
```json
{
  "id": "uuid",
  "name": "Recipe Name",
  "ingredients": [...],
  "servings": 4,
  "source": "manual|youtube",
  "created_at": "2024-01-23T10:30:00",
  "updated_at": "2024-01-23T10:30:00"
}
```

## 🎯 Common Units

**Volume**: cup, tablespoon, teaspoon, milliliter, liter  
**Weight**: gram, kilogram, ounce, pound  
**Count**: whole, pinch, dash  

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `kill -9 $(lsof -t -i:8000)` or change PORT env var |
| Module not found | `pip install --upgrade -r requirements.txt` |
| CORS error | Check frontend URL in main.py |
| Database error | Delete `app/recipe_scaler.db`, restart server |
| YouTube issues | Update libs: `pip install --upgrade youtube-transcript-api yt-dlp` |

## 📁 Project Structure

```
app/
├── models/schemas.py       - Data validation
├── database/db.py          - Database setup
├── services/               - Business logic
│   ├── ingredient_service.py
│   ├── scaling_service.py
│   └── youtube_service.py
└── routes/                 - API endpoints
    ├── ingredients.py
    ├── scaling.py
    ├── recipes.py
    └── youtube.py
```

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, route registration |
| `requirements.txt` | Python dependencies |
| `API_DOCUMENTATION.md` | Full API reference |
| `SETUP_GUIDE.md` | Deployment & setup |
| `.env.example` | Configuration template |

## 🌐 Frontend Integration

```javascript
const API = 'http://localhost:8000';

// Extract ingredients
async function extract(text) {
  return fetch(`${API}/api/ingredients/extract`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text, serving_size: 4})
  }).then(r => r.json());
}

// Scale recipe
async function scale(ingredients, from, to) {
  return fetch(`${API}/api/scaling/scale`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      ingredients,
      original_servings: from,
      target_servings: to
    })
  }).then(r => r.json());
}

// Save recipe
async function saveRecipe(recipe) {
  return fetch(`${API}/api/recipes/create`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(recipe)
  }).then(r => r.json());
}
```

## ⚙️ Configuration

Create `.env` file:
```
HOST=0.0.0.0
PORT=8000
DEBUG=false
RELOAD=true
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
```

Or use environment variables:
```bash
export HOST=0.0.0.0
export PORT=8000
python main.py
```

## 🐳 Docker

```bash
# Build
docker build -t recipe-scaler-api .

# Run
docker run -p 8000:8000 recipe-scaler-api

# Or with Docker Compose
docker-compose up
```

## 📋 Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (validation error) |
| 404 | Not found |
| 500 | Server error |

## 🔗 Useful Links

- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI**: http://localhost:8000/api/openapi.json

## 📦 Install From Scratch

```bash
# 1. Navigate to project
cd recipe-scaler-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run server
python main.py

# 5. Open browser
http://localhost:8000/api/docs
```

## 🔄 Common Workflows

### Extract & Scale
```javascript
// 1. Extract ingredients from text
const extracted = await fetch('/api/ingredients/extract', {
  method: 'POST',
  body: JSON.stringify({text: '2 cups flour, 1 cup sugar'})
}).then(r => r.json());

// 2. Scale the ingredients
const scaled = await fetch('/api/scaling/scale', {
  method: 'POST',
  body: JSON.stringify({
    ingredients: extracted.ingredients,
    original_servings: 4,
    target_servings: 8
  })
}).then(r => r.json());
```

### YouTube to Recipe
```javascript
// 1. Get YouTube data
const yt = await fetch('/api/youtube/extract', {
  method: 'POST',
  body: JSON.stringify({
    url: 'https://youtube.com/watch?v=...',
    extract_ingredients: true
  })
}).then(r => r.json());

// 2. Save as recipe
const recipe = await fetch('/api/recipes/create', {
  method: 'POST',
  body: JSON.stringify({
    name: yt.metadata.title,
    ingredients: yt.ingredients,
    servings: 4,
    source: 'youtube',
    source_url: 'https://youtube.com/watch?v=...'
  })
}).then(r => r.json());
```

### Save & Retrieve Recipe
```javascript
// Create
const recipe = await fetch('/api/recipes/create', {
  method: 'POST',
  body: JSON.stringify({...})
}).then(r => r.json());

// Get
const stored = await fetch(`/api/recipes/${recipe.recipe.id}`).then(r => r.json());

// Update
await fetch(`/api/recipes/${recipe.recipe.id}`, {
  method: 'PUT',
  body: JSON.stringify({...})
});

// Delete
await fetch(`/api/recipes/${recipe.recipe.id}`, {method: 'DELETE'});
```

## 📞 Need Help?

1. Check Swagger UI: http://localhost:8000/api/docs
2. Read API docs: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
3. Setup guide: [SETUP_GUIDE.md](./SETUP_GUIDE.md)
4. Check error message in API response

## ✅ Pre-Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Server starts: `python main.py`
- [ ] Swagger UI accessible: http://localhost:8000/api/docs
- [ ] Health check works: http://localhost:8000/api/health
- [ ] Test endpoints in Swagger
- [ ] Frontend integration tested
- [ ] Database created: `app/recipe_scaler.db`
- [ ] CORS configured for frontend domain
- [ ] Environment variables set

---

**Ready to deploy!** Questions? Check the documentation files or Swagger UI.
