# AI Features Quick Start Guide

## Installation

### 1. Install Dependencies

```bash
# From your project root
pip install -r requirements.txt

# If you need to download spacy model for NLP
python -m spacy download en_core_web_sm
```

### 2. Start the Server

```bash
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
API documentation at: `http://localhost:8000/api/docs`

---

## Quick API Tests

### 1. Test Ingredient Extraction

```bash
curl -X POST http://localhost:8000/api/ai/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "2 cups flour, a pinch of salt, 3 tablespoons butter, 2 eggs, vanilla extract"
  }'
```

**Expected Response:**
```json
{
  "ingredients": [
    {
      "name": "flour",
      "quantity": 2,
      "unit": "cup",
      "grams_equivalent": 240,
      "vague_phrase": false
    },
    {
      "name": "salt",
      "quantity": 0.125,
      "unit": "teaspoon",
      "grams_equivalent": 0.625,
      "vague_phrase": true
    }
  ],
  "count": 5
}
```

---

### 2. Test Ingredient Substitution

```bash
curl -X POST http://localhost:8000/api/ai/substitute \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient": "butter",
    "quantity": 2,
    "unit": "tablespoon",
    "dietary_preference": "vegan",
    "cuisine": "asian"
  }'
```

**Expected Response:**
```json
{
  "ingredient": "butter",
  "substitutions": [
    {
      "ingredient": "coconut oil",
      "original_quantity": 2,
      "adjusted_quantity": 2,
      "unit": "tablespoon",
      "ratio": 1.0,
      "explanation": "Coconut oil has similar fat content and works well in baking",
      "dietary_tags": ["vegan", "dairy_free"],
      "best_cuisines": ["asian", "mediterranean"]
    }
  ]
}
```

---

### 3. Test Nutrition Analysis

```bash
curl -X POST http://localhost:8000/api/ai/nutrition \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"name": "chicken breast", "quantity": 200, "unit": "g"},
      {"name": "olive oil", "quantity": 2, "unit": "tablespoon"},
      {"name": "tomato", "quantity": 150, "unit": "g"}
    ],
    "servings": 2
  }'
```

**Expected Response:**
```json
{
  "total": {
    "calories": 470.5,
    "protein": 62,
    "carbs": 5.85,
    "fat": 24.9
  },
  "per_serving": {
    "calories": 235.25,
    "protein": 31,
    "carbs": 2.925,
    "fat": 12.45
  },
  "ingredients": [...],
  "servings": 2
}
```

---

### 4. Test Conversational Assistant

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "message": "Can I substitute butter with oil in my cake recipe?",
    "recipe_context": {
      "name": "Chocolate Cake",
      "servings": 8
    },
    "dietary_restrictions": ["vegan"]
  }'
```

**Expected Response:**
```json
{
  "session_id": "test-session",
  "user_message": "Can I substitute butter with oil in my cake recipe?",
  "assistant_response": "I can help with butter substitutions! Based on your vegan diet, I recommend coconut oil or olive oil...",
  "conversation_history": [
    {
      "role": "user",
      "content": "Can I substitute butter with oil in my cake recipe?"
    },
    {
      "role": "assistant",
      "content": "I can help with butter substitutions!..."
    }
  ]
}
```

---

### 5. Test Translation

```bash
curl -X POST http://localhost:8000/api/ai/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mix flour, sugar, and butter together",
    "target_language": "hi"
  }'
```

**Expected Response:**
```json
{
  "source_language": "en",
  "target_language": "hi",
  "original": "Mix flour, sugar, and butter together",
  "translated": "मैदा, चीनी और मक्खन को एक साथ मिलाएं"
}
```

---

### 6. Check Supported Languages

```bash
curl http://localhost:8000/api/ai/languages
```

**Response:**
```json
{
  "supported_languages": [
    {"code": "en", "name": "English"},
    {"code": "hi", "name": "Hindi"},
    {"code": "ml", "name": "Malayalam"},
    {"code": "ta", "name": "Tamil"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"}
  ]
}
```

---

### 7. Test Chat History

```bash
# Get conversation history
curl http://localhost:8000/api/chat/history/test-session

# Clear session
curl -X DELETE http://localhost:8000/api/ai/chat/session/test-session
```

---

### 8. Health Check

```bash
curl http://localhost:8000/api/ai/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "ingredient_extraction": "available",
    "substitution": "available",
    "nutrition": "available",
    "chat": "available",
    "translation": "available"
  }
}
```

---

## Python Usage Examples

### Using with Requests Library

```python
import requests

BASE_URL = "http://localhost:8000/api/ai"

# Example 1: Extract ingredients
response = requests.post(
    f"{BASE_URL}/extract",
    json={"text": "2 cups flour, 1 egg, salt to taste"}
)
print(response.json())

# Example 2: Get substitutions
response = requests.post(
    f"{BASE_URL}/substitute",
    json={
        "ingredient": "milk",
        "quantity": 1,
        "unit": "cup",
        "dietary_preference": "vegan"
    }
)
print(response.json())

# Example 3: Get nutrition
response = requests.post(
    f"{BASE_URL}/nutrition",
    json={
        "ingredients": [
            {"name": "egg", "quantity": 2, "unit": "piece"},
            {"name": "milk", "quantity": 1, "unit": "cup"}
        ],
        "servings": 1
    }
)
print(response.json())

# Example 4: Chat
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "session_id": "my-session",
        "message": "How do I make this recipe vegan?",
        "dietary_restrictions": ["vegan"]
    }
)
print(response.json())

# Example 5: Translate
response = requests.post(
    f"{BASE_URL}/translate",
    json={
        "text": "1 cup flour",
        "target_language": "hi"
    }
)
print(response.json())
```

---

## Integration with Frontend

### React Example

```javascript
// API utility
const API_BASE = 'http://localhost:8000/api/ai';

// Extract ingredients
async function extractIngredients(text) {
  const response = await fetch(`${API_BASE}/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  return response.json();
}

// Get substitutions
async function getSubstitutions(ingredient, quantity, unit, dietary) {
  const response = await fetch(`${API_BASE}/substitute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ingredient,
      quantity,
      unit,
      dietary_preference: dietary
    })
  });
  return response.json();
}

// Analyze nutrition
async function analyzeNutrition(ingredients, servings) {
  const response = await fetch(`${API_BASE}/nutrition`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ingredients, servings })
  });
  return response.json();
}

// Chat
async function chat(message, sessionId, dietary) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId || undefined,
      message,
      dietary_restrictions: dietary
    })
  });
  return response.json();
}

// Translate
async function translateText(text, targetLanguage) {
  const response = await fetch(`${API_BASE}/translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text,
      target_language: targetLanguage
    })
  });
  return response.json();
}

// Usage in component
function RecipeForm() {
  const handleExtract = async (recipeText) => {
    const data = await extractIngredients(recipeText);
    console.log('Extracted:', data.ingredients);
  };
  
  // ... component code
}
```

---

## Common Issues & Solutions

### Issue: "Module not found" error for transformers

**Solution:**
```bash
pip install --upgrade transformers torch
```

### Issue: spaCy model not found

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: Translation returning empty

**Solution:**
Make sure you have internet connection for Google Translate API. Or add custom glossary entry:
```python
from app.services.translation_service import translation_service
translation_service.add_glossary_entry("en", "hi", "flour", "मैदा")
```

### Issue: Chat not recognizing context

**Solution:**
Make sure to include recipe_context in the request with at least a name:
```json
{
  "recipe_context": {
    "name": "Chocolate Cake"
  }
}
```

---

## Performance Tips

1. **Cache translations** - Don't translate the same text multiple times
2. **Batch requests** - Use `/api/ai/translate` with `texts` array for multiple items
3. **Session reuse** - Keep chat session IDs to maintain context
4. **Lazy loading** - spaCy models load on first use; initial request may be slower

---

## Next Steps

1. Review [AI_FEATURES_DOCUMENTATION.md](AI_FEATURES_DOCUMENTATION.md) for complete API reference
2. Integrate with your frontend application
3. Customize substitutions and nutrition data as needed
4. Consider adding LLM integration for enhanced chat (GPT, Claude, etc.)

---

## Support

For issues or questions:
1. Check the full documentation: `AI_FEATURES_DOCUMENTATION.md`
2. Review service code in `app/services/`
3. Check route implementation in `app/routes/ai.py`
4. Test endpoints using Swagger UI at `/api/docs`

---

Created: January 24, 2026
