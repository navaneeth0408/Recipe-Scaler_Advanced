# Recipe Scaler Backend API

A comprehensive REST API for recipe management, ingredient extraction, and recipe scaling. Built with FastAPI, SQLAlchemy, and SQLite.

## Features

✨ **Ingredient Extraction**: Parse raw ingredient text and extract structured data
🔄 **Recipe Scaling**: Scale recipes based on serving size changes
🎥 **YouTube Integration**: Extract video metadata and ingredients from transcripts
💾 **Recipe Persistence**: Save, retrieve, update, and delete recipes
📐 **Unit Conversion**: Convert between various cooking units
🚀 **Production Ready**: Async, CORS-enabled, fully documented

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python main.py

# 3. Open browser
# API Docs: http://localhost:8000/api/docs
# Health Check: http://localhost:8000/api/health
```

## API Endpoints

### Ingredients
- `POST /api/ingredients/extract` - Extract from text
- `POST /api/ingredients/normalize` - Normalize units
- `POST /api/ingredients/detect-duplicates` - Find duplicates

### Scaling
- `POST /api/scaling/scale` - Scale by servings
- `POST /api/scaling/convert-unit` - Convert units
- `GET /api/scaling/suggest-unit` - Suggest better unit

### Recipes
- `POST /api/recipes/create` - Create recipe
- `GET /api/recipes` - List recipes
- `GET /api/recipes/{id}` - Get recipe
- `PUT /api/recipes/{id}` - Update recipe
- `DELETE /api/recipes/{id}` - Delete recipe
- `POST /api/recipes/{id}/scale` - Scale recipe

### YouTube
- `POST /api/youtube/extract` - Extract metadata and ingredients
- `GET /api/youtube/metadata` - Get video metadata
- `GET /api/youtube/transcript` - Get video transcript

## Example Usage

### Extract Ingredients
```bash
curl -X POST "http://localhost:8000/api/ingredients/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "2 cups flour, 1/2 cup sugar, 3 eggs",
    "serving_size": 4
  }'
```

### Scale Recipe
```bash
curl -X POST "http://localhost:8000/api/scaling/scale" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [{"name": "flour", "quantity": 2.0, "unit": "cup"}],
    "original_servings": 4,
    "target_servings": 8
  }'
```

## Documentation

- **[Setup Guide](./SETUP_GUIDE.md)** - Installation and deployment
- **[API Documentation](./API_DOCUMENTATION.md)** - Complete API reference
- **[Interactive Docs](http://localhost:8000/api/docs)** - Swagger UI (after starting server)

## Project Structure

```
recipe-scaler-backend/
├── app/
│   ├── models/
│   │   └── schemas.py          # Pydantic validation models
│   ├── database/
│   │   └── db.py               # SQLAlchemy ORM & SQLite setup
│   ├── services/
│   │   ├── ingredient_service.py   # Parsing & extraction
│   │   ├── scaling_service.py      # Scaling logic
│   │   └── youtube_service.py      # YouTube integration
│   └── routes/
│       ├── ingredients.py       # Ingredient endpoints
│       ├── scaling.py           # Scaling endpoints
│       ├── recipes.py           # Recipe management
│       └── youtube.py           # YouTube endpoints
├── main.py                      # FastAPI app entry point
├── requirements.txt             # Python dependencies
├── API_DOCUMENTATION.md         # API reference
└── SETUP_GUIDE.md              # Setup & deployment guide
```

## Technology Stack

- **Framework**: FastAPI (modern, fast, async)
- **Server**: Uvicorn (ASGI)
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic
- **YouTube**: youtube-transcript-api, yt-dlp
- **Deployment**: Docker-ready

## Key Features Deep Dive

### 1. Ingredient Extraction
- Parse multiple formats (comma-separated, newline-separated)
- Normalize units to standard forms
- Extract modifiers (chopped, diced, etc.)
- Detect duplicate ingredients using similarity matching

### 2. Recipe Scaling
- Scale ingredients by serving changes
- Convert between units (volume, weight, count)
- Smart unit suggestions (e.g., 8 tsp → 2 tbsp)
- Precision rounding for realistic measurements

### 3. Recipe Management
- Full CRUD operations
- Track creation and update times
- Store source information
- Link to YouTube videos

### 4. YouTube Integration
- Extract video metadata
- Parse video transcripts
- Extract ingredients from transcripts
- Cache metadata for performance

## Environment Variables

```
HOST=0.0.0.0              # Server host
PORT=8000                 # Server port
DEBUG=false               # Debug mode
RELOAD=true              # Auto-reload (development)
ENVIRONMENT=development   # development or production
FRONTEND_URL=http://localhost:3000  # CORS frontend URL
```

## Deployment

### Docker
```bash
docker build -t recipe-scaler-api .
docker run -p 8000:8000 recipe-scaler-api
```

### Docker Compose
```bash
docker-compose up
```

### Traditional Server
```bash
pip install -r requirements.txt
python main.py
```

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed deployment instructions.

## Testing

### Using Swagger UI
1. Start server: `python main.py`
2. Open: http://localhost:8000/api/docs
3. Test endpoints interactively

### Using curl
```bash
curl -X POST "http://localhost:8000/api/ingredients/extract" \
  -H "Content-Type: application/json" \
  -d '{"text":"2 cups flour","serving_size":4}'
```

### Using Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/ingredients/extract',
    json={'text': '2 cups flour', 'serving_size': 4}
)
print(response.json())
```

## Supported Units

**Volume**: cup, tablespoon, teaspoon, milliliter, liter
**Weight**: gram, kilogram, ounce, pound  
**Count**: whole, pinch, dash

## Database

- **Type**: SQLite
- **Location**: `app/recipe_scaler.db`
- **Auto-created**: On first run
- **Tables**: recipes, ingredients, youtube_cache

## Error Handling

Consistent error responses:
```json
{
  "error": "Error message",
  "details": {},
  "success": false
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Validation error
- `404`: Not found
- `500`: Server error

## Performance

- **Caching**: YouTube metadata cached
- **Indexing**: Database queries optimized
- **Async**: Concurrent request handling
- **Pagination**: List endpoints support skip/limit

## CORS Configuration

Configured for:
- `http://localhost:3000` - Dev frontend
- `http://localhost:5000` - Dev frontend
- `file://` - Electron apps

Customize in `main.py` for production.

## Contributing

When adding features:
1. Add Pydantic models in `models/schemas.py`
2. Add logic in `services/`
3. Add endpoints in `routes/`
4. Update documentation
5. Test with Swagger UI

## Troubleshooting

**Port in use**: `kill -9 $(lsof -t -i:8000)`  
**Module not found**: `pip install --upgrade -r requirements.txt`  
**Database error**: `rm app/recipe_scaler.db` (recreates on startup)  
**CORS error**: Check frontend URL in `main.py`

## License

MIT

## Support

- **Interactive Docs**: http://localhost:8000/api/docs
- **Issues**: Check error messages in API response
- **Logging**: Check console output

---

**Ready to use!** Start the server and visit http://localhost:8000/api/docs
