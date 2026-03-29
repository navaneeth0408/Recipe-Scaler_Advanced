# Recipe Scaler - Frontend Architecture

## Overview

The Recipe Scaler frontend has been refactored into a clean, layered architecture that separates concerns and improves maintainability.

```
┌─────────────────────────────────────────────────────────────────┐
│                         HTML LAYER                              │
│         (User Interface - index.html, enter_recipe.html)       │
│         onclick="fetchIngredients()" onclick="searchYouTubeUI()"│
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│               UI CONTROLLER LAYER (ui-controller.js)             │
│                                                                  │
│  • Input Validation                                              │
│  • Loading State Management                                      │
│  • Error Handling & User Feedback                                │
│  • DOM Rendering Functions                                       │
│  • Global Functions Exposed on window                            │
│                                                                  │
│  Global Functions:                                               │
│  ├── fetchIngredients()                                          │
│  ├── parseIngredientsUI(text)                                    │
│  ├── searchYouTubeUI(pageToken)                                  │
│  ├── useVideoFromSearch(url)                                     │
│  ├── scaleRecipeUI()                                             │
│  ├── updateScalingOptions()                                      │
│  ├── loadSavedRecipes()                                          │
│  ├── loadRecipeUI(id)                                            │
│  ├── deleteRecipeUI(id)                                          │
│  └── initializeUI()                                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│               API CLIENT LAYER (api-client.js)                   │
│                                                                  │
│  • Centralized API Communication                                 │
│  • Request/Response Formatting                                   │
│  • Error Handling                                                │
│  • Configuration (base URL, timeout, retries)                    │
│                                                                  │
│  API Methods:                                                    │
│  ├── extractYouTubeMetadata(url)                                 │
│  ├── searchYouTube(query, category, pageToken)                   │
│  ├── parseIngredients(text)                                      │
│  ├── scaleRecipe(ingredients, original, target)                  │
│  ├── getSubstitutions(...)                                       │
│  ├── analyzeNutrition(...)                                       │
│  ├── chatWithAssistant(...)                                      │
│  ├── translate(...)                                              │
│  └── isHealthy() / testConnectivity()                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                          │
│                  localhost:8000 (or similar)                     │
│                                                                  │
│  Endpoints:                                                      │
│  ├── POST /api/youtube/extract                                   │
│  ├── POST /api/youtube/search                                    │
│  ├── POST /api/ingredients/parse                                 │
│  ├── POST /api/scaling/scale                                     │
│  ├── POST /api/ai/...                                            │
│  └── GET /api/health                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

### Core Files

- **`index.html`** - Main page with search, scaling, and saved recipes
- **`api-client.js`** - ⚠️ **DO NOT MODIFY** - Centralized API communication
- **`ui-controller.js`** - **NEW** - UI bridge layer with input validation, error handling, and DOM rendering
- **`script.js`** - Legacy functionality (being phased into ui-controller)
- **`recipe-enhancements.js`** - Additional features
- **`styles.css`** - Styling (unchanged)

### Document Files (Reference)

- `ARCHITECTURE.md` - This file
- `README.md` - Project overview
- `FEATURES.md` - Feature documentation
- `QUICK_START.md` - User guide

---

## Data Flow Examples

### Example 1: Fetch Ingredients from YouTube

```
User Action: Click "Fetch Ingredients"
    │
    ├─> HTML: onclick="fetchIngredients()"
    │
    ├─> UI Controller: fetchIngredients()
    │       ├─ Validate: isValidYouTubeUrl()
    │       ├─ UI: showLoadingState()
    │       │
    │       ├─> API Client: apiClient.extractYouTubeMetadata(url)
    │       │       └─> Backend: POST /api/youtube/extract
    │       │           └─> Response: { success: true, metadata: {...} }
    │       │
    │       ├─ Render: renderVideoThumbnail(...)
    │       ├─> UI Controller: parseIngredientsUI(description)
    │       │       ├─> API Client: apiClient.parseIngredients(description)
    │       │       │   └─> Backend: POST /api/ingredients/parse
    │       │       │       └─> Response: { success: true, ingredients: [...] }
    │       │       │
    │       │       ├─ Render: renderIngredientsList(ingredients)
    │       │       └─ Render: populateAvailableIngredientsDropdown(...)
    │       │
    │       ├─ UI: hideLoadingState()
    │       └─ Feedback: showSuccess()
    │
    └─> DOM Updated: Thumbnail, title, ingredients displayed
```

### Example 2: Search YouTube

```
User Action: Click "Search YouTube"
    │
    ├─> HTML: onclick="searchYouTubeUI()"
    │
    ├─> UI Controller: searchYouTubeUI()
    │       ├─ Validate: isValidSearchQuery()
    │       ├─ UI: showLoadingState()
    │       │
    │       ├─> API Client: apiClient.searchYouTube(query, category, pageToken)
    │       │       └─> Backend: POST /api/youtube/search
    │       │           └─> Response: { success: true, results: [...], next_page_token: "..." }
    │       │
    │       ├─ Render: renderSearchResults(results)
    │       ├─ Render: renderPaginationButtons(...)
    │       │
    │       ├─ UI: hideLoadingState()
    │       └─ Feedback: showSuccess()
    │
    └─> DOM Updated: Search results with thumbnails, pagination
```

### Example 3: Use Video from Search

```
User Action: Click "Use This Recipe" on a search result
    │
    ├─> HTML: onclick="useVideoFromSearch('https://youtube.com/watch?v=...')"
    │
    ├─> UI Controller: useVideoFromSearch(videoUrl)
    │       ├─ Set input: document.getElementById('youtubeLink').value = videoUrl
    │       ├─ Switch tab to "Direct Link"
    │       ├─ Clear previous data
    │       │
    │       └─> Call: fetchIngredients() [goes back to Example 1]
    │
    └─> DOM Updated: Video ready for ingredient fetching
```

---

## UI Controller - Key Functions

### Input Validation Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `isValidYouTubeUrl(url)` | Check if URL is a YouTube link | `boolean` |
| `isValidSearchQuery(query)` | Check if search term is non-empty | `boolean` |
| `isValidScalingValue(value)` | Check if scaling value is positive number | `boolean` |

### Loading State Functions

| Function | Purpose |
|----------|---------|
| `showLoadingState()` | Display loading spinner |
| `hideLoadingState()` | Hide loading spinner |

### Error Handling Functions

| Function | Purpose |
|----------|---------|
| `showError(message)` | Show error alert to user |
| `showSuccess(message)` | Show success message (optional: upgrade to toast) |

### DOM Rendering Functions

| Function | Purpose |
|----------|---------|
| `renderIngredientsList(ingredients, containerId)` | Display ingredients as list |
| `populateAvailableIngredientsDropdown(ingredients)` | Fill dropdown for scaling |
| `renderVideoThumbnail(url, title, youtubeUrl, containerId)` | Display video info |
| `renderSearchResults(results, containerId)` | Display YouTube search results |
| `renderPaginationButtons(hasPrev, hasNext, prevToken, nextToken, containerId)` | Display pagination |

### Global UI Functions (exposed on window)

| Function | Purpose | Called From |
|----------|---------|-------------|
| `fetchIngredients()` | Get video metadata & ingredients | `onclick="fetchIngredients()"` |
| `parseIngredientsUI(text)` | Parse ingredients from text | Internal |
| `searchYouTubeUI(pageToken)` | Search YouTube for recipes | `onclick="searchYouTubeUI()"` |
| `useVideoFromSearch(url)` | Use video from search results | `onclick="useVideoFromSearch(...)"` |
| `scaleRecipeUI()` | Scale ingredients (placeholder) | `onclick="scaleRecipeUI()"` |
| `updateScalingOptions()` | Show/hide scaling input fields | `onchange="updateScalingOptions()"` |
| `loadSavedRecipes()` | Load recipes from localStorage | `initializeUI()` |
| `loadRecipeUI(id)` | Load specific recipe | `onclick="loadRecipeUI(...)"` |
| `deleteRecipeUI(id)` | Delete recipe | `onclick="deleteRecipeUI(...)"` |
| `initializeUI()` | Initialize all UI on page load | Auto on DOMContentLoaded |

---

## API Client - Key Methods

The `apiClient` object should **NEVER be modified**. All methods are pre-configured:

### YouTube Endpoints

```javascript
// Extract video metadata
await apiClient.extractYouTubeMetadata(url)
// Response: { success: true, metadata: { title, thumbnail_url, description } }

// Search for recipes
await apiClient.searchYouTube(query, category, pageToken)
// Response: { success: true, results: [...], next_page_token: "...", prev_page_token: "..." }
```

### Ingredient Endpoints

```javascript
// Parse ingredients from text
await apiClient.parseIngredients(text)
// Response: { success: true, ingredients: [...], extracted_count: number }

// Extract structured ingredients
await apiClient.extractIngredients(text, servingSize)
// Response: { success: true, ingredients: [...] }
```

### Scaling Endpoints

```javascript
// Scale recipe
await apiClient.scaleRecipe(ingredients, originalServings, targetServings)
// Response: { success: true, ingredients: [...], scale_factor: number }
```

### AI Endpoints

```javascript
// Get substitutions
await apiClient.getSubstitutions(ingredient, quantity, unit, dietaryPreference)

// Analyze nutrition
await apiClient.analyzeNutrition(ingredients, servings)

// Chat with assistant
await apiClient.chatWithAssistant(message, sessionId, recipeContext)

// Translate
await apiClient.translate(content, targetLanguage)
```

### Health Checks

```javascript
// Check if backend is healthy
await apiClient.isHealthy()  // Returns: true/false

// Test connectivity with timeout
await apiClient.testConnectivity()  // Returns: true/false
```

---

## Script Loading Order (in index.html)

```html
<script src="api-client.js"></script>       <!-- 1. API communication first -->
<script src="ui-controller.js"></script>    <!-- 2. UI layer second -->
<script src="script.js"></script>           <!-- 3. Legacy code third -->
<script src="recipe-enhancements.js"></script> <!-- 4. Enhancements last -->
```

**Why this order?**
- `api-client.js` must load first (UI controller depends on `apiClient`)
- `ui-controller.js` second (provides global UI functions)
- `script.js` third (can override/extend if needed)
- `recipe-enhancements.js` last (enhancement layer on top)

---

## Error Handling Strategy

### Frontend Errors (UI Layer)

| Scenario | Handling |
|----------|----------|
| Invalid YouTube URL | `showError()` - Ask user to enter valid URL |
| Empty search query | `showError()` - Ask user to enter search term |
| API call fails | `showError()` - Show error message to user |
| Missing DOM elements | `console.warn()` - Log to console, continue gracefully |
| Backend unavailable | `showError()` - Tell user to try again later |

### Console Logging

The UI controller uses `console.log()` and `console.error()` extensively for debugging:

```javascript
// Developers can see flow in browser console (F12)
console.log('UI Controller: Fetching YouTube metadata');
console.log(`UI Controller: Found ${results.length} results`);
console.error('UI Controller Error [fetchIngredients]:', error);
```

---

## Example: Adding a New Feature

To add a new feature that uses the backend, follow this pattern:

### 1. Add UI Controller Function

```javascript
// ui-controller.js

/**
 * FUNCTION: Do something new
 * 
 * @global
 */
async function doSomethingNewUI() {
  // === VALIDATION ===
  const input = document.getElementById('myInput')?.value || '';
  if (!isValid(input)) {
    showError('Please enter valid input.');
    return;
  }

  // === LOADING STATE ===
  showLoadingState();

  try {
    // === API CALL ===
    console.log('UI Controller: Calling API');
    const response = await apiClient.doSomethingNew(input);

    // === ERROR CHECK ===
    if (!response.success) {
      showError('Operation failed.');
      return;
    }

    // === RENDER ===
    renderResults(response.data);

    showSuccess('Done!');
  } catch (error) {
    console.error('UI Controller Error [doSomethingNewUI]:', error);
    showError(`Error: ${error.message}`);
  } finally {
    hideLoadingState();
  }
}
```

### 2. Add HTML Button

```html
<button onclick="doSomethingNewUI(); return false;">Do Something New</button>
```

### 3. Backend Must Provide API Endpoint

The `apiClient` already has a placeholder method ready. Just ensure backend responds with:

```json
{
  "success": true,
  "data": { ... }
}
```

---

## Placeholders for Future Features

These functions are placeholders and will throw user-friendly errors:

| Function | Status | Next Steps |
|----------|--------|-----------|
| `scaleRecipeUI()` | Placeholder | Needs backend scaling endpoint |
| `saveRecipeUI()` | Placeholder | Needs recipe storage logic |

To implement:

1. **Remove placeholder** from `ui-controller.js`
2. **Add backend endpoint** (FastAPI)
3. **Add `apiClient` method** (if not already there)
4. **Implement UI function** following the pattern above

---

## Debugging Tips

### Check Browser Console (F12)

The UI controller logs all major operations:

```
UI Controller: Initializing...
UI Controller: Fetching YouTube metadata
UI Controller: Parsed 15 ingredients
UI Controller: Found 6 results
UI Controller: Ready
```

### Check Network Tab (F12 → Network)

See all API calls to backend:

- `POST /api/youtube/extract` → Check response
- `POST /api/youtube/search` → Check pagination tokens
- `POST /api/ingredients/parse` → Check ingredients array

### Check Local Storage (F12 → Application)

Saved recipes stored under:

```
localStorage.savedRecipes
```

---

## Migration Notes

If modifying `script.js` or other files:

1. **DO NOT modify** `api-client.js`
2. **DO move functions to** `ui-controller.js` when possible
3. **Keep `script.js`** for legacy code (being phased out)
4. **Test in browser console** before using features

---

## Summary

This architecture provides:

✅ **Clear Separation of Concerns** - UI, API, Backend are distinct layers
✅ **Input Validation** - All user input validated before API calls
✅ **Error Handling** - Graceful degradation, user-friendly messages
✅ **DOM Rendering** - Centralized rendering functions
✅ **Debugging** - Console logs for tracing execution
✅ **Maintainability** - Easy to add features following the pattern
✅ **No Breaking Changes** - `apiClient` untouched, backward compatible

