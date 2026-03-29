/**
 * ============================================================================
 * UI CONTROLLER / BRIDGE LAYER
 * ============================================================================
 * 
 * This file serves as the bridge between the HTML UI and the apiClient.
 * 
 * ARCHITECTURE:
 *   HTML (onclick handlers) → UI Controller → apiClient → Backend API
 *                          ↓
 *                   DOM Rendering
 * 
 * RESPONSIBILITIES:
 *   1. Expose global functions for HTML onclick handlers
 *   2. Validate user input before API calls
 *   3. Show/hide loading states
 *   4. Handle errors gracefully
 *   5. Render API responses into the DOM
 *   6. Manage session/local storage for navigation
 * 
 * DO NOT MODIFY: The apiClient object (api-client.js)
 * DO NOT ADD: New frameworks or complex libraries
 * 
 * ============================================================================
 */

// ============================================================================
// INPUT VALIDATION HELPERS
// ============================================================================

/**
 * Validates a YouTube URL
 * Accepts: youtube.com/watch?v=..., youtu.be/..., youtube.com/embed/...
 */
function isValidYouTubeUrl(url) {
  if (!url || typeof url !== 'string') return false;
  const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\//;
  return youtubeRegex.test(url.trim());
}

/**
 * Validates a search query (non-empty string)
 */
function isValidSearchQuery(query) {
  return query && typeof query === 'string' && query.trim().length > 0;
}

/**
 * Validates scaling value (positive number)
 */
function isValidScalingValue(value) {
  const num = parseFloat(value);
  return !isNaN(num) && num > 0;
}

/**
 * Safe DOM element getter with error handling
 */
function getElement(elementId) {
  const element = document.getElementById(elementId);
  if (!element) {
    console.warn(`UI Controller: Element with ID "${elementId}" not found`);
  }
  return element;
}

// ============================================================================
// LOADING STATE MANAGEMENT
// ============================================================================

/**
 * Show loading spinner
 * Expects: <div id="loading" class="loading"></div> in HTML
 */
function showLoadingState() {
  const loadingEl = getElement('loading');
  if (loadingEl) {
    loadingEl.style.display = 'block';
  }
}

/**
 * Hide loading spinner
 */
function hideLoadingState() {
  const loadingEl = getElement('loading');
  if (loadingEl) {
    loadingEl.style.display = 'none';
  }
}

// ============================================================================
// ERROR HANDLING & USER FEEDBACK
// ============================================================================

/**
 * Display error message to user
 * Uses alert for now; can be upgraded to toast notifications
 */
function showError(message) {
  const fullMessage = message || 'An unexpected error occurred. Please try again.';
  console.error('UI Error:', fullMessage);
  alert(fullMessage);
}

/**
 * Display success message to user
 */
function showSuccess(message) {
  console.log('UI Success:', message);
  // Could upgrade to toast notification
  // alert(message); // Optional: uncomment for visible feedback
}

// ============================================================================
// DOM RENDERING HELPERS - INGREDIENTS
// ============================================================================

/**
 * Render a list of ingredients to the DOM
 * @param {Array} ingredients - Array of ingredient objects
 * @param {string} containerId - ID of container element
 */
function renderIngredientsList(ingredients, containerId = 'ingredientsList') {
  window.currentIngredients = ingredients;

  const container = getElement(containerId);
  if (!container) return;

  container.innerHTML = '';

  if (!ingredients || ingredients.length === 0) {
    container.innerHTML = '<p style="color: #666;">No ingredients found. Try a different video.</p>';
    return;
  }

  ingredients.forEach((ingredient, index) => {
    const quantity = ingredient.quantity || 1;
    const unit = ingredient.unit || '';
    const name = ingredient.name || 'Unknown';
    let displayText;

    // Visible text inside the card, e.g. "1 cup milk"
    const isWhole = unit.trim().toLowerCase() === 'whole';
    if (isWhole) {
      if (quantity === 1) {
        displayText = name.trim();
      } else {
        displayText = `${quantity} ${name}`.replace(/\s+/g, ' ').trim();
      }
    } else {
      displayText = `${quantity} ${unit} ${name}`.replace(/\s+/g, ' ').trim();
    }

    const div = document.createElement('div');
    div.className = 'ingredient-card';
    div.style.backgroundColor = 'white';
    div.style.padding = '15px';
    div.style.borderRadius = '10px';
    div.style.boxShadow = '0 2px 8px rgba(0,0,0,0.05)';
    div.style.marginBottom = '15px';
    div.style.maxWidth = '80%';
    div.style.marginLeft = 'auto';
    div.style.marginRight = 'auto';
    div.style.display = 'flex';
    div.style.flexDirection = 'column';

    const row = document.createElement('div');
    row.style.display = 'flex';
    row.style.justifyContent = 'space-between';
    row.style.alignItems = 'center';
    row.style.gap = '15px';
    row.style.width = '100%';
    row.style.flexWrap = 'wrap';

    row.innerHTML = `
      <input 
        type="text" 
        value="${displayText}" 
        readonly 
        class="ingredient-name"
        data-ingredient-index="${index}"
        style="flex-grow: 1; margin: 0; min-width: 200px;"
      >
      <button class="substitute-btn" style="background-color: #F2D479; color: #333; margin: 0; padding: 10px 15px; border-radius: 6px; font-weight: 600; white-space: nowrap;">Find Substitute</button>
    `;

    const dropdown = document.createElement('div');
    dropdown.className = 'substitute-dropdown';
    dropdown.style.display = 'none';
    dropdown.style.backgroundColor = '#f9f9f9';
    dropdown.style.border = '1px solid #e0e0e0';
    dropdown.style.borderRadius = '8px';
    dropdown.style.padding = '15px';
    dropdown.style.marginTop = '15px';
    dropdown.style.textAlign = 'left';

    const btn = row.querySelector('.substitute-btn');
    btn.onclick = (e) => {
      e.stopPropagation();
      handleIngredientClick(ingredient, dropdown, btn);
    };

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!div.contains(e.target) && dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
      }
    });

    div.appendChild(row);
    div.appendChild(dropdown);
    container.appendChild(div);
  });
}

async function handleIngredientClick(ingredient, dropdown, btn) {
  if (dropdown.style.display === 'block') {
    dropdown.style.display = 'none';
    return;
  }

  // Close other open dropdowns
  document.querySelectorAll('.substitute-dropdown').forEach(d => {
    if (d !== dropdown) d.style.display = 'none';
  });

  dropdown.style.display = 'block';

  if (dropdown.hasAttribute('data-fetched')) {
    return; // Already loaded
  }

  dropdown.innerHTML = '<p style="margin:0; color:#666;">Finding substitutes <i class="fas fa-spinner fa-spin"></i></p>';

  try {
    const data = await apiClient.getSubstitutions(
      ingredient.name,
      ingredient.quantity,
      ingredient.unit
    );

    renderSubstitutions(data, dropdown);
    dropdown.setAttribute('data-fetched', 'true');

  } catch (error) {
    console.error('UI Controller Error [handleIngredientClick]:', error);
    dropdown.innerHTML = '<p style="color:red; margin:0;">Failed to fetch substitutions.</p>';
  }
}

function renderSubstitutions(data, container) {
  if (!container) return;
  container.innerHTML = "";

  if (!data || !data.substitutions || data.substitutions.length === 0) {
    container.innerHTML = '<p style="margin:0;">No substitutions found.</p>';
    return;
  }

  const heading = document.createElement("h4");
  heading.innerText = "Substitutions";
  heading.style.marginTop = "0";
  heading.style.marginBottom = "10px";
  heading.style.color = "#5a8c5a";
  container.appendChild(heading);

  data.substitutions.forEach(sub => {
    const div = document.createElement("div");
    div.style.borderLeft = "3px solid #E63946";
    div.style.paddingLeft = "10px";
    div.style.marginBottom = "10px";

    div.innerHTML = `
            <strong style="display:block; color:#333;">${sub.substitute}</strong>
            <span style="font-size:0.9rem; color:#666; display:block;">Use: ${sub.updated_quantity}</span>
            <small style="color:#888; display:block;">${sub.reason || ''}</small>
        `;

    container.appendChild(div);
  });
}

/**
 * Populate "Available Ingredients" dropdown for scaling mode
 * @param {Array} ingredients - Array of ingredient objects
 */
function populateAvailableIngredientsDropdown(ingredients) {
  const dropdown = getElement('availableIngredient');
  if (!dropdown) return;

  dropdown.innerHTML = '';

  if (!ingredients || ingredients.length === 0) {
    const option = document.createElement('option');
    option.innerText = 'No ingredients available';
    option.disabled = true;
    dropdown.appendChild(option);
    return;
  }

  ingredients.forEach((ingredient, index) => {
    const option = document.createElement('option');
    option.value = index;
    option.innerText = ingredient.name || `Ingredient ${index + 1}`;
    dropdown.appendChild(option);
  });
}

// ============================================================================
// DOM RENDERING HELPERS - YOUTUBE THUMBNAIL
// ============================================================================

/**
 * Render YouTube video thumbnail and metadata
 * @param {string} thumbnailUrl - URL to video thumbnail
 * @param {string} videoTitle - Title of the video
 * @param {string} youtubeUrl - Full YouTube URL
 * @param {string} containerId - ID of container element
 */
function renderVideoThumbnail(thumbnailUrl, videoTitle, youtubeUrl, containerId = 'thumbnailContainer') {
  const container = getElement(containerId);
  if (!container) return;

  container.innerHTML = '';

  // Image
  const img = document.createElement('img');
  img.src = thumbnailUrl;
  img.alt = 'YouTube Thumbnail';
  img.loading = 'eager';
  img.onerror = () => {
    img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%23ccc" width="320" height="180"/%3E%3C/svg%3E';
  };
  container.appendChild(img);

  // Title
  const title = document.createElement('p');
  title.innerText = videoTitle || 'Untitled Video';
  title.style.fontWeight = 'bold';
  title.style.marginTop = '10px';
  container.appendChild(title);

  // Link to watch on YouTube
  if (youtubeUrl) {
    const linkContainer = document.createElement('div');
    linkContainer.className = 'video-source';

    const link = document.createElement('a');
    link.href = youtubeUrl;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.innerHTML = '<i class="fab fa-youtube"></i> Watch on YouTube';

    linkContainer.appendChild(link);
    container.appendChild(linkContainer);
  }
}

// ============================================================================
// DOM RENDERING HELPERS - SEARCH RESULTS
// ============================================================================

/**
 * Render YouTube search results to the DOM
 * @param {Array} results - Array of search result objects
 * @param {string} containerId - ID of results container
 */
function renderSearchResults(results, containerId = 'searchResults') {
  const container = getElement(containerId);
  if (!container) return;

  container.innerHTML = '';

  if (!results || results.length === 0) {
    container.innerHTML = '<p style="color: #666; padding: 20px;">No results found. Try a different search term.</p>';
    return;
  }

  const grid = document.createElement('div');
  grid.className = 'search-results';

  results.forEach(result => {
    const card = document.createElement('div');
    card.className = 'search-result-item';

    const publishedDate = new Date(result.published_date);
    const formattedDate = publishedDate.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });

    const views = result.views ? formatViewCount(result.views) : 'N/A';
    const videoUrl = `https://www.youtube.com/watch?v=${result.video_id}`;

    card.innerHTML = `
      <img 
        src="${result.thumbnail_url}" 
        alt="${result.title}" 
        class="search-result-thumb"
        onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22160%22 height=%2290%22%3E%3Crect fill=%22%23ccc%22 width=%22160%22 height=%2290%22/%3E%3C/svg%3E'"
      >
      <div class="search-result-info">
        <h3 class="search-result-title">${escapeHtml(result.title)}</h3>
        <div class="search-result-channel">${escapeHtml(result.channel || 'Unknown Channel')}</div>
        <div class="search-result-views">${views} views • ${formattedDate}</div>
        <div class="search-result-buttons">
          <button class="search-result-button" onclick="useVideoFromSearch('${videoUrl}')">Use This Recipe</button>
          <button class="search-result-button" onclick="window.open('${videoUrl}', '_blank')">Watch</button>
        </div>
      </div>
    `;

    grid.appendChild(card);
  });

  container.appendChild(grid);
}

/**
 * Render pagination buttons
 * @param {boolean} hasPrev - Whether there's a previous page
 * @param {boolean} hasNext - Whether there's a next page
 * @param {string} prevToken - Previous page token
 * @param {string} nextToken - Next page token
 * @param {string} containerId - ID of pagination container
 */
function renderPaginationButtons(hasPrev, hasNext, prevToken, nextToken, containerId = 'pagination') {
  const container = getElement(containerId);
  if (!container) return;

  container.innerHTML = '';

  if (hasPrev && prevToken) {
    const prevBtn = document.createElement('button');
    prevBtn.className = 'pagination-button';
    prevBtn.innerHTML = '&laquo; Previous';
    prevBtn.onclick = () => searchYouTubeUI(prevToken);
    container.appendChild(prevBtn);
  }

  if (hasNext && nextToken) {
    const nextBtn = document.createElement('button');
    nextBtn.className = 'pagination-button';
    nextBtn.innerHTML = 'Next &raquo;';
    nextBtn.onclick = () => searchYouTubeUI(nextToken);
    container.appendChild(nextBtn);
  }
}

/**
 * Helper: Format view count (1000 -> 1K, 1000000 -> 1M)
 */
function formatViewCount(viewCount) {
  const count = parseInt(viewCount, 10);
  if (isNaN(count)) return '0';
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
}

/**
 * Helper: Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  if (!text) return '';
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// ============================================================================
// GLOBAL UI FUNCTIONS (Exposed on window for HTML onclick handlers)
// ============================================================================

/**
 * FUNCTION: Fetch ingredients from YouTube video
 * 
 * UI Flow:
 *   1. Validate YouTube URL input
 *   2. Show loading state
 *   3. Call apiClient.extractYouTubeMetadata()
 *   4. Render thumbnail
 *   5. Parse & render ingredients
 *   6. Hide loading state
 * 
 * Error Handling: Graceful - shows user-friendly messages
 * 
 * @global
 */
async function fetchIngredients() {
  // === INPUT VALIDATION ===
  const youtubeLink = document.getElementById('youtubeLink')?.value || '';

  if (!isValidYouTubeUrl(youtubeLink)) {
    showError('Please enter a valid YouTube Video URL.\n\nExamples:\n• youtube.com/watch?v=...\n• youtu.be/...');
    return;
  }

  // === LOADING STATE ===
  showLoadingState();

  try {
    // === API CALL ===
    console.log('UI Controller: Fetching YouTube metadata');
    const response = await apiClient.extractYouTubeMetadata(youtubeLink.trim());

    // === ERROR CHECKING ===
    if (!response.success || !response.metadata) {
      showError('Could not extract video information. Try another video.');
      return;
    }

    const metadata = response.metadata;

    // === STORE RECIPE METADATA FOR SCALED PAGE ===
    sessionStorage.setItem('recipeName', metadata.title || 'Scaled Recipe');
    sessionStorage.setItem('mainIngredient', metadata.channel || '');
    sessionStorage.setItem('youtubeVideoUrl', youtubeLink.trim());

    // === RENDER THUMBNAIL ===
    renderVideoThumbnail(
      metadata.thumbnail_url,
      metadata.title,
      youtubeLink
    );

    // === PARSE & RENDER INGREDIENTS ===
    let ingredientsFound = false;
    const description = metadata.description || '';
    const isLikelyIngredientList = description.includes('\n') && description.length < 3000;
    if (description && isLikelyIngredientList) {
      console.log('UI Controller: Parsing ingredients from description');
      ingredientsFound = await parseIngredientsUI(description);
    }

    if (!ingredientsFound) {
      console.log('UI Controller: No ingredients in description, falling back to audio extraction');
      const loadingEl = getElement('loading');
      const originalLoadingHtml = loadingEl ? loadingEl.innerHTML : '';
      if (loadingEl) {
        loadingEl.innerHTML = `
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px;">
            <div style="margin: 0 auto 15px; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #E63946; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <p style="margin-top: 15px; color: #2B2D42; font-size: 15px; text-align: center; font-weight: 500;">No ingredients in description.<br>Extracting from audio...</p>
            <p style="margin-top: 5px; color: #666; font-size: 13px; text-align: center;">(This may take up to a minute)</p>
          </div>
        `;
      }

      // Call audio extraction with the URL
      await extractAudioIngredients(youtubeLink.trim());

      // Restore original loading element HTML for future calls
      if (loadingEl) {
        loadingEl.innerHTML = originalLoadingHtml;
      }
    } else {
      showSuccess('Video loaded successfully!');
    }
  } catch (error) {
    console.error('UI Controller Error [fetchIngredients]:', error);
    showError(`Error fetching video:\n${error.message}`);
  } finally {
    hideLoadingState();
  }
}

/**
 * FUNCTION: Parse ingredients from raw text
 * 
 * Backend does the heavy lifting; UI just renders the result.
 * 
 * @param {string} text - Raw text to parse (from YouTube description, etc.)
 * @global
 */
async function parseIngredientsUI(text) {
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    console.warn('UI Controller: No text to parse');
    return false;
  }

  try {
    console.log('UI Controller: Calling apiClient.parseIngredients()');
    const response = await apiClient.parseIngredients(text);

    if (response.success && response.ingredients) {
      // === RENDER INGREDIENTS ===
      renderIngredientsList(response.ingredients);

      // === POPULATE DROPDOWN ===
      populateAvailableIngredientsDropdown(response.ingredients);

      console.log(`UI Controller: Parsed ${response.ingredients.length} ingredients`);
      return true;
    } else {
      console.warn('UI Controller: Backend returned no ingredients');
      return false;
    }
  } catch (error) {
    console.error('UI Controller Error [parseIngredientsUI]:', error);
    return false;
  }
}

/**
 * FUNCTION: Search YouTube for recipes
 * 
 * UI Flow:
 *   1. Validate search query
 *   2. Show loading state
 *   3. Call apiClient.searchYouTube()
 *   4. Render search results
 *   5. Render pagination
 *   6. Hide loading state
 * 
 * @param {string} pageToken - Optional pagination token
 * @global
 */
async function searchYouTubeUI(pageToken = '') {
  // === INPUT VALIDATION ===
  const query = document.getElementById('searchQuery')?.value || '';
  const category = document.getElementById('recipeCategory')?.value || '';

  if (!isValidSearchQuery(query)) {
    showError('Please enter a search term.');
    return;
  }

  // === LOADING STATE ===
  showLoadingState();

  try {
    // === API CALL ===
    console.log('UI Controller: Searching YouTube', { query, category });
    const response = await apiClient.searchYouTube(query, category, pageToken);

    // === ERROR CHECKING ===
    if (!response.success) {
      showError('YouTube search failed. Please try again.');
      renderSearchResults([]);
      renderPaginationButtons(false, false, '', '');
      return;
    }

    const results = response.results || [];
    const hasNext = !!response.next_page_token;
    const hasPrev = !!response.prev_page_token;

    // === RENDER RESULTS ===
    renderSearchResults(results);
    renderPaginationButtons(hasPrev, hasNext, response.prev_page_token, response.next_page_token);

    console.log(`UI Controller: Found ${results.length} results`);
  } catch (error) {
    console.error('UI Controller Error [searchYouTubeUI]:', error);
    showError(`Search error:\n${error.message}`);
    renderSearchResults([]);
    renderPaginationButtons(false, false, '', '');
  } finally {
    hideLoadingState();
  }
}

/**
 * FUNCTION: Use a video from search results
 * 
 * Sets the video URL in the input field and fetches ingredients.
 * 
 * @param {string} videoUrl - Full YouTube video URL
 * @global
 */
function useVideoFromSearch(videoUrl) {
  const input = getElement('youtubeLink');
  if (!input) return;

  // === SET VIDEO URL ===
  input.value = videoUrl;

  // === SWITCH TAB ===
  const tabs = document.querySelectorAll('.search-tab');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => tab.classList.remove('active'));
  contents.forEach(content => content.classList.remove('active'));

  const directLinkTab = document.querySelector('[data-tab="direct-link"]');
  const directLinkContent = getElement('direct-link');

  if (directLinkTab) directLinkTab.classList.add('active');
  if (directLinkContent) directLinkContent.classList.add('active');

  // === CLEAR PREVIOUS DATA ===
  const thumbnailContainer = getElement('thumbnailContainer');
  const ingredientsList = getElement('ingredientsList');
  if (thumbnailContainer) thumbnailContainer.innerHTML = '';
  if (ingredientsList) ingredientsList.innerHTML = '';

  // === FETCH INGREDIENTS ===
  fetchIngredients();
}

/**
 * FUNCTION: Extract ingredients from YouTube audio
 * 
 * Uses speech-to-text to extract ingredients when description unavailable.
 * 
 * UI Flow:
 *   1. Validate YouTube URL input
 *   2. Show loading state
 *   3. Call apiClient.extractAudioIngredients()
 *   4. Parse & render ingredients
 *   5. Hide loading state
 * 
 * Error Handling: Graceful - shows user-friendly messages
 * 
 * @global
 */
async function extractAudioIngredients(optionalUrl = null) {
  // === INPUT VALIDATION ===
  let youtubeLink = '';
  if (typeof optionalUrl === 'string' && optionalUrl.trim().length > 0) {
    youtubeLink = optionalUrl;
  } else {
    youtubeLink = document.getElementById('youtubeLink')?.value || '';
  }

  if (!isValidYouTubeUrl(youtubeLink)) {
    showError('Please enter a valid YouTube Video URL.\n\nExamples:\n• youtube.com/watch?v=...\n• youtu.be/...');
    return;
  }

  // === LOADING STATE ===
  showLoadingState();

  try {
    // === API CALL ===
    console.log('UI Controller: Extracting ingredients from audio');
    const response = await apiClient.extractAudioIngredients(youtubeLink.trim());

    // === ERROR CHECKING ===
    if (!response.success) {
      showError('Could not extract audio ingredients. Try fetching from description instead.');
      return;
    }

    // === PARSE & RENDER INGREDIENTS ===
    if (response.ingredients && response.ingredients.length > 0) {
      console.log('UI Controller: Rendering ingredients from audio extraction');
      renderIngredientsList(response.ingredients);
      populateAvailableIngredientsDropdown(response.ingredients);
      showSuccess('Ingredients extracted from audio successfully!');
    } else {
      console.warn('UI Controller: No ingredients found in audio');
      renderIngredientsList([]);
      showError('No ingredients found in the audio. Try fetching from the description.');
    }
  } catch (error) {
    console.error('UI Controller Error [extractAudioIngredients]:', error);
    showError(`Error extracting from audio:\n${error.message}`);
  } finally {
    hideLoadingState();
  }
}

/**
 * FUNCTION: Scale recipe ingredients
 * 
 * Takes current ingredients and scaling value, calls backend to scale.
 * 
 * @global
 */
window.scaleRecipe = async function () {
  const valueEl = document.getElementById("scaleValue") || document.getElementById("scalingValue");
  const typeEl = document.getElementById("scaleType") || document.getElementById("scalingOption");

  const value = valueEl ? Number(valueEl.value) : 1;
  const type = typeEl ? typeEl.value : "servings";

  if (!window.currentIngredients || window.currentIngredients.length === 0) {
    showError("No ingredients to scale. Please fetch a recipe first.");
    return;
  }

  try {
    showLoadingState();

    const response = await apiClient.scaleRecipe({
      ingredients: window.currentIngredients || [],
      value: value,
      type: type
    });

    if (response && response.ingredients) {
      console.log('UI Controller: Raw scale response:', JSON.stringify(response.ingredients.slice(0, 3)));

      // Detect & fix malformed backend response:
      // Backend bug returns {quantity: scaleFactor, unit: originalQty, name: "originalUnit originalName"}
      // instead of {quantity: scaledQty, unit: originalUnit, name: originalName}
      const scaledIngredients = response.ingredients.map(ing => {
        let qty = ing.quantity;
        let unit = ing.unit || '';
        let name = ing.name || '';

        // Heuristic: if quantity equals the scale value AND unit looks like a number,
        // the backend shifted fields — reconstruct by multiplying original qty by scale
        const unitAsNum = parseFloat(unit);
        if (!isNaN(unitAsNum) && Math.abs(qty - value) < 0.001) {
          // unit field actually holds the original quantity, name starts with original unit
          const originalQty = unitAsNum;
          // Extract the real unit from the start of the name field
          const nameMatch = name.match(/^(\S+)\s+(.*)$/);
          if (nameMatch) {
            unit = nameMatch[1];
            name = nameMatch[2];
          } else {
            unit = '';
          }
          qty = originalQty * value;
        }

        // Format quantity nicely (avoid ugly floats like 2.0000001)
        const formattedQty = Number.isInteger(qty)
          ? qty
          : parseFloat(qty.toFixed(4).replace(/\.?0+$/, ''));

        const isWhole = unit.trim().toLowerCase() === 'whole';
        const displayUnit = isWhole ? '' : unit;
        return [formattedQty, displayUnit, name].filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
      });

      console.log('UI Controller: Corrected ingredients:', scaledIngredients.slice(0, 3));

      // Store as JSON array of strings for script-new.js
      sessionStorage.setItem('scaledIngredients', JSON.stringify(scaledIngredients));
      sessionStorage.setItem('scaleFactor', value);
      sessionStorage.setItem('scaleType', type);

      if (!sessionStorage.getItem('recipeName')) {
        sessionStorage.setItem('recipeName', 'Scaled Recipe');
      }

      window.location.href = 'scaled.html';
    } else {
      showError("Scaling failed: no ingredients returned.");
    }

  } catch (error) {
    console.error(error);
    showError("Scaling failed: " + error.message);
  }

  hideLoadingState();
};

/**
 * FUNCTION: Update scaling options display
 * 
 * Shows/hides different scaling input fields based on user selection.
 * Pure UI logic - no API calls.
 * 
 * @global
 */
function updateScalingOptions() {
  const scalingOption = document.getElementById('scalingOption')?.value || 'servings';

  // Hide all scaling methods
  const methods = document.querySelectorAll('.scaling-method');
  methods.forEach(method => {
    method.style.display = 'none';
  });

  // Show the selected one
  switch (scalingOption) {
    case 'servings':
      const standardEl = getElement('standard-scaling');
      if (standardEl) standardEl.style.display = 'block';
      break;

    case 'available':
      const availableEl = getElement('available-scaling');
      if (availableEl) availableEl.style.display = 'block';
      break;

    case 'custom':
      const customEl = getElement('custom-scaling');
      if (customEl) customEl.style.display = 'block';
      break;

    default:
      const defaultEl = getElement('standard-scaling');
      if (defaultEl) defaultEl.style.display = 'block';
  }
}

/**
 * FUNCTION: Load saved recipes
 * 
 * Retrieves recipes from localStorage and renders them.
 * Pure frontend - no API calls.
 * 
 * @global
 */
function loadSavedRecipes() {
  console.log('UI Controller: Loading saved recipes from localStorage');

  const container = getElement('saved-recipes');
  const list = getElement('saved-recipes-list');

  if (!container || !list) return;

  // === GET DATA FROM STORAGE ===
  const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];

  if (savedRecipes.length === 0) {
    container.style.display = 'none';
    return;
  }

  container.style.display = 'block';
  list.innerHTML = '';

  // === RENDER RECIPES ===
  savedRecipes.forEach(recipe => {
    const item = document.createElement('div');
    item.className = 'saved-recipe-item';
    item.innerHTML = `
      <h3>${escapeHtml(recipe.name)}</h3>
      <p>${recipe.ingredients?.length || 0} ingredients</p>
      <div class="saved-recipe-actions">
        <button onclick="loadRecipeUI('${escapeHtml(recipe.id)}')">
          <i class="fas fa-eye"></i>
        </button>
        <button onclick="deleteRecipeUI('${escapeHtml(recipe.id)}')">
          <i class="fas fa-trash"></i>
        </button>
      </div>
    `;
    list.appendChild(item);
  });
}

/**
 * FUNCTION: Load a specific saved recipe
 * 
 * @param {string} recipeId - ID of the recipe to load
 * @global
 */
function loadRecipeUI(recipeId) {
  const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  const recipe = savedRecipes.find(r => r.id === recipeId);

  if (!recipe) {
    showError('Recipe not found.');
    return;
  }

  // === STORE IN SESSION ===
  sessionStorage.setItem('recipeName', recipe.name);
  sessionStorage.setItem('mainIngredient', recipe.mainIngredient);
  sessionStorage.setItem('scaledIngredients', recipe.ingredients?.join('<br>') || '');

  if (recipe.youtubeLink) {
    sessionStorage.setItem('youtubeVideoUrl', recipe.youtubeLink);
  }

  // === NAVIGATE ===
  window.location.href = 'scaled.html';
}

/**
 * FUNCTION: Delete a saved recipe
 * 
 * @param {string} recipeId - ID of the recipe to delete
 * @global
 */
function deleteRecipeUI(recipeId) {
  if (!confirm('Are you sure you want to delete this recipe?')) {
    return;
  }

  let savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  savedRecipes = savedRecipes.filter(r => r.id !== recipeId);

  localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));
  loadSavedRecipes();

  showSuccess('Recipe deleted.');
}

/**
 * PLACEHOLDER: Save recipe to localStorage
 * (Called from enter_recipe.html)
 * @global
 */
function saveRecipeUI() {
  console.warn('UI Controller: saveRecipeUI() is a placeholder');
  showError('Save recipe feature is being configured.');
  // TODO: Implement when recipe storage logic is finalized
}

// ============================================================================
// INITIALIZE UI ON PAGE LOAD
// ============================================================================

/**
 * Initialize all UI interactions when page loads
 */
function initializeUI() {
  console.log('UI Controller: Initializing...');

  // Load saved recipes if container exists
  if (getElement('saved-recipes')) {
    loadSavedRecipes();
  }

  // Setup tab switching
  const tabs = document.querySelectorAll('.search-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', function () {
      // Remove active from all tabs and contents
      document.querySelectorAll('.search-tab').forEach(t => {
        t.classList.remove('active');
      });
      document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.remove('active');
      });

      // Add active to clicked tab and corresponding content
      this.classList.add('active');
      const tabId = this.getAttribute('data-tab');
      const content = getElement(tabId);
      if (content) {
        content.classList.add('active');
      }
    });
  });

  // Setup scaling option updates
  const scalingSelect = getElement('scalingOption');
  if (scalingSelect) {
    scalingSelect.addEventListener('change', updateScalingOptions);
  }

  // Setup enter recipe manually button
  const enterRecipeBtn = getElement('enterRecipeManually');
  if (enterRecipeBtn) {
    enterRecipeBtn.addEventListener('click', () => {
      window.location.href = 'enter_recipe.html';
    });
  }

  console.log('UI Controller: Ready');
}

// ============================================================================
// AUTO-INITIALIZE ON DOM READY
// ============================================================================

// Modern approach
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeUI);
} else {
  // Page already loaded
  initializeUI();
}

// Also expose initializeUI globally in case it's needed
window.initializeUI = initializeUI;