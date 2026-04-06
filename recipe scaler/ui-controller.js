/**
 * ============================================================================
 * UI CONTROLLER / BRIDGE LAYER
 * ============================================================================
 */

// ============================================================================
// INPUT VALIDATION HELPERS
// ============================================================================

function isValidYouTubeUrl(url) {
  if (!url || typeof url !== 'string') return false;
  const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\//;
  return youtubeRegex.test(url.trim());
}

function isValidSearchQuery(query) {
  return query && typeof query === 'string' && query.trim().length > 0;
}

function isValidScalingValue(value) {
  const num = parseFloat(value);
  return !isNaN(num) && num > 0;
}

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

function showLoadingState() {
  const loadingEl = getElement('loading');
  if (loadingEl) loadingEl.style.display = 'block';
}

function hideLoadingState() {
  const loadingEl = getElement('loading');
  if (loadingEl) loadingEl.style.display = 'none';
}

// ============================================================================
// ERROR HANDLING & USER FEEDBACK
// ============================================================================

function showError(message) {
  const fullMessage = message || 'An unexpected error occurred. Please try again.';
  console.error('UI Error:', fullMessage);
  alert(fullMessage);
}

function showSuccess(message) {
  console.log('UI Success:', message);
}

// ============================================================================
// TRANSLATION STATE & DICTIONARY
// ============================================================================

let originalIngredients = [];
let translatedIngredients = [];
let sourceLanguage = "english";
let currentLanguage = "source";

const ingredientMap = {
  "tomato": "തക്കാളി",
  "onion": "സവാള",
  "green chilli": "പച്ചമുളക്",
  "chilli": "മുളക്",
  "capsicum": "കാപ്സിക്കം",
  "carrot": "കാരറ്റ്",
  "potato": "ഉരുളക്കിഴങ്ങ്",
  "ginger": "ഇഞ്ചി",
  "garlic": "വെളുത്തുള്ളി",
  "curry leaves": "കരിവേപ്പില",
  "coriander leaves": "മല്ലിയില",
  "turmeric": "മഞ്ഞൾ",
  "salt": "ഉപ്പ്",
  "sugar": "പഞ്ചസാര",
  "oil": "എണ്ണ",
  "mustard seeds": "കടുക്",
  "cumin seeds": "ജീരകം",
  "pepper": "കുരുമുളക്",
  "green pepper": "പച്ച കാപ്സിക്കം",
  "red pepper": "ചുവപ്പ് കാപ്സിക്കം",
  "cheese": "ചീസ്",
  "mozzarella": "മൊസറെല്ല",
  "butter": "വെണ്ണ",
  "milk": "പാൽ",
  "flour": "മാവ്"
};

const reverseMap = Object.fromEntries(
  Object.entries(ingredientMap).map(([k, v]) => [v, k])
);

const unitMap = {
  "cup": "കപ്പ്",
  "cups": "കപ്പ്",
  "tablespoon": "ടേബിൾസ്പൂൺ",
  "tablespoons": "ടേബിൾസ്പൂൺ",
  "tbsp": "ടേബിൾസ്പൂൺ",
  "teaspoon": "ടീസ്പൂൺ",
  "teaspoons": "ടീസ്പൂൺ",
  "tsp": "ടീസ്പൂൺ",
  "gram": "ഗ്രാം",
  "grams": "ഗ്രാം",
  "kg": "കിലോ",
  "ml": "മില്ലി",
  "liter": "ലിറ്റർ",
  "litre": "ലിറ്റർ",
  "piece": "കഷണം",
  "pieces": "കഷണങ്ങൾ",
  "slice": "സ്ലൈസ്",
  "slices": "സ്ലൈസ്"
};

const reverseUnitMap = Object.fromEntries(
  Object.entries(unitMap).map(([k, v]) => [v, k])
);

const descriptorMap = {
  "warm": "ചൂട്",
  "hot": "ചൂട്",
  "cold": "തണുപ്പ്",
  "soft": "സോഫ്റ്റ്",
  "grated": "തുരന്ന",
  "chopped": "അരിഞ്ഞ",
  "minced": "ചെറുതായി അരിഞ്ഞ",
  "fresh": "പുതിയത്",
  "large": "വലിയ",
  "small": "ചെറിയ",
  "to": "",
  "taste": "രുചിക്ക്"
};

const reverseDescriptorMap = Object.fromEntries(
  Object.entries(descriptorMap).map(([k, v]) => [v, k])
);

function isMalayalam(word) {
  return /[\u0D00-\u0D7F]/.test(word);
}

function isNumber(word) {
  return /^[0-9\/\.]+$/.test(word);
}

function transliterate(word) {
  return word
    .replace(/carrot/i, "കാരറ്റ്")
    .replace(/thyme/i, "തൈം")
    .replace(/scotch/i, "സ്കോച്ച്")
    .replace(/bacon/i, "ബേക്കൺ")
    .replace(/sausage/i, "സോസേജ്")
    .replace(/pepper/i, "പെപ്പർ")
    .replace(/cheese/i, "ചീസ്")
    .replace(/butter/i, "ബട്ടർ")
    .replace(/water/i, "വെള്ളം");
}

function processTranslation(text, selectedLang) {
  if (!text) return text;

  const isToMalayalam = selectedLang === 'malayalam';

  if (!isToMalayalam) {
    // Very basic reverse lookup for entire strings if available, or just split and return (since Malayalam to English transliteration fallback is disabled)
    let processedName = text.trim();
    let lowerName = processedName.toLowerCase();
    if (reverseMap[lowerName]) return reverseMap[lowerName];
    if (reverseUnitMap[lowerName]) return reverseUnitMap[lowerName];
    if (reverseDescriptorMap[lowerName]) return reverseDescriptorMap[lowerName];

    const words = processedName.split(" ");
    return words.map(word => {
      let clean = word.toLowerCase().replace(/[.,]/g, '');
      if (reverseMap[clean]) return reverseMap[clean];
      if (reverseUnitMap[clean]) return reverseUnitMap[clean];
      if (reverseDescriptorMap[clean]) return reverseDescriptorMap[clean];
      return word;
    }).join(" ");
  }

  // To Malayalam Strict Pipeline
  return text.split(" ").map(word => {
    let clean = word.toLowerCase().replace(/[.,]/g, '');

    if (isMalayalam(word)) return word;
    if (isNumber(word)) return word;

    if (ingredientMap[clean]) return ingredientMap[clean];
    if (unitMap[clean]) return unitMap[clean];
    if (descriptorMap[clean] !== undefined) return descriptorMap[clean] === "" ? "" : descriptorMap[clean];

    return transliterate(word);
  }).filter(Boolean).join(" ");
}

function translateIngredients() {
  const selectedLang = document.getElementById('translateLanguage')?.value || 'english';

  if ((selectedLang === 'english' && sourceLanguage === 'english') ||
    (selectedLang === 'malayalam' && sourceLanguage === 'malayalam')) {
    // User is translating to the language it's already in
    currentLanguage = 'source';
    window.currentIngredients = JSON.parse(JSON.stringify(originalIngredients));
    renderIngredientsList(window.currentIngredients, 'ingredientsList', true);
    return;
  }

  translatedIngredients = originalIngredients.map(ing => {
    let newUnit = processTranslation(ing.unit, selectedLang);
    let newName = processTranslation(ing.name, selectedLang);

    return {
      ...ing,
      unit: newUnit,
      name: newName
    };
  });

  currentLanguage = 'translated';
  window.currentIngredients = translatedIngredients;
  renderIngredientsList(window.currentIngredients, 'ingredientsList', true);
} // Optional translation end

// ============================================================================
// DOM RENDERING HELPERS - INGREDIENTS
// ============================================================================

function renderIngredientsList(ingredients, containerId = 'ingredientsList', isTranslation = false) {
  window.currentIngredients = ingredients;

  if (!isTranslation) {
    originalIngredients = JSON.parse(JSON.stringify(ingredients || []));
    const malayalamRegex = /[\u0D00-\u0D7F]/;
    const isMalayalam = originalIngredients.some(ing => malayalamRegex.test(ing.name || ''));
    sourceLanguage = isMalayalam ? "malayalam" : "english";
    currentLanguage = "source";

    const translateSection = document.getElementById('translateSection');
    if (translateSection) {
      translateSection.style.display = (ingredients && ingredients.length > 0) ? 'block' : 'none';
      const translateDropdown = document.getElementById('translateLanguage');
      if (translateDropdown) {
        translateDropdown.value = sourceLanguage === 'english' ? 'malayalam' : 'english';
      }
    }
  }

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

    const isWhole = unit.trim().toLowerCase() === 'whole';
    let displayText;
    if (isWhole) {
      displayText = quantity === 1 ? name.trim() : `${quantity} ${name}`.trim();
    } else {
      displayText = `${quantity} ${unit} ${name}`.replace(/\s+/g, ' ').trim();
    }

    const div = document.createElement('div');
    div.className = 'ingredient-card';
    div.style.cssText = 'background:white;padding:15px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.05);margin-bottom:15px;max-width:80%;margin-left:auto;margin-right:auto;display:flex;flex-direction:column;';

    const row = document.createElement('div');
    row.style.cssText = 'display:flex;justify-content:space-between;align-items:center;gap:15px;width:100%;flex-wrap:wrap;';

    row.innerHTML = `
      <input 
        type="text" 
        value="${displayText}" 
        readonly 
        class="ingredient-name"
        data-ingredient-index="${index}"
        style="flex-grow:1;margin:0;min-width:200px;"
      >
      <button class="substitute-btn" style="background-color:#F2D479;color:#333;margin:0;padding:10px 15px;border-radius:6px;font-weight:600;white-space:nowrap;">Find Substitute</button>
    `;

    const dropdown = document.createElement('div');
    dropdown.className = 'substitute-dropdown';
    dropdown.style.cssText = 'display:none;background-color:#f9f9f9;border:1px solid #e0e0e0;border-radius:8px;padding:15px;margin-top:15px;text-align:left;';

    const btn = row.querySelector('.substitute-btn');
    btn.onclick = (e) => {
      e.stopPropagation();
      handleIngredientClick(ingredient, dropdown, btn);
    };

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

  if (dropdown.hasAttribute('data-fetched')) return;

  dropdown.innerHTML = '<p style="margin:0;color:#666;">Finding substitutes <i class="fas fa-spinner fa-spin"></i></p>';

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
    dropdown.innerHTML = '<p style="color:red;margin:0;">Failed to fetch substitutions.</p>';
  }
}

/**
 * FIX #2: The API returns `data.substitutes` (not `data.substitutions`).
 * Each substitute has { name, ratio, note } fields per the Substitute schema.
 */
function renderSubstitutions(data, container) {
  if (!container) return;
  container.innerHTML = '';

  // Support both field names for safety
  const subs = (data && (data.substitutes || data.substitutions)) || [];

  if (!subs || subs.length === 0) {
    container.innerHTML = '<p style="margin:0;color:#666;">No substitutions found.</p>';
    return;
  }

  const heading = document.createElement('h4');
  heading.innerText = 'Substitutions';
  heading.style.cssText = 'margin-top:0;margin-bottom:10px;color:#5a8c5a;';
  container.appendChild(heading);

  subs.forEach(sub => {
    const div = document.createElement('div');
    div.style.cssText = 'border-left:3px solid #E63946;padding-left:10px;margin-bottom:10px;';

    // API returns: { name, ratio, note }
    const name = sub.name || sub.substitute || 'Alternative';
    const ratio = sub.ratio || '';
    const note = sub.note || sub.reason || '';

    div.innerHTML = `
      <strong style="display:block;color:#333;">${name}</strong>
      ${ratio ? `<span style="font-size:0.9rem;color:#666;display:block;">Ratio: ${ratio}</span>` : ''}
      ${note ? `<small style="color:#888;display:block;">${note}</small>` : ''}
    `;

    container.appendChild(div);
  });
}

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

function renderVideoThumbnail(thumbnailUrl, videoTitle, youtubeUrl, containerId = 'thumbnailContainer') {
  const container = getElement(containerId);
  if (!container) return;

  container.innerHTML = '';

  const img = document.createElement('img');
  img.src = thumbnailUrl;
  img.alt = 'YouTube Thumbnail';
  img.loading = 'eager';
  img.onerror = () => {
    img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%23ccc" width="320" height="180"/%3E%3C/svg%3E';
  };
  container.appendChild(img);

  const title = document.createElement('p');
  title.innerText = videoTitle || 'Untitled Video';
  title.style.fontWeight = 'bold';
  title.style.marginTop = '10px';
  container.appendChild(title);

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

function renderSearchResults(results, containerId = 'searchResults') {
  const container = getElement(containerId);
  if (!container) return;

  container.innerHTML = '';

  if (!results || results.length === 0) {
    container.innerHTML = '<p style="color:#666;padding:20px;">No results found. Try a different search term.</p>';
    return;
  }

  const grid = document.createElement('div');
  grid.className = 'search-results';

  results.forEach(result => {
    const card = document.createElement('div');
    card.className = 'search-result-item';

    const publishedDate = new Date(result.published_date);
    const formattedDate = publishedDate.toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric'
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

function formatViewCount(viewCount) {
  const count = parseInt(viewCount, 10);
  if (isNaN(count)) return '0';
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return count.toString();
}

function escapeHtml(text) {
  if (!text) return '';
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// ============================================================================
// GLOBAL UI FUNCTIONS
// ============================================================================

async function fetchIngredients() {
  const youtubeLink = document.getElementById('youtubeLink')?.value || '';

  if (!isValidYouTubeUrl(youtubeLink)) {
    showError('Please enter a valid YouTube Video URL.\n\nExamples:\n• youtube.com/watch?v=...\n• youtu.be/...');
    return;
  }

  showLoadingState();

  try {
    const response = await apiClient.extractYouTubeMetadata(youtubeLink.trim());

    if (!response.success || !response.metadata) {
      showError('Could not extract video information. Try another video.');
      return;
    }

    const metadata = response.metadata;

    sessionStorage.setItem('recipeName', metadata.title || 'Scaled Recipe');
    sessionStorage.setItem('mainIngredient', metadata.channel || '');
    sessionStorage.setItem('youtubeVideoUrl', youtubeLink.trim());

    renderVideoThumbnail(metadata.thumbnail_url, metadata.title, youtubeLink);

    let ingredientsFound = false;
    const description = metadata.description || '';
    const isLikelyIngredientList = description.includes('\n') && description.length < 3000;
    if (description && isLikelyIngredientList) {
      ingredientsFound = await parseIngredientsUI(description);
    }

    if (!ingredientsFound) {
      const loadingEl = getElement('loading');
      const originalLoadingHtml = loadingEl ? loadingEl.innerHTML : '';
      if (loadingEl) {
        loadingEl.innerHTML = `
          <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px;">
            <div style="margin:0 auto 15px;width:40px;height:40px;border:4px solid #f3f3f3;border-top:4px solid #E63946;border-radius:50%;animation:spin 1s linear infinite;"></div>
            <p style="margin-top:15px;color:#2B2D42;font-size:15px;text-align:center;font-weight:500;">No ingredients in description.<br>Extracting from audio...</p>
            <p style="margin-top:5px;color:#666;font-size:13px;text-align:center;">(This may take up to a minute)</p>
          </div>
        `;
      }

      await extractAudioIngredients(youtubeLink.trim());

      if (loadingEl) loadingEl.innerHTML = originalLoadingHtml;
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

async function parseIngredientsUI(text) {
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    console.warn('UI Controller: No text to parse');
    return false;
  }

  try {
    const response = await apiClient.parseIngredients(text);

    if (response.success && response.ingredients) {
      renderIngredientsList(response.ingredients);
      populateAvailableIngredientsDropdown(response.ingredients);
      return true;
    }
    return false;
  } catch (error) {
    console.error('UI Controller Error [parseIngredientsUI]:', error);
    return false;
  }
}

async function searchYouTubeUI(pageToken = '') {
  const query = document.getElementById('searchQuery')?.value || '';
  const category = document.getElementById('recipeCategory')?.value || '';

  if (!isValidSearchQuery(query)) {
    showError('Please enter a search term.');
    return;
  }

  showLoadingState();

  try {
    const response = await apiClient.searchYouTube(query, category, pageToken);

    if (!response.success) {
      showError('YouTube search failed. Please try again.');
      renderSearchResults([]);
      renderPaginationButtons(false, false, '', '');
      return;
    }

    const results = response.results || [];
    renderSearchResults(results);
    renderPaginationButtons(
      !!response.prev_page_token, !!response.next_page_token,
      response.prev_page_token, response.next_page_token
    );
  } catch (error) {
    console.error('UI Controller Error [searchYouTubeUI]:', error);
    showError(`Search error:\n${error.message}`);
    renderSearchResults([]);
    renderPaginationButtons(false, false, '', '');
  } finally {
    hideLoadingState();
  }
}

function useVideoFromSearch(videoUrl) {
  const input = getElement('youtubeLink');
  if (!input) return;

  input.value = videoUrl;

  document.querySelectorAll('.search-tab').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

  const directLinkTab = document.querySelector('[data-tab="direct-link"]');
  const directLinkContent = getElement('direct-link');

  if (directLinkTab) directLinkTab.classList.add('active');
  if (directLinkContent) directLinkContent.classList.add('active');

  const thumbnailContainer = getElement('thumbnailContainer');
  const ingredientsList = getElement('ingredientsList');
  if (thumbnailContainer) thumbnailContainer.innerHTML = '';
  if (ingredientsList) ingredientsList.innerHTML = '';

  fetchIngredients();
}

async function extractAudioIngredients(optionalUrl = null) {
  let youtubeLink = '';
  if (typeof optionalUrl === 'string' && optionalUrl.trim().length > 0) {
    youtubeLink = optionalUrl;
  } else {
    youtubeLink = document.getElementById('youtubeLink')?.value || '';
  }

  if (!isValidYouTubeUrl(youtubeLink)) {
    showError('Please enter a valid YouTube Video URL.');
    return;
  }

  showLoadingState();

  try {
    const response = await apiClient.extractAudioIngredients(youtubeLink.trim());

    if (!response.success) {
      showError('Could not extract audio ingredients. Try fetching from description instead.');
      return;
    }

    if (response.ingredients && response.ingredients.length > 0) {
      renderIngredientsList(response.ingredients);
      populateAvailableIngredientsDropdown(response.ingredients);
      showSuccess('Ingredients extracted from audio successfully!');
    } else {
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

// ============================================================================
// FIX #1: scaleRecipe — properly format scaled ingredient strings
// ============================================================================
/**
 * The backend returns ingredients as objects: { name, quantity, unit, ... }
 * We must format them as "quantity unit name" strings for scaled.html display.
 * The old heuristic that detected a "malformed response" was itself causing
 * the bug by prepending the scale factor to every ingredient string.
 */
window.scaleRecipe = async function () {
  const valueEl = document.getElementById('scaleValue') || document.getElementById('scalingValue');
  const typeEl = document.getElementById('scaleType') || document.getElementById('scalingOption');

  const value = valueEl ? Number(valueEl.value) : 1;
  const type = typeEl ? typeEl.value : 'servings';

  if (!window.currentIngredients || window.currentIngredients.length === 0) {
    showError('No ingredients to scale. Please fetch a recipe first.');
    return;
  }

  if (!value || value <= 0) {
    showError('Please enter a valid scaling value greater than 0.');
    return;
  }

  try {
    showLoadingState();

    const response = await apiClient.scaleRecipe({
      ingredients: window.currentIngredients,
      value: value,
      type: type
    });

    if (response && response.ingredients) {
      console.log('[scaleRecipe] raw backend response ingredients:', JSON.stringify(response.ingredients.slice(0, 4)));

      // Each item is { name, quantity, unit, ... } — format directly.
      // Each item might have the original quantity inside `ing.name` and the scale factor in `ing.quantity`
      const scaledIngredients = response.ingredients.map(ing => {
        const scaleFactor = ing.quantity || 1;
        const originalName = (ing.name || '').trim();

        // Extract numeric quantity from the beginning of the name
        const regex = /^((?:\d+\s+)?\d+\/\d+|\d+(?:\.\d+)?)\s*(.*)$/;
        const match = originalName.match(regex);

        if (match) {
          const qtyStr = match[1].trim();
          const restOfIngredient = match[2].trim();

          // Convert fractions to decimals
          let numericQty = 0;
          if (qtyStr.includes(' ') && qtyStr.includes('/')) {
            const parts = qtyStr.split(' ');
            const whole = parseFloat(parts[0]);
            const fracParts = parts[1].split('/');
            numericQty = whole + (parseFloat(fracParts[0]) / parseFloat(fracParts[1]));
          } else if (qtyStr.includes('/')) {
            const fracParts = qtyStr.split('/');
            numericQty = parseFloat(fracParts[0]) / parseFloat(fracParts[1]);
          } else {
            numericQty = parseFloat(qtyStr);
          }

          // Multiply original quantity by scale factor
          const scaledQty = numericQty * scaleFactor;

          // Format back into a readable quantity using existing helper
          const rounded = parseFloat(scaledQty.toFixed(4).replace(/\.?0+$/, ''));
          const formattedQty = formatNiceQuantity(rounded);

          // Rebuild ingredient string
          return `${formattedQty} ${restOfIngredient}`;
        }

        // Output raw ingredient if no numbers found
        return originalName;
      });

      console.log('[scaleRecipe] formatted strings going to sessionStorage:', scaledIngredients.slice(0, 4));
      sessionStorage.setItem('scaledIngredients', JSON.stringify(scaledIngredients));
      sessionStorage.setItem('scaleFactor', value);
      sessionStorage.setItem('scaleType', type);

      if (!sessionStorage.getItem('recipeName')) {
        sessionStorage.setItem('recipeName', 'Scaled Recipe');
      }

      window.location.href = 'scaled.html';
    } else {
      showError('Scaling failed: no ingredients returned.');
    }
  } catch (error) {
    console.error(error);
    showError('Scaling failed: ' + error.message);
  } finally {
    hideLoadingState();
  }
};

/**
 * Format a decimal number as a nice cooking quantity string.
 * Examples: 0.5 → "½", 1.25 → "1 ¼", 8 → "8"
 */
function formatNiceQuantity(qty) {
  if (Number.isInteger(qty)) return qty.toString();

  const whole = Math.floor(qty);
  const frac = qty - whole;

  const FRACTIONS = [
    [0.125, '⅛'],
    [0.167, '⅙'],
    [0.25, '¼'],
    [0.333, '⅓'],
    [0.5, '½'],
    [0.667, '⅔'],
    [0.75, '¾'],
  ];

  for (const [val, sym] of FRACTIONS) {
    if (Math.abs(frac - val) < 0.04) {
      return whole > 0 ? `${whole} ${sym}` : sym;
    }
  }

  // Fallback: up to 2 decimal places, strip trailing zeros
  return parseFloat(qty.toFixed(2)).toString();
}

function updateScalingOptions() {
  const scalingOption = document.getElementById('scalingOption')?.value || 'servings';

  document.querySelectorAll('.scaling-method').forEach(method => {
    method.style.display = 'none';
  });

  switch (scalingOption) {
    case 'servings':
    case 'quantity': {
      const el = getElement('standard-scaling');
      if (el) el.style.display = 'block';
      break;
    }
    case 'available': {
      const el = getElement('available-scaling');
      if (el) el.style.display = 'block';
      break;
    }
    case 'custom': {
      const el = getElement('custom-scaling');
      if (el) el.style.display = 'block';
      break;
    }
    default: {
      const el = getElement('standard-scaling');
      if (el) el.style.display = 'block';
    }
  }
}

function loadSavedRecipes() {
  const container = getElement('saved-recipes');
  const list = getElement('saved-recipes-list');

  if (!container || !list) return;

  const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];

  if (savedRecipes.length === 0) {
    container.style.display = 'none';
    return;
  }

  container.style.display = 'block';
  list.innerHTML = '';

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

function loadRecipeUI(recipeId) {
  const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  const recipe = savedRecipes.find(r => r.id === recipeId);

  if (!recipe) {
    showError('Recipe not found.');
    return;
  }

  sessionStorage.setItem('recipeName', recipe.name);
  sessionStorage.setItem('mainIngredient', recipe.mainIngredient);
  sessionStorage.setItem('scaledIngredients', recipe.ingredients?.join('<br>') || '');

  if (recipe.youtubeLink) {
    sessionStorage.setItem('youtubeVideoUrl', recipe.youtubeLink);
  }

  window.location.href = 'scaled.html';
}

function deleteRecipeUI(recipeId) {
  if (!confirm('Are you sure you want to delete this recipe?')) return;

  let savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  savedRecipes = savedRecipes.filter(r => r.id !== recipeId);
  localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));
  loadSavedRecipes();
  showSuccess('Recipe deleted.');
}

function saveRecipeUI() {
  console.warn('UI Controller: saveRecipeUI() is a placeholder');
  showError('Save recipe feature is being configured.');
}

// ============================================================================
// INITIALIZE UI ON PAGE LOAD
// ============================================================================

function initializeUI() {
  console.log('UI Controller: Initializing...');

  if (getElement('saved-recipes')) loadSavedRecipes();

  const tabs = document.querySelectorAll('.search-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', function () {
      document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      this.classList.add('active');
      const tabId = this.getAttribute('data-tab');
      const content = getElement(tabId);
      if (content) content.classList.add('active');
    });
  });

  const scalingSelect = getElement('scalingOption');
  if (scalingSelect) scalingSelect.addEventListener('change', updateScalingOptions);

  const enterRecipeBtn = getElement('enterRecipeManually');
  if (enterRecipeBtn) {
    enterRecipeBtn.addEventListener('click', () => {
      window.location.href = 'enter_recipe.html';
    });
  }

  const translateBtn = getElement('translateBtn');
  if (translateBtn) {
    translateBtn.addEventListener('click', translateIngredients);
  }

  console.log('UI Controller: Ready');
}

document.addEventListener('DOMContentLoaded', initializeUI);

window.initializeUI = initializeUI;
