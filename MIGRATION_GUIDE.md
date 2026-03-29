# Recipe Scaler Frontend-to-Backend Migration Guide

## Overview
This document outlines the systematic refactoring of the Recipe Scaler project to move business logic from frontend JavaScript to FastAPI backend while preserving all UI behavior and user interactions.

---

## Architecture Evolution

### Current State (Frontend-Heavy)
```
User Input → Browser JavaScript Logic → DOM Manipulation → User Output
```

### Target State (Backend-Focused)
```
User Input → Browser (API call) → Backend Logic → JSON Response → Browser (Display)
```

---

## Feature Migration Plan

### 1. YouTube Video Data Extraction
**Current Frontend Location:** `script.js` - `fetchIngredients()`, `displayThumbnail()`

**Business Logic:**
- Extract video ID from URL
- Call YouTube API
- Parse metadata (title, description, thumbnail)
- Display results to user

**Migration Strategy:**
- **KEEP:** `fetchIngredients()` function (UI trigger remains unchanged)
- **KEEP:** `displayThumbnail()` function (DOM manipulation)
- **MOVE:** YouTube API calls and metadata extraction to backend
- **REPLACE:** Direct API call with `fetch()` call to backend endpoint

**New Backend Endpoint:**
```
POST /api/youtube/extract
Request: { "url": "https://youtube.com/..." }
Response: { "title": "...", "description": "...", "thumbnail_url": "...", "video_id": "..." }
```

**Frontend Change (Minimal):**
```javascript
// Before: Direct YouTube API call in fetchIngredients()
// After: Call backend endpoint
function fetchIngredients() {
  const youtubeLink = document.getElementById("youtubeLink").value;
  
  fetch('/api/youtube/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: youtubeLink })
  })
  .then(response => response.json())
  .then(data => {
    displayThumbnail(data.thumbnail_url, data.title);
    parseIngredients(data.description);
  })
  .catch(error => {
    hideLoading();
    alert('Error: ' + error.message);
  });
}
```

---

### 2. Ingredient Extraction from Text
**Current Frontend Location:** `script.js` - `parseIngredients()`

**Business Logic:**
- Parse ingredient text using regex and unit matching
- Filter unnecessary keywords and instruction indicators
- Extract quantity, unit, and ingredient name
- Normalize ingredient data

**Migration Strategy:**
- **KEEP:** UI function name `parseIngredients()` (but change implementation)
- **KEEP:** DOM manipulation code (displaying ingredients)
- **MOVE:** Text parsing logic and regex operations to backend
- **REPLACE:** Local parsing with backend API call

**New Backend Endpoint:**
```
POST /api/ingredients/parse
Request: { "text": "2 cups flour, 1 egg, ..." }
Response: {
  "ingredients": [
    { "name": "flour", "quantity": 2, "unit": "cup" },
    { "name": "egg", "quantity": 1, "unit": "whole" }
  ]
}
```

**Frontend Change (Minimal):**
```javascript
// Keep the function name, change the implementation
function parseIngredients(description) {
  showLoading();
  
  fetch('/api/ingredients/parse', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: description })
  })
  .then(response => response.json())
  .then(data => {
    displayIngredientsList(data.ingredients);
    hideLoading();
  })
  .catch(error => {
    hideLoading();
    console.error('Error parsing ingredients:', error);
  });
}

// Extracted display logic (stays on frontend)
function displayIngredientsList(ingredients) {
  const ingredientsList = document.getElementById("ingredientsList");
  ingredientsList.innerHTML = "";
  ingredients.forEach(ingredient => {
    const div = document.createElement("div");
    div.className = "ingredient-entry";
    const text = `${ingredient.quantity} ${ingredient.unit} ${ingredient.name}`;
    div.innerHTML = `<input type="text" value="${text}" readonly class="ingredient-name">`;
    ingredientsList.appendChild(div);
  });
}
```

---

### 3. Recipe Scaling
**Current Frontend Location:** `script.js` - `scaleFetchedIngredients()`, `scaleRecipe()`

**Business Logic:**
- Parse ingredient quantities (handles fractions, mixed numbers, ranges)
- Calculate scale factor based on servings or custom ratio
- Scale all ingredients proportionally
- Format output quantities

**Migration Strategy:**
- **KEEP:** UI function names and triggers
- **KEEP:** DOM manipulation and sessionStorage operations
- **MOVE:** Quantity parsing and mathematical calculations to backend
- **REPLACE:** JavaScript calculation with API call

**New Backend Endpoint:**
```
POST /api/scaling/scale
Request: {
  "ingredients": [
    { "name": "flour", "quantity": 2, "unit": "cup" }
  ],
  "original_servings": 4,
  "target_servings": 8
}
Response: {
  "scale_factor": 2,
  "ingredients": [
    { "name": "flour", "quantity": 4, "unit": "cup" }
  ]
}
```

**Frontend Change (Minimal):**
```javascript
function scaleFetchedIngredients() {
  const scalingValue = parseFloat(document.getElementById("scalingValue").value);
  
  const ingredients = Array.from(document.querySelectorAll("#ingredientsList .ingredient-entry"))
    .map(ing => {
      // Frontend: just extracts raw values, backend does the parsing
      return {
        name: ing.querySelector(".ingredient-name").value,
        quantity: 1,  // Will be extracted by backend
        unit: ""      // Will be extracted by backend
      };
    });
  
  // Call backend to scale
  fetch('/api/scaling/scale', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ingredients: ingredients,
      original_servings: 1,
      target_servings: scalingValue
    })
  })
  .then(response => response.json())
  .then(data => {
    // Frontend: display scaled results
    const scaledIngredients = data.ingredients.map(ing =>
      `${ing.quantity} ${ing.unit} ${ing.name}`
    );
    
    sessionStorage.setItem('scaledIngredients', scaledIngredients.join("<br>"));
    window.location.href = "scaled.html";
  })
  .catch(error => alert('Error: ' + error.message));
}
```

---

### 4. YouTube Search
**Current Frontend Location:** `script.js` - `searchYouTube()`, `filterSearchResults()`

**Business Logic:**
- Build search query with filters
- Call YouTube API
- Score and rank videos by quality
- Filter out YouTube Shorts
- Parse ISO 8601 durations

**Migration Strategy:**
- **KEEP:** UI function and search trigger
- **KEEP:** Result display and pagination UI
- **MOVE:** API calls, scoring algorithm, and filtering logic to backend
- **REPLACE:** YouTube API calls with backend endpoint

**New Backend Endpoint:**
```
POST /api/youtube/search
Request: {
  "query": "pasta",
  "category": "pasta",
  "page_token": ""
}
Response: {
  "results": [
    {
      "video_id": "...",
      "title": "...",
      "thumbnail_url": "...",
      "channel": "...",
      "views": 100000,
      "duration_seconds": 600
    }
  ],
  "next_page_token": "...",
  "prev_page_token": "..."
}
```

**Frontend Change (Minimal):**
```javascript
function searchYouTube(pageToken = '') {
  showLoading();
  
  const query = document.getElementById('searchQuery').value;
  const category = document.getElementById('recipeCategory').value;
  
  fetch('/api/youtube/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      category: category,
      page_token: pageToken
    })
  })
  .then(response => response.json())
  .then(data => {
    displaySearchResults(data.results);
    createPagination(data.next_page_token, data.prev_page_token);
    hideLoading();
  })
  .catch(error => {
    hideLoading();
    alert('Error searching YouTube: ' + error.message);
  });
}
```

---

### 5. AI-Based Features (Future Enhancement)
**Current State:** Mostly implemented on backend, some JavaScript enhancements possible

**Planned Backend Endpoints:**
```
POST /api/ai/extract-ingredients          # NLP-based ingredient extraction
POST /api/ai/suggest-substitutions       # Smart substitution with dietary info
POST /api/ai/nutrition                   # Nutrition analysis
POST /api/ai/chat                        # Cooking assistant
POST /api/ai/translate                   # Recipe translation
```

**Frontend Integration:** Minimal changes - just add fetch calls when features are enabled

---

## Implementation Phases

### Phase 1: YouTube Extraction (HIGHEST PRIORITY)
1. ✅ Analysis complete
2. Backend: Add `/api/youtube/extract` endpoint
3. Frontend: Replace `fetchIngredients()` to use backend
4. Testing: Verify thumbnail and ingredient display work

### Phase 2: Ingredient Parsing
1. Backend: Add `/api/ingredients/parse` endpoint
2. Frontend: Replace `parseIngredients()` to use backend
3. Fallback: Keep original parsing as fallback if backend fails

### Phase 3: Recipe Scaling
1. Backend: Enhance `/api/scaling/scale` endpoint
2. Frontend: Replace `scaleFetchedIngredients()` to use backend
3. Testing: Verify all scaling modes work

### Phase 4: YouTube Search
1. Backend: Add `/api/youtube/search` endpoint
2. Frontend: Replace `searchYouTube()` to use backend
3. Testing: Pagination and result filtering

### Phase 5: AI Features Integration
1. Backend: Ensure all AI routes are optimized
2. Frontend: Add UI toggles for AI features
3. Testing: All AI features accessible through API

---

## Key Principles Maintained

✅ **UI Consistency**
- All function names remain the same where possible
- Button clicks trigger same functions
- DOM elements and IDs unchanged

✅ **User Experience**
- Loading spinners work for backend calls
- Error messages displayed to users
- Fallback to frontend logic if backend unavailable

✅ **Data Integrity**
- SessionStorage and LocalStorage usage unchanged
- All recipe data preserved
- Scaling calculations remain accurate

✅ **Backward Compatibility**
- Old code paths can coexist during transition
- Features degraded gracefully if backend is down
- No breaking changes to HTML structure

---

## API Configuration (Frontend)

Create a new `api-client.js` file to centralize API communication:

```javascript
// api-client.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = {
  async fetchYouTubeData(url) {
    return this.post('/api/youtube/extract', { url });
  },
  
  async parseIngredients(text) {
    return this.post('/api/ingredients/parse', { text });
  },
  
  async scaleRecipe(ingredients, originalServings, targetServings) {
    return this.post('/api/scaling/scale', {
      ingredients,
      original_servings: originalServings,
      target_servings: targetServings
    });
  },
  
  async searchYouTube(query, category, pageToken) {
    return this.post('/api/youtube/search', {
      query, category, page_token: pageToken
    });
  },
  
  async post(endpoint, body) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }
};
```

---

## Testing Checklist

- [ ] YouTube video extraction returns metadata
- [ ] Ingredient parsing extracts quantities and units correctly
- [ ] Recipe scaling calculates correct proportions
- [ ] YouTube search returns filtered, ranked results
- [ ] Pagination works with page tokens
- [ ] Error handling displays gracefully
- [ ] All UI elements remain functional
- [ ] SessionStorage operations preserve recipe data
- [ ] Recipe saving/loading works with new system

---

## Rollback Plan

If issues arise during migration:
1. Comment out backend calls in frontend
2. Uncomment original frontend logic
3. Features continue working with client-side processing
4. Fix backend issue and re-enable calls

---

## Success Criteria

✅ All core functionality accessible through RESTful API
✅ Frontend acts as thin client layer
✅ Zero changes to HTML/CSS
✅ All function signatures identical (where practical)
✅ All tests pass
✅ UI behavior unchanged from user perspective
✅ Backend handles all business logic and API integrations
✅ Clear error messages for debugging

