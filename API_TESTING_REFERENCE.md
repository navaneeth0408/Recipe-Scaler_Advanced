## API Testing Reference

Test these endpoints to verify the migration is working:

### 1. YouTube Extraction

**Request:**
```bash
curl -X POST http://localhost:8000/api/youtube/extract \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=RKt-L8E8Cr4",
    "extract_ingredients": false
  }'
```

**Expected Response:**
```json
{
  "metadata": {
    "video_id": "RKt-L8E8Cr4",
    "title": "Easy Homemade Pasta Carbonara",
    "description": "Ingredients:\n2 cups flour\n...",
    "channel_name": "Cooking with Maria",
    "thumbnail_url": "https://i.ytimg.com/vi/...",
    "duration": "12:30",
    "view_count": 250000
  },
  "success": true
}
```

### 2. Ingredient Parsing

**Request:**
```bash
curl -X POST http://localhost:8000/api/ingredients/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ingredients:\n2 cups all-purpose flour\n1/2 cup granulated sugar\n3 large eggs\n1 tsp vanilla extract\n1/4 tsp salt",
    "serving_size": 12
  }'
```

**Expected Response:**
```json
{
  "ingredients": [
    {
      "name": "all-purpose flour",
      "quantity": 2,
      "unit": "cup"
    },
    {
      "name": "granulated sugar",
      "quantity": 0.5,
      "unit": "cup"
    },
    {
      "name": "large eggs",
      "quantity": 3,
      "unit": "whole"
    },
    {
      "name": "vanilla extract",
      "quantity": 1,
      "unit": "tsp"
    },
    {
      "name": "salt",
      "quantity": 0.25,
      "unit": "tsp"
    }
  ],
  "extracted_count": 5,
  "serving_size": 12,
  "success": true
}
```

### 3. Recipe Scaling

**Request:**
```bash
curl -X POST http://localhost:8000/api/scaling/scale \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"name": "flour", "quantity": 2, "unit": "cup"},
      {"name": "sugar", "quantity": 1, "unit": "cup"},
      {"name": "eggs", "quantity": 3, "unit": "whole"}
    ],
    "original_servings": 12,
    "target_servings": 24
  }'
```

**Expected Response:**
```json
{
  "original_servings": 12,
  "target_servings": 24,
  "scale_factor": 2.0,
  "ingredients": [
    {
      "name": "flour",
      "quantity": 4,
      "unit": "cup"
    },
    {
      "name": "sugar",
      "quantity": 2,
      "unit": "cup"
    },
    {
      "name": "eggs",
      "quantity": 6,
      "unit": "whole"
    }
  ],
  "success": true
}
```

### 4. YouTube Search

**Request:**
```bash
curl -X POST http://localhost:8000/api/youtube/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pasta carbonara",
    "category": "pasta",
    "page_token": "",
    "max_results": 6
  }'
```

**Expected Response:**
```json
{
  "results": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Authentic Carbonara Recipe",
      "channel": "Pasta Masterclass",
      "thumbnail_url": "https://i.ytimg.com/vi/...",
      "views": 500000,
      "duration_seconds": 720,
      "published_date": "2024-01-15",
      "relevance_score": 95.5
    },
    {
      "video_id": "abc123def456",
      "title": "Easy 10 Minute Carbonara",
      "channel": "Quick Recipes",
      "thumbnail_url": "https://i.ytimg.com/vi/...",
      "views": 250000,
      "duration_seconds": 600,
      "published_date": "2024-01-10",
      "relevance_score": 85.2
    }
  ],
  "next_page_token": "CDIQAA...",
  "prev_page_token": null,
  "total_results": 10000,
  "success": true
}
```

### 5. AI - Ingredient Substitution

**Request:**
```bash
curl -X POST http://localhost:8000/api/ai/substitute \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient": "butter",
    "quantity": 1,
    "unit": "cup",
    "dietary_preference": "vegan",
    "available_ingredients": ["olive oil", "coconut oil"]
  }'
```

**Expected Response:**
```json
{
  "ingredient": "butter",
  "substitutions": [
    {
      "name": "coconut oil",
      "quantity": 0.75,
      "unit": "cup",
      "ratio": 0.75,
      "reason": "Vegan alternative with similar fat content",
      "notes": "Use refined for neutral flavor"
    },
    {
      "name": "olive oil",
      "quantity": 0.75,
      "unit": "cup",
      "ratio": 0.75,
      "reason": "Vegan alternative, use extra virgin for flavor",
      "notes": "May slightly alter taste"
    }
  ],
  "success": true
}
```

### 6. AI - Nutrition Analysis

**Request:**
```bash
curl -X POST http://localhost:8000/api/ai/nutrition \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"name": "chicken breast", "quantity": 200, "unit": "g"},
      {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
      {"name": "salt", "quantity": 1, "unit": "tsp"}
    ],
    "servings": 2
  }'
```

**Expected Response:**
```json
{
  "total": {
    "calories": 580,
    "protein_g": 65,
    "carbs_g": 0,
    "fat_g": 34,
    "fiber_g": 0
  },
  "per_serving": {
    "calories": 290,
    "protein_g": 32.5,
    "carbs_g": 0,
    "fat_g": 17,
    "fiber_g": 0
  },
  "ingredients": [
    {
      "name": "chicken breast",
      "calories": 330,
      "protein_g": 65,
      "carbs_g": 0,
      "fat_g": 7
    },
    {
      "name": "olive oil",
      "calories": 240,
      "protein_g": 0,
      "carbs_g": 0,
      "fat_g": 27
    }
  ],
  "servings": 2,
  "success": true
}
```

### 7. Health Check

**Request:**
```bash
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Recipe Scaler API is running"
}
```

---

## JavaScript Testing

### In Browser Console:

```javascript
// Test each API endpoint

// 1. YouTube Extraction
const youtubeData = await apiClient.extractYouTubeMetadata(
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
);
console.log('YouTube data:', youtubeData);

// 2. Ingredient Parsing
const ingredients = await apiClient.parseIngredients(
  "2 cups flour, 1 egg, 1 tsp salt"
);
console.log('Parsed ingredients:', ingredients);

// 3. Recipe Scaling
const scaled = await apiClient.scaleRecipe(
  [{name: "flour", quantity: 2, unit: "cup"}],
  4,
  8
);
console.log('Scaled recipe:', scaled);

// 4. YouTube Search
const searchResults = await apiClient.searchYouTube("pasta carbonara", "pasta");
console.log('Search results:', searchResults);

// 5. Substitution Suggestions
const substitutes = await apiClient.getSubstitutions(
  "butter",
  1,
  "cup",
  "vegan"
);
console.log('Substitutions:', substitutes);

// 6. Nutrition Analysis
const nutrition = await apiClient.analyzeNutrition(
  [{name: "chicken", quantity: 200, unit: "g"}],
  2
);
console.log('Nutrition:', nutrition);

// 7. Health Check
const isHealthy = await apiClient.testConnectivity();
console.log('Backend healthy:', isHealthy ? '✅' : '❌');
```

---

## Error Responses

### Invalid Request
```json
{
  "detail": "Search query cannot be empty",
  "success": false
}
```

### Backend Error
```json
{
  "detail": "Error communicating with YouTube API",
  "success": false
}
```

### Missing API Key
```json
{
  "detail": "YouTube API key not configured. Set YOUTUBE_API_KEY environment variable.",
  "success": false
}
```

---

## Environment Variables Needed

```bash
# Backend configuration
YOUTUBE_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=development

# Frontend configuration (optional, in browser)
# window.API_BASE_URL = 'http://localhost:8000'
```

---

## Performance Benchmarks

| Endpoint | Avg Response Time |
|----------|-------------------|
| `/youtube/extract` | 2-5 seconds |
| `/ingredients/parse` | 100-200 ms |
| `/scaling/scale` | 50-100 ms |
| `/youtube/search` | 3-8 seconds |
| `/ai/substitute` | 500-1000 ms |
| `/ai/nutrition` | 300-600 ms |

Note: Times depend on network and external API availability

---

## Debugging Tips

### Check Backend is Running
```bash
curl http://localhost:8000/api/health
```

### View API Documentation
```
http://localhost:8000/api/docs
```

### Enable Debug Mode
```bash
DEBUG=true python main.py
```

### Check Logs
```bash
# Backend logs show all API calls and errors
# Frontend console shows client-side errors
```

### Test Individual Components
```javascript
// Test API client
console.log(apiClient)

// Test connectivity
apiClient.testConnectivity().then(r => console.log(r))

// Test with specific data
apiClient.parseIngredients("2 cups flour").then(r => console.log(r))
```

