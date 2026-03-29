/**
 * ============================================================================
 * INTEGRATION GUIDE: UI CONTROLLER & APICLIENT
 * ============================================================================
 * 
 * This file demonstrates how the frontend layers work together.
 * 
 * For Developers:
 * - Understand the data flow
 * - Know where to add new features
 * - Know what NOT to modify
 * - Debug common issues
 * 
 * ============================================================================
 */

// ============================================================================
// LAYER 1: HTML (User Interface)
// ============================================================================

/*
  The HTML uses inline onclick handlers to trigger UI functions:
  
  <button onclick="fetchIngredients()">Fetch</button>
  <button onclick="searchYouTubeUI()">Search</button>
  <button onclick="deleteRecipeUI('recipe-id')">Delete</button>
  
  These functions must exist globally on window object.
  They are defined in ui-controller.js, NOT in HTML inline scripts.
*/

// ============================================================================
// LAYER 2: UI CONTROLLER (ui-controller.js) - WHERE YOU ARE NOW
// ============================================================================

/*
  RESPONSIBILITY: Bridge between HTML and API
  
  Tasks:
  1. Validate user input
     - isValidYouTubeUrl(url)
     - isValidSearchQuery(query)
     - etc.
  
  2. Manage UI state
     - showLoadingState()
     - hideLoadingState()
  
  3. Handle errors gracefully
     - showError(message)
     - showSuccess(message)
  
  4. Render responses to DOM
     - renderIngredientsList(ingredients)
     - renderSearchResults(results)
     - renderVideoThumbnail(url, title, youtubeUrl)
  
  5. Call apiClient methods
     - await apiClient.extractYouTubeMetadata(url)
     - await apiClient.searchYouTube(query, category, pageToken)
     - etc.
  
  Example Flow:
  ┌────────────────────────────────────────────────┐
  │ async function fetchIngredients() {            │
  │   // 1. VALIDATE                               │
  │   if (!isValidYouTubeUrl(url)) return;          │
  │                                                │
  │   // 2. LOADING STATE                          │
  │   showLoadingState();                          │
  │                                                │
  │   try {                                        │
  │     // 3. API CALL                             │
  │     const response = await                     │
  │       apiClient.extractYouTubeMetadata(url);   │
  │                                                │
  │     // 4. RENDER                               │
  │     renderVideoThumbnail(...);                 │
  │     renderIngredientsList(...);                │
  │   } catch (error) {                            │
  │     // 5. ERROR HANDLING                       │
  │     showError(error.message);                  │
  │   } finally {                                  │
  │     hideLoadingState();                        │
  │   }                                            │
  │ }                                              │
  └────────────────────────────────────────────────┘
*/

// ============================================================================
// LAYER 3: API CLIENT (api-client.js) - DO NOT MODIFY!
// ============================================================================

/*
  RESPONSIBILITY: Communication with backend
  
  Configuration:
  const API_CONFIG = {
    BASE_URL: 'http://localhost:8000' or current origin,
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 2,
  };
  
  Methods (NEVER modify):
  - apiClient.request(endpoint, method, body)      [Generic fetch]
  - apiClient.post(endpoint, body)                  [Shorthand]
  - apiClient.get(endpoint)                         [Shorthand]
  - apiClient.extractYouTubeMetadata(url)
  - apiClient.searchYouTube(query, category, pageToken)
  - apiClient.parseIngredients(text)
  - apiClient.extractIngredients(text, servingSize)
  - apiClient.scaleRecipe(ingredients, orig, target)
  - apiClient.getSubstitutions(...)
  - apiClient.analyzeNutrition(...)
  - apiClient.chatWithAssistant(...)
  - apiClient.translate(...)
  - apiClient.isHealthy()
  - apiClient.testConnectivity()
  
  Example Call:
  const response = await apiClient.extractYouTubeMetadata(url);
  
  Response Format (always):
  {
    success: true|false,
    data|metadata|results|ingredients: {...} or [...],
    error?: "error message if success=false",
    ...other fields
  }
*/

// ============================================================================
// LAYER 4: BACKEND API (FastAPI)
// ============================================================================

/*
  RESPONSIBILITY: Business logic, database, AI/ML
  
  Endpoints (examples):
  - POST /api/youtube/extract
    Request: { url: "..." }
    Response: { success: true, metadata: {...} }
  
  - POST /api/youtube/search
    Request: { query: "...", category: "...", page_token: "..." }
    Response: { success: true, results: [...], next_page_token: "..." }
  
  - POST /api/ingredients/parse
    Request: { text: "..." }
    Response: { success: true, ingredients: [...] }
  
  - POST /api/scaling/scale
    Request: { ingredients: [...], original_servings: n, target_servings: m }
    Response: { success: true, ingredients: [...], scale_factor: x }
  
  - GET /api/health
    Response: { status: "healthy" }
*/

// ============================================================================
// DATA FLOW EXAMPLE: YouTube Fetch
// ============================================================================

/*
  STEP 1: USER CLICKS BUTTON
  ├─ HTML: <button onclick="fetchIngredients()">Fetch Ingredients</button>
  │
  STEP 2: UI CONTROLLER EXECUTES
  ├─ Function: async function fetchIngredients()
  ├─ Validate: isValidYouTubeUrl(url)
  ├─ UI: showLoadingState()
  │
  STEP 3: CALL API CLIENT
  ├─ Code: const response = await apiClient.extractYouTubeMetadata(url)
  │
  STEP 4: API CLIENT MAKES HTTP REQUEST
  ├─ HTTP: POST http://localhost:8000/api/youtube/extract
  ├─ Body: { url: "https://youtube.com/watch?v=..." }
  │
  STEP 5: BACKEND PROCESSES
  ├─ Extract video ID from URL
  ├─ Fetch metadata from YouTube Data API
  ├─ Return thumbnail, title, description
  │
  STEP 6: BACKEND RETURNS RESPONSE
  ├─ Response: {
  │   success: true,
  │   metadata: {
  │     title: "Chocolate Cake Recipe",
  │     thumbnail_url: "https://...",
  │     description: "Ingredients: 2 cups flour, ..."
  │   }
  │ }
  │
  STEP 7: UI CONTROLLER PROCESSES RESPONSE
  ├─ Check: if (response.success && response.metadata)
  ├─ Render: renderVideoThumbnail(metadata.thumbnail_url, metadata.title, url)
  ├─ Parse: await parseIngredientsUI(metadata.description)
  ├─ UI: hideLoadingState()
  │
  STEP 8: DOM UPDATES
  └─ User sees: Thumbnail, title, and list of ingredients
*/

// ============================================================================
// COMMON PATTERNS - HOW TO ADD NEW FEATURES
// ============================================================================

/*
  PATTERN 1: Simple API Call with Validation
  
  async function myNewFeature() {
    // 1. Get & validate input
    const input = document.getElementById('myInput').value;
    if (!isValidInput(input)) {
      showError('Invalid input');
      return;
    }
    
    // 2. Show loading
    showLoadingState();
    
    try {
      // 3. Call API
      const response = await apiClient.myNewFeatureMethod(input);
      
      // 4. Check response
      if (!response.success) {
        showError('Operation failed');
        return;
      }
      
      // 5. Render results
      renderMyResults(response.data);
      showSuccess('Done!');
    } catch (error) {
      console.error('Error:', error);
      showError(`Error: ${error.message}`);
    } finally {
      hideLoadingState();
    }
  }
  
  // 2. Add to HTML:
  <button onclick="myNewFeature()">Do Something</button>
  
  // 3. Backend must provide endpoint:
  POST /api/my/endpoint
  Response: { success: true, data: {...} }
*/

/*
  PATTERN 2: Render Function
  
  function renderMyResults(results) {
    const container = getElement('myResultsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (!results || results.length === 0) {
      container.innerHTML = '<p>No results</p>';
      return;
    }
    
    const html = results.map(item => `
      <div class="result-item">
        <h3>${escapeHtml(item.title)}</h3>
        <p>${item.description}</p>
      </div>
    `).join('');
    
    container.innerHTML = html;
  }
*/

/*
  PATTERN 3: Error Handling Helpers
  
  function validateMyInput(input) {
    if (!input) return false;
    if (typeof input !== 'string') return false;
    if (input.trim().length < 3) return false;
    return true;
  }
  
  function showErrorForFeature(message) {
    console.error('MyFeature Error:', message);
    showError(message);
  }
*/

// ============================================================================
// WHAT TO MODIFY / NOT MODIFY
// ============================================================================

/*
  DO MODIFY:
  ✅ ui-controller.js
     - Add new UI functions
     - Add new render functions
     - Add new validation functions
  
  ✅ index.html
     - Add new buttons
     - Add new input fields
     - Update onclick handlers
  
  ✅ styles.css
     - Add new styles
     - Update colors, fonts, layout
  
  ✅ script.js (Legacy)
     - Move functions to ui-controller.js
     - Phase out old code
     - Keep for backward compatibility
  
  DO NOT MODIFY:
  ❌ api-client.js
     - This is the service layer
     - Backend depends on these method signatures
     - If you need new API method, ask backend team
  
  ❌ Network communication in ui-controller.js
     - Always use apiClient methods
     - Never use fetch() directly
     - Never modify request/response formats
*/

// ============================================================================
// DEBUGGING CHECKLIST
// ============================================================================

/*
  ISSUE: Buttons don't work
  Check:
  1. Browser console (F12) for errors
  2. Script loading order (api-client.js before ui-controller.js)
  3. Function names (fetchIngredients vs fetchIngredientsUI)
  4. HTML onclick syntax: onclick="myFunction(); return false;"
  
  ISSUE: API returns error
  Check:
  1. Backend is running on localhost:8000 (or correct URL)
  2. Browser Network tab (F12) to see request/response
  3. Response has { success: true } or { success: false }
  4. Error message in response.error or response.detail
  
  ISSUE: DOM not updating
  Check:
  1. Element ID is correct: getElement('myId')
  2. Element exists in HTML
  3. Container innerHTML is being set
  4. CSS display property isn't hiding it
  
  ISSUE: Validation failing
  Check:
  1. Input value is being trimmed()
  2. Regex patterns are correct
  3. Error message is shown to user
  4. Validation logic is in UI controller, not HTML
*/

// ============================================================================
// QUICK REFERENCE - KEY FUNCTIONS
// ============================================================================

/*
  INPUT VALIDATION
  
  function isValidYouTubeUrl(url)        → boolean
  function isValidSearchQuery(query)     → boolean
  function isValidScalingValue(value)    → boolean
  function getElement(elementId)         → Element | null
  function escapeHtml(text)              → string
  
  LOADING & FEEDBACK
  
  function showLoadingState()            → void
  function hideLoadingState()            → void
  function showError(message)            → void
  function showSuccess(message)          → void
  
  RENDERING
  
  function renderIngredientsList(items, containerId)
  function populateAvailableIngredientsDropdown(items)
  function renderVideoThumbnail(url, title, youtubeUrl, containerId)
  function renderSearchResults(results, containerId)
  function renderPaginationButtons(hasPrev, hasNext, prevToken, nextToken, containerId)
  function formatViewCount(count)        → string
  
  GLOBAL FUNCTIONS
  
  async function fetchIngredients()
  async function parseIngredientsUI(text)
  async function searchYouTubeUI(pageToken)
  function useVideoFromSearch(videoUrl)
  async function scaleRecipeUI()
  function updateScalingOptions()
  function loadSavedRecipes()
  function loadRecipeUI(recipeId)
  function deleteRecipeUI(recipeId)
  function saveRecipeUI()
  function initializeUI()
*/

// ============================================================================
// TESTING YOUR CHANGES
// ============================================================================

/*
  MANUAL TESTING
  
  1. Open browser console (F12)
  2. Type: fetchIngredients()
     (if no error, try other functions too)
  3. Check console for logs:
     "UI Controller: Fetching YouTube metadata"
  4. Check Network tab (F12 → Network)
     Should see POST /api/youtube/extract
  5. Check response status and body
  
  AUTOMATED TESTING (Future)
  
  // Example Jest tests (if added later)
  test('isValidYouTubeUrl rejects invalid URLs', () => {
    expect(isValidYouTubeUrl('not-a-url')).toBe(false);
    expect(isValidYouTubeUrl('https://youtube.com/watch?v=abc123')).toBe(true);
  });
  
  test('fetchIngredients shows error for empty URL', async () => {
    document.getElementById('youtubeLink').value = '';
    await fetchIngredients();
    // Check that showError was called
  });
*/

// ============================================================================
// SUMMARY
// ============================================================================

/*
  REMEMBER:
  
  1. UI Layer (HTML + ui-controller.js)
     ├─ Handles user input
     ├─ Validates data
     ├─ Shows/hides loading
     ├─ Handles errors
     └─ Renders DOM
  
  2. API Layer (api-client.js) ← DO NOT MODIFY
     ├─ Makes HTTP requests
     ├─ Handles timeout/retries
     ├─ Formats requests
     └─ Parses responses
  
  3. Backend Layer (FastAPI)
     ├─ Processes requests
     ├─ Calls YouTube API
     ├─ Parses text
     ├─ Scales recipes
     └─ Handles AI/ML
  
  BEST PRACTICES:
  
  ✅ Always validate input in UI controller
  ✅ Always use apiClient methods (never fetch directly)
  ✅ Always handle errors gracefully
  ✅ Always show loading state for async operations
  ✅ Always log to console for debugging
  ✅ Always render to DOM (don't alert too much)
  ✅ Always escape HTML for security
  ✅ Always check response.success before using data
  ✅ Always expose functions on window for HTML
  ✅ Never modify apiClient.js
  
  When adding a new feature, ask:
  1. Which UI elements do I need? (HTML)
  2. How do I validate input? (ui-controller)
  3. Which API method do I use? (apiClient)
  4. How do I render the response? (DOM rendering)
  5. What errors can occur? (Error handling)
*/

// ============================================================================
// END OF INTEGRATION GUIDE
// ============================================================================
