# Frontend JavaScript Migration - Updated Functions

This file shows the minimal changes needed to migrate `script.js` functions to use the backend API.
The function names and UI behavior remain identical - only the implementation changes to call the backend.

## Step 1: Add script tag to index.html

Before the closing `</body>` tag in `index.html`, make sure `api-client.js` is loaded BEFORE `script.js`:

```html
  <script src="api-client.js"></script>
  <script src="script.js"></script>
</body>
```

## Step 2: Updated script.js Functions

Replace the following functions in `script.js` with these versions that call the backend:

---

### Function 1: `fetchIngredients()` - YouTube Video Extraction

**Original:** Calls YouTube API directly
**Updated:** Calls backend `/api/youtube/extract` endpoint

```javascript
async function fetchIngredients() {
  const youtubeLink = document.getElementById("youtubeLink").value;
  
  if (!youtubeLink.trim()) {
    alert('Please enter a valid YouTube Video URL.');
    return;
  }

  showLoading();

  try {
    // Call backend API instead of YouTube API directly
    const response = await apiClient.extractYouTubeMetadata(youtubeLink);
    
    if (response.success && response.metadata) {
      const metadata = response.metadata;
      displayThumbnail(metadata.thumbnail_url, metadata.title);
      
      // Parse ingredients from the description using backend
      await parseIngredients(metadata.description);
    } else {
      alert('Error: Could not extract video metadata');
    }
  } catch (error) {
    console.error('Error fetching video:', error);
    alert('Error fetching video: ' + error.message);
  } finally {
    hideLoading();
  }
}
```

**Changes Made:**
- ✅ Function name unchanged: `fetchIngredients()`
- ✅ UI flow unchanged: Shows loading, displays thumbnail, parses ingredients
- ✅ Error handling: User-friendly messages
- ✅ Logic moved: YouTube API calls → Backend handles them

**Benefits:**
- API key stays on backend (more secure)
- YouTube quota managed centrally
- Caching happens on backend

---

### Function 2: `parseIngredients()` - Ingredient Extraction from Text

**Original:** Regex-based parsing in JavaScript
**Updated:** Calls backend `/api/ingredients/parse` endpoint

```javascript
async function parseIngredients(description) {
  if (!description) {
    console.warn('No description provided for ingredient parsing');
    return;
  }

  try {
    // Call backend to parse ingredients from description
    const response = await apiClient.parseIngredients(description);
    
    if (response.success && response.ingredients) {
      // Populate available ingredients dropdown for scaling
      populateAvailableIngredients(response.ingredients);
      
      // Display ingredients to user
      displayIngredientsList(response.ingredients);
    } else {
      console.warn('No ingredients extracted from description');
      displayIngredientsList([]);
    }
  } catch (error) {
    console.error('Error parsing ingredients:', error);
    // Graceful degradation: show empty list instead of error
    displayIngredientsList([]);
  }
}

/**
 * Helper: Display parsed ingredients in the UI
 * (Frontend-only: DOM manipulation stays on client)
 */
function displayIngredientsList(ingredients) {
  const ingredientsList = document.getElementById("ingredientsList");
  if (!ingredientsList) return;

  ingredientsList.innerHTML = "";
  
  ingredients.forEach(ingredient => {
    const div = document.createElement("div");
    div.className = "ingredient-entry";
    
    // Format ingredient display
    const quantity = ingredient.quantity || 1;
    const unit = ingredient.unit || '';
    const name = ingredient.name || '';
    const text = `${quantity} ${unit} ${name}`.trim();
    
    div.innerHTML = `<input type="text" value="${text}" readonly class="ingredient-name">`;
    ingredientsList.appendChild(div);
  });
}

/**
 * Helper: Populate dropdown for "Available Ingredients" scaling mode
 */
function populateAvailableIngredients(ingredients) {
  const dropdown = document.getElementById("availableIngredient");
  if (!dropdown) return;

  dropdown.innerHTML = '';
  
  ingredients.forEach((ingredient, index) => {
    const option = document.createElement('option');
    option.value = index;
    option.innerText = ingredient.name;
    dropdown.appendChild(option);
  });
}
```

**Changes Made:**
- ✅ Function name unchanged: `parseIngredients()`
- ✅ UI flow unchanged: Displays ingredients, populates dropdowns
- ✅ Logic moved: Complex regex parsing → Backend handles it
- ✅ Added helper functions: Kept DOM manipulation on frontend
- ✅ Error handling: Gracefully falls back to empty list

**Benefits:**
- Complex parsing logic centralized on backend
- Easier to update parsing rules (no frontend deployment needed)
- Backend can use NLP/ML models for better extraction
- Reduced JavaScript complexity

---

### Function 3: `scaleFetchedIngredients()` - Recipe Scaling

**Original:** JavaScript calculates scaling factors
**Updated:** Calls backend `/api/scaling/scale` endpoint

```javascript
async function scaleFetchedIngredients() {
  const scalingValue = parseFloat(document.getElementById("scalingValue").value);

  if (isNaN(scalingValue) || scalingValue <= 0) {
    alert("Please enter a valid scaling value.");
    return;
  }

  showLoading();

  try {
    // Collect current ingredients
    const ingredientElements = document.querySelectorAll("#ingredientsList .ingredient-entry");
    
    if (ingredientElements.length === 0) {
      alert("No ingredients found. Please fetch ingredients first.");
      hideLoading();
      return;
    }

    // Build ingredients list from current display
    const ingredients = Array.from(ingredientElements).map((ing, index) => ({
      name: ing.querySelector(".ingredient-name").value,
      quantity: 1, // Backend will parse from the full text
      unit: 'whole'
    }));

    // Call backend to scale
    const response = await apiClient.scaleRecipe(
      ingredients,
      1, // original servings
      scalingValue // target servings
    );

    if (response.success && response.ingredients) {
      // Format scaled ingredients for display
      const scaledIngredients = response.ingredients.map(ing => {
        const qty = formatQuantity(ing.quantity);
        const unit = ing.unit || '';
        return `${qty} ${unit} ${ing.name}`.trim();
      });

      // Get recipe title
      const titleElement = document.querySelector("#thumbnailContainer p");
      const recipeName = titleElement ? titleElement.innerText : "Scaled Recipe";

      // Store in session storage
      sessionStorage.setItem('recipeName', recipeName);
      sessionStorage.setItem('mainIngredient', '');
      sessionStorage.setItem('scaledIngredients', scaledIngredients.join("<br>"));
      sessionStorage.setItem('youtubeVideoUrl', document.getElementById("youtubeLink").value);
      sessionStorage.setItem('isManualRecipe', 'false');

      // Navigate to results page
      window.location.href = "scaled.html";
    } else {
      alert('Error scaling ingredients: ' + response.error);
    }
  } catch (error) {
    console.error('Error scaling recipe:', error);
    alert('Error: ' + error.message);
  } finally {
    hideLoading();
  }
}
```

**Changes Made:**
- ✅ Function name unchanged: `scaleFetchedIngredients()`
- ✅ UI flow unchanged: Shows loading, navigates to scaled.html
- ✅ Logic moved: Math calculations → Backend handles scaling
- ✅ SessionStorage usage unchanged: Still stores results
- ✅ Error handling: User feedback on failure

**Benefits:**
- Accurate quantity parsing on backend
- Consistent scaling logic across all clients
- Backend can support advanced scaling modes (unit conversion, etc)

---

### Function 4: `searchYouTube()` - YouTube Search

**Original:** Calls YouTube API, filters results in JavaScript
**Updated:** Calls backend `/api/youtube/search` endpoint

```javascript
let nextPageToken = '';
let prevPageToken = '';
let currentQuery = '';
let currentCategory = '';

async function searchYouTube(pageToken = '') {
  showLoading();

  const query = document.getElementById('searchQuery').value;
  const category = document.getElementById('recipeCategory').value;

  currentQuery = query;
  currentCategory = category;

  if (!query) {
    hideLoading();
    alert('Please enter a search term');
    return;
  }

  try {
    // Call backend search API
    const response = await apiClient.searchYouTube(query, category, pageToken);

    if (response.success && response.results) {
      nextPageToken = response.next_page_token || '';
      prevPageToken = response.prev_page_token || '';

      displaySearchResults(response.results);
      createPagination();
    } else {
      displaySearchResults([]);
      createPagination();
    }
  } catch (error) {
    console.error('Error searching YouTube:', error);
    alert('Error searching YouTube: ' + error.message);
  } finally {
    hideLoading();
  }
}

/**
 * Helper: Display search results
 * Note: This function already existed and handles UI - no changes needed
 * But updated to work with new response format
 */
function displaySearchResults(results) {
  const resultsContainer = document.getElementById('searchResults');
  resultsContainer.innerHTML = '';

  if (!results || results.length === 0) {
    resultsContainer.innerHTML = '<p>No results found. Try a different search term.</p>';
    return;
  }

  const resultsGrid = document.createElement('div');
  resultsGrid.className = 'search-results';

  results.forEach(result => {
    const resultCard = document.createElement('div');
    resultCard.className = 'search-result-item';

    // Format published date
    const publishedDate = new Date(result.published_date);
    const formattedDate = publishedDate.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });

    // Format view count
    const views = result.views ? formatViewCount(result.views) : 'N/A';

    resultCard.innerHTML = `
      <img src="${result.thumbnail_url}" alt="${result.title}" class="search-result-thumb">
      <div class="search-result-info">
        <h3 class="search-result-title">${result.title}</h3>
        <div class="search-result-channel">${result.channel}</div>
        <div class="search-result-views">${views} views • ${formattedDate}</div>
        <div class="search-result-buttons">
          <button onclick="useVideo('https://www.youtube.com/watch?v=${result.video_id}')" class="search-result-button">Use This Recipe</button>
          <button onclick="window.open('https://www.youtube.com/watch?v=${result.video_id}', '_blank')" class="search-result-button">Watch</button>
        </div>
      </div>
    `;

    resultsGrid.appendChild(resultCard);
  });

  resultsContainer.appendChild(resultsGrid);
}

/**
 * Helper: Create pagination buttons
 * (Already existed, kept as-is)
 */
function createPagination() {
  const paginationContainer = document.getElementById('pagination');
  paginationContainer.innerHTML = '';

  if (prevPageToken) {
    const prevButton = document.createElement('button');
    prevButton.className = 'pagination-button';
    prevButton.innerHTML = '&laquo; Previous';
    prevButton.onclick = () => searchYouTube(prevPageToken);
    paginationContainer.appendChild(prevButton);
  }

  if (nextPageToken) {
    const nextButton = document.createElement('button');
    nextButton.className = 'pagination-button';
    nextButton.innerHTML = 'Next &raquo;';
    nextButton.onclick = () => searchYouTube(nextPageToken);
    paginationContainer.appendChild(nextButton);
  }
}
```

**Changes Made:**
- ✅ Function name unchanged: `searchYouTube()`
- ✅ UI flow unchanged: Shows results grid with pagination
- ✅ Logic moved: Filtering and ranking → Backend handles it
- ✅ Global variables maintained: `nextPageToken`, `prevPageToken`
- ✅ Pagination works the same way

**Benefits:**
- Backend filters out shorts automatically
- Ranking algorithm stays up-to-date centrally
- API key management centralized
- More efficient (backend batches API calls)

---

## Step 3: Remove/Update Functions (Deletion/Modification)

### Remove from script.js (no longer needed):

1. **`getVideoId()`** - Backend handles this
2. **`filterSearchResults()`** - Backend handles this
3. **`isYoutubeShort()`** - Backend handles this
4. **`parseDuration()`** - Backend handles this
5. **Direct YouTube API calls** - All moved to backend

### Keep as-is (UI-only functions):

- `showLoading()` / `hideLoading()`
- `displayThumbnail()`
- `addIngredient()`
- `updateScalingOptions()`
- `formatQuantity()`
- `saveRecipe()` / `loadSavedRecipes()` / etc.
- `printRecipe()` / `exportPDF()` / `exportText()` / etc.
- `useVideo()`
- All DOM manipulation functions

---

## Step 4: Fallback Strategy (Optional but Recommended)

For robustness, you can add fallback logic if backend is unavailable:

```javascript
/**
 * Wrapper function with fallback to old logic
 */
async function fetchIngredientsWithFallback() {
  try {
    // Check if backend is available
    const isBackendAvailable = await apiClient.testConnectivity();
    
    if (isBackendAvailable) {
      // Use new backend-based approach
      await fetchIngredients();
    } else {
      console.warn('Backend unavailable, using client-side parsing');
      // Fallback: fetch YouTube data and use old parsing logic
      fetchIngredientsLegacy();
    }
  } catch (error) {
    console.warn('Error in fallback check:', error);
    // Default to legacy approach
    fetchIngredientsLegacy();
  }
}
```

---

## Migration Checklist

- [ ] Add `api-client.js` to HTML (before `script.js`)
- [ ] Update `fetchIngredients()` to use `apiClient.extractYouTubeMetadata()`
- [ ] Update `parseIngredients()` to use `apiClient.parseIngredients()`
- [ ] Update `scaleFetchedIngredients()` to use `apiClient.scaleRecipe()`
- [ ] Update `searchYouTube()` to use `apiClient.searchYouTube()`
- [ ] Remove old API call functions (listed above)
- [ ] Test YouTube extraction works
- [ ] Test ingredient parsing works
- [ ] Test recipe scaling works
- [ ] Test YouTube search works
- [ ] Test pagination
- [ ] Test error handling
- [ ] Verify UI behavior unchanged

---

## Quick Reference: What Changed vs What Didn't

| Aspect | Changed | Unchanged |
|--------|---------|-----------|
| Function names | ❌ No | ✅ Yes |
| HTML structure | ❌ No | ✅ Yes |
| CSS styling | ❌ No | ✅ Yes |
| DOM manipulation | ❌ No | ✅ Yes |
| User interactions | ❌ No | ✅ Yes |
| Business logic location | ✅ Yes | → Moved to backend |
| API integrations | ✅ Yes | → Now via backend |
| Data flow | ✅ Yes | → Backend processes |

---

## API Response Format Examples

### YouTube Extraction
```json
{
  "metadata": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Amazing Pasta Recipe",
    "description": "Ingredients:\n2 cups flour...",
    "channel_name": "Cooking Channel",
    "thumbnail_url": "https://...",
    "duration": "10:30"
  },
  "success": true
}
```

### Ingredient Parsing
```json
{
  "ingredients": [
    {"name": "flour", "quantity": 2, "unit": "cup"},
    {"name": "sugar", "quantity": 0.5, "unit": "cup"}
  ],
  "extracted_count": 2,
  "success": true
}
```

### Recipe Scaling
```json
{
  "scale_factor": 2,
  "ingredients": [
    {"name": "flour", "quantity": 4, "unit": "cup"},
    {"name": "sugar", "quantity": 1, "unit": "cup"}
  ],
  "success": true
}
```

### YouTube Search
```json
{
  "results": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Pasta Recipe",
      "channel": "Cooking",
      "thumbnail_url": "https://...",
      "views": 100000,
      "duration_seconds": 600
    }
  ],
  "next_page_token": "...",
  "success": true
}
```

