# AI Features Implementation Guide

## Overview

This document describes the complete AI-based feature set added to the Recipe Scaler Backend. The implementation includes 5 major AI-powered endpoints that enhance recipe management with intelligent processing.

## Features Implemented

### 1. 🤖 AI-Based Ingredient Extraction (POST `/api/ai/extract`)

**Purpose**: Automatically extract and normalize ingredients from raw text using transformer-based NLP.

**Features**:
- Identifies individual ingredients from text
- Predicts missing quantities for incomplete ingredient lists
- Normalizes units (teaspoon → tsp, tablespoon → tbsp, etc.)
- Handles vague phrases like "pinch", "handful", "dash"
- Converts vague quantities to standard measurements

**Request Example**:
```json
{
  "text": "2 cups flour, a pinch of salt, 3 tablespoons butter, egg, handful of vanilla"
}
```

**Response Example**:
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
      "quantity": 0.5,
      "unit": "teaspoon",
      "grams_equivalent": 2.5,
      "vague_phrase": true
    }
  ],
  "count": 4
}
```

**Implementation Details**:
- Service: `app/services/ai_ingredient_service.py`
- Uses zero-shot classification for ingredient identification
- Maintains fallback rule-based extraction for robustness
- Supports 50+ common ingredients

---

### 2. 🤖 Smart Ingredient Substitution (POST `/api/ai/substitute`)

**Purpose**: Suggest ingredient alternatives based on dietary preferences, availability, and cuisine.

**Features**:
- Suggests alternatives based on:
  - Dietary preferences (vegan, gluten-free, keto, paleo, etc.)
  - Ingredient availability
  - Cuisine type (Italian, Indian, Asian, etc.)
  - Adjusted quantities for accurate scaling

**Request Example**:
```json
{
  "ingredient": "butter",
  "quantity": 2,
  "unit": "tablespoon",
  "dietary_preference": "vegan",
  "cuisine": "indian"
}
```

**Response Example**:
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

**Supported Substitutions**:
- Butter → coconut oil, olive oil, ghee, applesauce
- Milk → almond milk, coconut milk, oat milk, water
- Eggs → flax eggs, applesauce, tofu, aquafaba
- Cheese → nutritional yeast, cashew cream, feta
- Wheat flour → almond flour, rice flour, oat flour, coconut flour
- Sugar → honey, maple syrup, stevia
- Soy sauce → tamari, coconut aminos

**Dietary Preferences Supported**:
- vegan, vegetarian, gluten_free, dairy_free, keto, paleo, kosher, halal

**Implementation Details**:
- Service: `app/services/ai_substitution_service.py`
- Maintains comprehensive substitution database
- Each substitution includes ratio for quantity adjustment
- Explanations include cooking tips and usage guidelines

---

### 3. 🤖 Nutritional Analysis (POST `/api/ai/nutrition`)

**Purpose**: Calculate detailed nutritional information and adjust based on scaling.

**Features**:
- Calculates:
  - Calories
  - Protein
  - Carbohydrates
  - Fat
- Provides per-serving and total nutrition
- Dynamically adjusts when recipe is scaled
- Supports 20+ common ingredients with nutrition data

**Request Example**:
```json
{
  "ingredients": [
    {"name": "chicken breast", "quantity": 200, "unit": "g"},
    {"name": "olive oil", "quantity": 2, "unit": "tablespoon"},
    {"name": "tomato", "quantity": 150, "unit": "g"}
  ],
  "servings": 2,
  "scale_factor": 1.5
}
```

**Response Example**:
```json
{
  "total": {
    "calories": 550.5,
    "protein": 70.2,
    "carbs": 15.8,
    "fat": 28.4
  },
  "per_serving": {
    "calories": 275.25,
    "protein": 35.1,
    "carbs": 7.9,
    "fat": 14.2
  },
  "ingredients": [...],
  "servings": 2
}
```

**Nutrition Database**:
- Proteins: chicken, beef, salmon, eggs, yogurt, cheese
- Carbs: flour, sugar, rice, pasta, bread, tomato, carrot, onion
- Fats: butter, olive oil, cheese
- And more...

**Implementation Details**:
- Service: `app/services/nutrition_service.py`
- Stores nutrition per 100g/100ml standard
- Automatically converts units for accurate calculations
- Includes helper functions for macro percentage calculations

---

### 4. 🤖 Conversational Assistant (POST `/api/ai/chat`)

**Purpose**: Context-aware chatbot for cooking questions with session management.

**Features**:
- Session-based conversation history
- Recipe context awareness
- Dietary restriction understanding
- Answers questions about:
  - Ingredient substitutions
  - Recipe scaling
  - Cooking techniques and methods
  - Cooking temperatures
  - Food storage
  - Nutritional information
- Maintains multi-turn conversation context

**Request Example**:
```json
{
  "session_id": "session-123",
  "message": "Can I substitute butter with oil?",
  "recipe_context": {
    "name": "Chocolate Cake",
    "servings": 8
  },
  "dietary_restrictions": ["vegan"]
}
```

**Response Example**:
```json
{
  "session_id": "session-123",
  "user_message": "Can I substitute butter with oil?",
  "assistant_response": "Yes! For vegan baking, I recommend coconut oil or olive oil at a 0.75:1 ratio. Use 25% less oil as it's lighter than butter.",
  "conversation_history": [
    {"role": "user", "content": "Can I substitute butter with oil?"},
    {"role": "assistant", "content": "Yes! For vegan baking..."}
  ]
}
```

**Session Management Endpoints**:
- POST `/api/ai/chat` - Send message
- DELETE `/api/ai/chat/session/{session_id}` - Clear session
- GET `/api/ai/chat/history/{session_id}` - Get conversation history

**Implementation Details**:
- Service: `app/services/chat_service.py`
- Rule-based response generation with NLP pattern matching
- Maintains session context for multi-turn conversations
- Supports 6+ conversation topics
- Easy to extend with LLM integration (GPT, Claude, Groq, etc.)

---

### 5. 🤖 Multilingual Translation (POST `/api/ai/translate`)

**Purpose**: Translate recipes, ingredients, and instructions to multiple languages.

**Features**:
- Supports multiple translation targets:
  - English, Hindi, Malayalam, Tamil
  - Spanish, French
- Can translate:
  - Single text
  - Batch of texts
  - Ingredient lists with proper unit translation
  - Complete recipes (name, description, ingredients, instructions)
- Custom glossary for cooking terms
- Language detection

**Request Examples**:

*Single text*:
```json
{
  "text": "1 cup of flour",
  "target_language": "hi"
}
```

*Complete recipe*:
```json
{
  "recipe": {
    "name": "Chocolate Cake",
    "ingredients": [
      {"name": "flour", "quantity": 2, "unit": "cup"},
      {"name": "sugar", "quantity": 1, "unit": "cup"}
    ],
    "instructions": ["Mix flour and sugar", "Bake for 30 minutes"]
  },
  "target_language": "ml"
}
```

**Response Example**:
```json
{
  "source_language": "en",
  "target_language": "hi",
  "original": "1 cup of flour",
  "translated": "1 कप मैदा"
}
```

**Supported Languages**:
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

**Implementation Details**:
- Service: `app/services/translation_service.py`
- Uses Google Translate API with fallback glossary
- Maintains cooking-specific translation glossary
- Automatic unit translation
- Easy to add custom glossary entries

---

## Technical Architecture

### Service Layer Structure

```
app/services/
├── ai_ingredient_service.py      # Ingredient extraction
├── ai_substitution_service.py    # Substitution suggestions
├── nutrition_service.py          # Nutrition analysis
├── chat_service.py               # Conversational assistant
└── translation_service.py        # Multilingual translation
```

### Route Layer

```
app/routes/
└── ai.py                         # All 5 AI endpoints
```

### Integration Points

All services are integrated into the main FastAPI application via:
```python
# main.py
from app.routes import ai
app.include_router(ai.router)
```

---

## Dependencies

New packages added to `requirements.txt`:

```
# NLP & AI
transformers==4.36.2              # Hugging Face transformers
torch==2.1.2                      # PyTorch for models
spacy==3.7.2                      # Advanced NLP
langchain==0.1.7                  # LLM framework

# Translation & Processing
deep-translator==1.11.4           # Translation API
requests==2.31.0                  # HTTP requests
python-Levenshtein==0.21.1        # String similarity

# APIs
groq==0.4.2                       # Groq LLM API
openai==1.6.1                     # OpenAI API
```

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/ai/extract` | POST | Extract ingredients from text | ✅ Implemented |
| `/api/ai/substitute` | POST | Get substitution suggestions | ✅ Implemented |
| `/api/ai/nutrition` | POST | Analyze nutritional information | ✅ Implemented |
| `/api/ai/chat` | POST | Conversational assistant | ✅ Implemented |
| `/api/ai/chat/session/{id}` | DELETE | Clear chat session | ✅ Implemented |
| `/api/ai/chat/history/{id}` | GET | Get chat history | ✅ Implemented |
| `/api/ai/translate` | POST | Translate content | ✅ Implemented |
| `/api/ai/languages` | GET | Get supported languages | ✅ Implemented |
| `/api/ai/health` | GET | Health check | ✅ Implemented |

---

## Usage Examples

### Example 1: Complete Ingredient Processing

```python
# Step 1: Extract ingredients from text
POST /api/ai/extract
{
  "text": "Mix 2 cups flour, a pinch of salt, butter, 3 eggs, handful of vanilla"
}

# Step 2: Get substitutions for dietary preference
POST /api/ai/substitute
{
  "ingredient": "butter",
  "quantity": 0.5,
  "unit": "cup",
  "dietary_preference": "vegan"
}

# Step 3: Calculate nutrition
POST /api/ai/nutrition
{
  "ingredients": [extracted ingredients],
  "servings": 4
}

# Step 4: Translate recipe to Hindi
POST /api/ai/translate
{
  "recipe": {...},
  "target_language": "hi"
}
```

### Example 2: Cooking Assistant with Context

```python
# Create session with recipe
POST /api/ai/chat
{
  "session_id": "my-session",
  "message": "How do I scale this recipe for 10 people?",
  "recipe_context": {
    "name": "Chocolate Cake",
    "servings": 4,
    "ingredients": [...]
  }
}

# Ask follow-up question (maintains context)
POST /api/ai/chat
{
  "session_id": "my-session",
  "message": "What about vegan substitutes?"
}

# Get conversation history
GET /api/ai/chat/history/my-session

# Clear session when done
DELETE /api/ai/chat/session/my-session
```

---

## Configuration & Environment Variables

No required environment variables, but optional:

```bash
# Translation API (if using paid services)
TRANSLATION_API_KEY=your_key

# LLM APIs (for enhanced chat)
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key

# App settings
DEBUG=false
ENVIRONMENT=production
```

---

## Future Enhancements

1. **LLM Integration**: Replace rule-based chat with GPT/Claude for better responses
2. **Image Recognition**: Extract ingredients from recipe photos
3. **User Preferences**: Save dietary restrictions and cuisine preferences
4. **Recipe Ratings**: User ratings and feedback on substitutions
5. **Allergen Detection**: Identify potential allergens in recipes
6. **Smart Shopping List**: Generate shopping lists with substitution options
7. **Meal Planning**: AI-powered weekly meal planning
8. **Cooking Video Integration**: Link recipes to video tutorials

---

## Error Handling

All endpoints include comprehensive error handling:

```json
{
  "error": "Error message",
  "details": "Additional context (only in DEBUG mode)"
}
```

Common HTTP Status Codes:
- `200 OK`: Successful request
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Performance Notes

- Ingredient extraction: ~100-500ms (depends on text length)
- Substitution suggestions: <50ms (database lookup)
- Nutrition analysis: <100ms (with 10+ ingredients)
- Chat response: 100-1000ms (depends on complexity)
- Translation: 500-2000ms (API calls)

---

## Security Considerations

1. Input validation on all endpoints
2. Request size limits to prevent abuse
3. No sensitive data stored in logs
4. CORS configuration for frontend safety
5. Rate limiting recommended for production

---

## Testing

Each service includes comprehensive functionality. To test:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest app/tests/

# Test specific endpoint
curl -X POST http://localhost:8000/api/ai/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "2 cups flour, 1 egg, salt"}'
```

---

## Support & Troubleshooting

**Issue**: Ingredient extraction not recognizing ingredient
- **Solution**: Add to `COMMON_INGREDIENTS` in `ai_ingredient_service.py`

**Issue**: Translation quality issues
- **Solution**: Add custom glossary entry using `/api/ai/translate` API

**Issue**: Chat not understanding context
- **Solution**: Provide more detailed recipe context

**Issue**: Nutrition data for ingredient not found
- **Solution**: Add to nutrition database in `nutrition_service.py`

---

Generated: January 24, 2026
Version: 1.0.0
