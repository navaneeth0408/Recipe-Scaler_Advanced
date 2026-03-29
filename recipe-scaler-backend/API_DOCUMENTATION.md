# Recipe Scaler Backend - API Documentation

## Overview
Complete REST API backend for the Recipe Scaler application. Handles recipe management, ingredient extraction, scaling calculations, and YouTube metadata integration.

## Features

### 1. **Ingredient Extraction** (`/api/ingredients`)
- Extract structured ingredients from raw text
- Support for multiple formats (comma-separated, newline-separated)
- Automatic unit normalization
- Duplicate detection
- Modifier extraction (chopped, diced, etc.)

### 2. **Recipe Scaling** (`/api/scaling`)
- Scale recipes based on serving size changes
- Unit conversion (cups, tbsp, grams, oz, etc.)
- Smart unit suggestions
- Precision rounding for cooking measurements

### 3. **Recipe Persistence** (`/api/recipes`)
- Create, read, update, delete recipes
- SQLite database storage
- Metadata tracking (created_at, updated_at)
- Source tracking (manual or YouTube)
- Recipe scaling without modifying stored recipe

### 4. **YouTube Integration** (`/api/youtube`)
- Extract video metadata (title, channel, thumbnail, etc.)
- Fetch video transcripts
- Extract ingredients from transcripts
- Metadata caching for performance

## API Endpoints

### Ingredients Extraction
```
POST /api/ingredients/extract
  - Extract ingredients from text
  - Body: { text: string, serving_size: int }

POST /api/ingredients/normalize
  - Normalize unit variations
  - Body: [Ingredient]

POST /api/ingredients/detect-duplicates
  - Find duplicate ingredients
  - Body: [Ingredient]
```

### Scaling
```
POST /api/scaling/scale
  - Scale ingredients by servings
  - Body: { ingredients, original_servings, target_servings }

POST /api/scaling/convert-unit
  - Convert between units
  - Params: quantity, from_unit, to_unit

GET /api/scaling/suggest-unit
  - Suggest better unit for quantity
  - Params: quantity, current_unit
```

### Recipes
```
POST /api/recipes/create
  - Create new recipe
  - Body: RecipeCreate

GET /api/recipes
  - List all recipes
  - Params: skip, limit

GET /api/recipes/{recipe_id}
  - Get recipe details
  
PUT /api/recipes/{recipe_id}
  - Update recipe

DELETE /api/recipes/{recipe_id}
  - Delete recipe

POST /api/recipes/{recipe_id}/scale
  - Scale recipe by servings
  - Params: target_servings
```

### YouTube
```
POST /api/youtube/extract
  - Extract metadata and optionally ingredients
  - Body: { url, extract_ingredients }

GET /api/youtube/metadata
  - Get video metadata only
  - Params: url

GET /api/youtube/transcript
  - Get video transcript
  - Params: url
```

### Health
```
GET /
  - API info

GET /api/health
  - Health check

GET /api/docs
  - Interactive API documentation (Swagger UI)
```

## Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
echo "HOST=0.0.0.0" > .env
echo "PORT=8000" >> .env
echo "DEBUG=false" >> .env

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

### Example Usage

#### 1. Extract Ingredients
```bash
curl -X POST "http://localhost:8000/api/ingredients/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "2 cups flour, 1/2 cup sugar, 3 eggs, 1 tsp vanilla extract",
    "serving_size": 4
  }'
```

Response:
```json
{
  "ingredients": [
    {
      "name": "flour",
      "quantity": 2.0,
      "unit": "cup"
    },
    {
      "name": "sugar",
      "quantity": 0.5,
      "unit": "cup"
    },
    {
      "name": "eggs",
      "quantity": 3.0,
      "unit": "whole"
    },
    {
      "name": "vanilla extract",
      "quantity": 1.0,
      "unit": "teaspoon"
    }
  ],
  "serving_size": 4,
  "extracted_count": 4,
  "success": true
}
```

#### 2. Scale Recipe
```bash
curl -X POST "http://localhost:8000/api/scaling/scale" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"name": "flour", "quantity": 2.0, "unit": "cup"}
    ],
    "original_servings": 4,
    "target_servings": 8
  }'
```

Response:
```json
{
  "original_servings": 4,
  "target_servings": 8,
  "scale_factor": 2.0,
  "ingredients": [
    {
      "name": "flour",
      "quantity": 4.0,
      "unit": "cup"
    }
  ],
  "success": true
}
```

#### 3. Create Recipe
```bash
curl -X POST "http://localhost:8000/api/recipes/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chocolate Chip Cookies",
    "ingredients": [
      {
        "name": "flour",
        "quantity": 2.0,
        "unit": "cup"
      },
      {
        "name": "sugar",
        "quantity": 1.0,
        "unit": "cup"
      }
    ],
    "servings": 24,
    "source": "manual",
    "notes": "My favorite recipe"
  }'
```

#### 4. Extract YouTube Data
```bash
curl -X POST "http://localhost:8000/api/youtube/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "extract_ingredients": true
  }'
```

## Data Models

### Ingredient
```json
{
  "name": "flour",
  "quantity": 2.0,
  "unit": "cup",
  "original_quantity": null,
  "original_unit": null,
  "notes": "all-purpose"
}
```

### Recipe
```json
{
  "id": "recipe_uuid",
  "name": "Recipe Name",
  "ingredients": [Ingredient],
  "servings": 4,
  "source": "manual|youtube",
  "source_url": "https://...",
  "notes": "Optional notes",
  "instructions": ["Step 1", "Step 2"],
  "created_at": "2024-01-23T10:30:00",
  "updated_at": "2024-01-23T10:30:00"
}
```

### YouTubeMetadata
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "description": "Video description",
  "channel_name": "Channel Name",
  "thumbnail_url": "https://...",
  "duration": "10:30",
  "view_count": 1000000,
  "upload_date": "2024-01-15"
}
```

## Supported Units

### Volume
- cup, tablespoon, teaspoon, milliliter, liter

### Weight
- gram, kilogram, ounce, pound

### Count
- whole, pinch, dash

## Environment Variables

```
HOST=0.0.0.0              # Server host
PORT=8000                 # Server port
DEBUG=false               # Debug mode
RELOAD=true              # Auto-reload on file changes
ENVIRONMENT=development   # development or production
FRONTEND_URL=http://localhost:3000  # CORS frontend URL
```

## Database

SQLite database is automatically created at:
```
app/recipe_scaler.db
```

### Tables
- **recipes**: Recipe data
- **ingredients**: Ingredient data (linked to recipes)
- **youtube_cache**: YouTube metadata cache

## Error Handling

All endpoints return consistent error responses:
```json
{
  "error": "Error message",
  "details": { "field": "additional info" },
  "success": false
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Validation error
- `404`: Not found
- `500`: Server error

## Testing the API

### Using Swagger UI
1. Start the server
2. Open: http://localhost:8000/api/docs
3. Test endpoints interactively

### Using curl
See examples above

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/ingredients/extract",
    json={
        "text": "2 cups flour, 1 cup sugar",
        "serving_size": 4
    }
)

print(response.json())
```

### Using JavaScript (from frontend)
```javascript
const response = await fetch('http://localhost:8000/api/ingredients/extract', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: '2 cups flour, 1 cup sugar',
    serving_size: 4
  })
});

const data = await response.json();
console.log(data);
```

## Performance Considerations

1. **YouTube Caching**: Video metadata is cached to reduce API calls
2. **Database Indexing**: Common queries are indexed for performance
3. **Pagination**: List endpoints support skip/limit for large datasets
4. **Async Operations**: FastAPI handles concurrent requests efficiently

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=false
```

### Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Configure proper CORS origins
- [ ] Use HTTPS in production
- [ ] Set up logging and monitoring
- [ ] Configure database backups
- [ ] Rate limiting (optional)
- [ ] Authentication/Authorization (if needed)

## Architecture

```
recipe-scaler-backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic validation models
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py               # SQLAlchemy ORM models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingredient_service.py   # Ingredient parsing logic
│   │   ├── scaling_service.py      # Recipe scaling logic
│   │   └── youtube_service.py      # YouTube integration
│   └── routes/
│       ├── __init__.py
│       ├── ingredients.py      # Ingredient endpoints
│       ├── scaling.py          # Scaling endpoints
│       ├── recipes.py          # Recipe management endpoints
│       └── youtube.py          # YouTube endpoints
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
└── recipe_scaler.db           # SQLite database (auto-created)
```

## Contributing

When adding new features:
1. Add Pydantic models in `models/schemas.py`
2. Add business logic in `services/`
3. Add API endpoints in `routes/`
4. Update documentation
5. Test with Swagger UI

## Support

For issues or questions:
1. Check the Swagger documentation: `/api/docs`
2. Review error messages in the response
3. Check server logs for detailed errors
4. Enable DEBUG mode for more information

