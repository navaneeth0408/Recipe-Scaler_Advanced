/**
 * ============================================================================
 * UI CONTROLLER / BRIDGE LAYER  (patched)
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
  if (loadingEl) {
    loadingEl.style.display = 'block';
  }
}

function hideLoadingState() {
  const loadingEl = getElement('loading');
  if (loadingEl) {
    loadingEl.style.display = 'none';
  }
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

function setTranslateSectionVisibility(show) {
  const section = getElement('translateSection');
  if (!section) return;
  section.style.display = show ? 'block' : 'none';
}

function getDisplayLinesFromIngredients(ingredients) {
  return (ingredients || []).map(ing => buildIngredientDisplayText(ing));
}

function splitLeadingQuantity(line) {
  const text = String(line || '').trim();
  if (!text) return { quantity: '', remainder: '' };

  // Capture only the leading numeric quantity and keep it unchanged.
  // Supports: 1, 2.5, 3/4, 1 1/2, ½, ¼, ¾, etc.
  const quantityRegex = /^(\d+(?:\.\d+)?(?:\s+\d+\/\d+)?|\d+\/\d+|[¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])(?:\s+|$)(.*)$/u;
  const match = text.match(quantityRegex);

  if (match) {
    return {
      quantity: match[1].trim(),
      remainder: (match[2] || '').trim(),
    };
  }

  return { quantity: '', remainder: text };
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
  "green chillies": "പച്ചമുളക്",
  "chilli": "മുളക്",
  "capsicum": "കാപ്സിക്കം",
  "carrot": "കാരറ്റ്",
  "potato": "ഉരുളക്കിഴങ്ങ്",
  "ginger": "ഇഞ്ചി",
  "garlic": "വെളുത്തുള്ളി",
  "curry leaves": "കരിവേപ്പില",
  "coriander leaves": "മല്ലിയില",
  "coriander": "മല്ലി",
  "turmeric": "മഞ്ഞൾ",
  "salt": "ഉപ്പ്",
  "sugar": "പഞ്ചസാര",
  "oil": "എണ്ണ",
  "ghee": "നെയ്യ്",
  "mustard seeds": "കടുക്",
  "cumin seeds": "ജീരകം",
  "cumin": "ജീരകം",
  "pepper": "കുരുമുളക്",
  "green pepper": "പച്ച കാപ്സിക്കം",
  "red pepper": "ചുവപ്പ് കാപ്സിക്കം",
  "cheese": "ചീസ്",
  "mozzarella": "മൊസറെല്ല",
  "butter": "വെണ്ണ",
  "milk": "പാൽ",
  "curd": "തൈര്",
  "flour": "മാവ്",
  "rice": "അരി",
  "chicken": "ചിക്കൻ",
  "tomatoes": "തക്കാളി",
  "potatoes": "ഉരുളക്കിഴങ്ങ്",
  "onions": "സവാള",
  "carrots": "കാരറ്റ്",
  "green bell pepper": "പച്ച കാപ്സിക്കം",
  "red bell pepper": "ചുവപ്പ് കാപ്സിക്കം",
  "egg": "മുട്ട",
  "eggs": "മുട്ട",
  "curry powder": "കറി പൗഡർ",
  "seasoning cube": "സീസണിംഗ് ക്യൂബ്",
  "all purpose": "ഓൾ പർപ്പസ്",
  "instant": "ഇൻസ്റ്റന്റ്",
  "yeast": "യീസ്റ്റ്",
  "breast": "ബ്രെസ്റ്റ്",
  "breasts": "ബ്രെസ്റ്റ്",
  "mozarella": "മൊസറെല്ല",
  "sausage": "സോസേജ്",
  "bacon": "ബേക്കൺ",
  "scotch bonnet": "സ്കോച്ച് ബോണറ്റ്",
  "bonnet": "ബോണറ്റ്",
  "peppers": "പെപ്പേഴ്സ്",
  "rose water": "റോസ് വാട്ടർ",
  "rose": "റോസ്",
  "red chillies": "വറ്റൽമുളക്",
  "red chilli": "വറ്റൽമുളക്",
  "red chilli powder": "വറ്റൽ മുളകുപൊടി",
  "chilli powder": "മുളകുപൊടി",
  "cashew nuts": "കശുവണ്ടി",
  "cashews": "കശുവണ്ടി",
  "cashew": "കശുവണ്ടി",
  "cashew nut": "കശുവണ്ടി",
  "garam masala": "ഗരം മസാല",
  "kasuri methi": "കസ്തൂരി മേത്തി",
  "kashmiri red chilli powder": "കാശ്മീരി മുളകുപൊടി",
  "kashmiri chilli powder": "കാശ്മീരി മുളകുപൊടി",
  "kashmiri red chilli": "കാശ്മീരി വറ്റൽമുളക്",
  "kashmiri chilli": "കാശ്മീരി മുളക്",
  "tamarind": "പുളി",
  "coconut": "തേങ്ങ",
  "fish": "മീൻ",
  "yogurt": "തൈര്",
  "cream": "ക്രീം",
  "paneer": "പനീർ",
  "jaggery": "ശർക്കര",
  "lemon": "നാരങ്ങ",
  "cloves": "ഗ്രാമ്പൂ",
  "cardamom": "ഏലക്ക",
  "paste": "പേസ്റ്റ്",
  "ginger garlic paste": "ഇഞ്ചി വെളുത്തുള്ളി പേസ്റ്റ്",
  "lemon juice": "നാരങ്ങാനീര്",
  "black pepper": "കുരുമുളക്",
  "vinegar": "വിനാഗിരി",
  "fenugreek": "ഉലുവ",
  "fennel": "പെരുംജീരകം",
  "mint": "പുതിന"
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
  "kilogram": "കിലോ",
  "kilograms": "കിലോ",
  "kg": "കിലോ",
  "milliliter": "മില്ലി",
  "milliliters": "മില്ലി",
  "ml": "മില്ലി",
  "liter": "ലിറ്റർ",
  "liters": "ലിറ്റർ",
  "litre": "ലിറ്റർ",
  "piece": "കഷണം",
  "pieces": "കഷണങ്ങൾ",
  "slice": "സ്ലൈസ്",
  "slices": "സ്ലൈസ്",
  "table spoon": "ടേബിൾസ്പൂൺ",
  "table spoons": "ടേബിൾസ്പൂൺ",
  "sprinkle of": "കുറച്ച്",
  "sprinkle": "കുറച്ച്",
  "handful": "ഒരു പിടി",
  "pinch": "ഒരു നുള്ള്",
  "bunch": "ഒരു കെട്ട്"
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
  "fresh": "ഫ്രഷ്",
  "large": "വലിയ",
  "small": "ചെറിയ",
  "to": "",
  "taste": "രുചിക്ക്",
  "bulb": "",
  "powder": "പൊടി",
  "kashmiri": "കാശ്മീരി",
  "kashmiri red": "കാശ്മീരി",
  "red": "ചുവന്ന"
};

const reverseDescriptorMap = Object.fromEntries(
  Object.entries(descriptorMap).map(([k, v]) => [v, k])
);

function isMalayalam(word) {
  return /[\u0D00-\u0D7F]/.test(word);
}

function isNumber(word) {
  return /^[0-9\/\.\-]+$/.test(word);
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

  let processedText = text.trim();
  const allMaps = { ...descriptorMap, ...unitMap, ...ingredientMap };
  const sortedKeys = Object.keys(allMaps).sort((a, b) => b.length - a.length);
  sortedKeys.forEach(key => {
    if (key.includes(' ')) {
      const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`\\b${escapedKey}\\b`, 'gi');
      processedText = processedText.replace(regex, allMaps[key]);
    }
  });

  return processedText.split(" ").map(word => {
    let clean = word.toLowerCase().replace(/[.,]/g, '');
    if (isMalayalam(word)) return word;
    if (isNumber(word)) return word;
    if (ingredientMap[clean]) return ingredientMap[clean];
    if (unitMap[clean]) return unitMap[clean];
    if (descriptorMap[clean] !== undefined) return descriptorMap[clean] === "" ? "" : descriptorMap[clean];
    return transliterate(word);
  }).filter(Boolean).join(" ");
}

function translateIngredientsUI() {
  const selectedLang = document.getElementById('translateLanguage')?.value || 'english';

  if ((selectedLang === 'english' && sourceLanguage === 'english') ||
    (selectedLang === 'malayalam' && sourceLanguage === 'malayalam')) {
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
}

// ============================================================================
// DOM RENDERING HELPERS - INGREDIENTS
// ============================================================================

/**
 * Build a human-readable display string for one ingredient.
 * e.g.  { name:"salt", quantity:1, unit:"tsp" }  →  "1 tsp salt"
 *        { name:"egg",  quantity:2, unit:"whole" } →  "2 egg"
 */
function buildIngredientDisplayText(ingredient) {
  const qty = (ingredient.quantity != null) ? ingredient.quantity : 1;
  const unit = (ingredient.unit || '').trim();
  const name = (ingredient.name || '').trim();

  const isWhole = unit.toLowerCase() === 'whole' || unit === '';

  let parts = [];
  // Always include quantity
  parts.push(formatQtyDisplay(qty));
  // Include unit only if it's a real measurement
  if (!isWhole) parts.push(unit);
  parts.push(name);

  return parts.filter(Boolean).join(' ');
}

/**
 * Format a numeric quantity nicely (avoid "2.0", prefer "2"; keep "0.5").
 */
function formatQtyDisplay(qty) {
  const n = parseFloat(qty);
  if (isNaN(n)) return '1';
  if (Number.isInteger(n)) return String(n);

  const whole = Math.floor(n);
  const rem = parseFloat((n - whole).toFixed(3));

  // Common culinary fractions
  const fractionMap = {
    0.25: '1/4',
    0.5: '1/2',
    0.75: '3/4',
    0.333: '1/3',
    0.667: '2/3',
    0.125: '1/8',
    0.375: '3/8',
    0.625: '5/8',
    0.875: '7/8',
    0.2: '1/5',
    0.4: '2/5',
    0.6: '3/5',
    0.8: '4/5'
  };

  const frac = fractionMap[rem];
  if (frac) {
    return whole > 0 ? `${whole} ${frac}` : frac;
  }

  // Fallback to 2 decimal places if no common fraction matches
  return parseFloat(n.toFixed(2)).toString();
}

/**
 * Render a list of ingredients to the DOM.
 * Each card stores the full structured ingredient on a data attribute so
 * the scale/substitute buttons can access exact qty + unit.
 */
function renderIngredientsList(ingredients, containerId = 'ingredientsList', isTranslation = false) {
  const uniqueMap = new Map();
  (ingredients || []).forEach(ing => {
    const normName = (ing.name || '').toLowerCase().trim();
    const normUnit = (ing.unit || '').toLowerCase().trim();
    const key = `${normName}|${normUnit}`;
    if (!uniqueMap.has(key)) {
      uniqueMap.set(key, { ...ing });
    }
  });

  const dedupIngredients = Array.from(uniqueMap.values());
  ingredients = dedupIngredients;
  window.currentIngredients = dedupIngredients;

  if (!isTranslation) {
    originalIngredients = JSON.parse(JSON.stringify(dedupIngredients || []));
    const malayalamRegex = /[\u0D00-\u0D7F]/;
    const isMalayalam = originalIngredients.some(ing => malayalamRegex.test(ing.name || ''));
    if (isMalayalam) {
      sourceLanguage = "malayalam";
    } else {
      sourceLanguage = "english";
    }
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
    setTranslateSectionVisibility(false);
    return;
  }

  ingredients.forEach((ingredient, index) => {
    const displayText = buildIngredientDisplayText(ingredient);

    const div = document.createElement('div');
    div.className = 'ingredient-card';
    div.style.cssText = 'background:white;padding:15px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.05);margin-bottom:15px;max-width:80%;margin-left:auto;margin-right:auto;display:flex;flex-direction:column;';

    // Store structured data so we can retrieve it without re-parsing the text
    div.dataset.ingredientIndex = index;

    const row = document.createElement('div');
    row.style.cssText = 'display:flex;justify-content:space-between;align-items:center;gap:15px;width:100%;flex-wrap:wrap;';

    row.innerHTML = `
      <input
        type="text"
        value="${escapeHtml(displayText)}"
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

  setTranslateSectionVisibility(true);
}

async function handleIngredientClick(ingredient, dropdown, btn) {
  if (dropdown.style.display === 'block') {
    dropdown.style.display = 'none';
    return;
  }

  document.querySelectorAll('.substitute-dropdown').forEach(d => {
    if (d !== dropdown) d.style.display = 'none';
  });

  dropdown.style.display = 'block';

  if (dropdown.hasAttribute('data-fetched')) {
    return;
  }

  dropdown.innerHTML = '<p style="margin:0; color:#666;">Finding substitutes <i class="fas fa-spinner fa-spin"></i></p>';

  try {
    const data = await apiClient.getSubstitutions(
      ingredient.name,
      ingredient.quantity,
      ingredient.unit
    );

    const index = Array.from(document.querySelectorAll('.ingredient-card')).indexOf(dropdown.closest('.ingredient-card'));
    renderSubstitutions(data, dropdown, index);
    dropdown.setAttribute('data-fetched', 'true');
  } catch (error) {
    console.error('UI Controller Error [handleIngredientClick]:', error);
    dropdown.innerHTML = '<p style="color:red; margin:0;">Failed to fetch substitutions.</p>';
  }
}

/**
 * Replace an ingredient with a selected substitution
 */
function applySubstitution(index, subName) {
  if (confirm(`Substitute this ingredient with "${subName}"?`)) {
    const ingredients = window.currentIngredients || [];
    if (ingredients[index]) {
      const oldName = ingredients[index].name;
      ingredients[index].name = subName;

      // Also update originalIngredients so scaling works on the new ingredient
      if (window.originalIngredients && window.originalIngredients[index]) {
        window.originalIngredients[index].name = subName;
      }

      showSuccess(`Replaced "${oldName}" with "${subName}"`);
      renderIngredientsList(ingredients, 'ingredientsList', currentLanguage === 'translated');
    }
  }
}

function renderSubstitutions(data, container, ingredientIndex) {
  if (!container) return;
  container.innerHTML = '';

  // Support both old schema {substitutions:[]} and new schema {substitutes:[{name,ratio,note}]}
  const subs = data.substitutes || data.substitutions || [];

  if (!subs || subs.length === 0) {
    container.innerHTML = '<p style="margin:0;">No substitutions found.</p>';
    return;
  }

  const heading = document.createElement('h4');
  heading.innerText = 'Substitutions';
  heading.style.cssText = 'margin-top:0;margin-bottom:10px;color:#5a8c5a;';
  container.appendChild(heading);

  subs.forEach(sub => {
    const div = document.createElement('div');
    div.className = 'substitution-item';
    div.style.cssText = 'border-left:3px solid #E63946;padding:10px;margin-bottom:10px;background:white;cursor:pointer;transition:all 0.2s;border-radius:0 6px 6px 0;';

    // Handle both old schema (substitute / updated_quantity / reason) and new (name / ratio / note)
    const subName = sub.name || sub.substitute || 'Unknown';
    const subRatio = sub.ratio || sub.updated_quantity || '';
    const subNote = sub.note || sub.reason || '';

    div.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <strong style="color:#333;">${escapeHtml(subName)}</strong>
        <i class="fas fa-plus-circle" style="color:#7AB87A; opacity:0.6;"></i>
      </div>
      <span style="font-size:0.9rem;color:#666;display:block;">${escapeHtml(subRatio)}</span>
      <small style="color:#888;display:block;">${escapeHtml(subNote)}</small>
    `;

    div.onclick = (e) => {
      e.stopPropagation();
      applySubstitution(ingredientIndex, subName);
    };

    div.onmouseover = () => { div.style.backgroundColor = '#fff9f0'; div.style.transform = 'translateX(5px)'; };
    div.onmouseout = () => { div.style.backgroundColor = 'white'; div.style.transform = 'translateX(0)'; };

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

  // Deduplicate for the dropdown view
  const seen = new Set();
  ingredients.forEach((ingredient, index) => {
    const name = (ingredient.name || '').toLowerCase().trim();
    const unit = (ingredient.unit || '').toLowerCase().trim();
    const key = `${name}|${unit}`;

    if (!seen.has(key)) {
      seen.add(key);
      const option = document.createElement('option');
      option.value = index;
      const displayUnit = ingredient.unit && ingredient.unit.toLowerCase() !== 'whole' ? ` (${ingredient.unit})` : '';
      option.innerText = (ingredient.name || `Ingredient ${index + 1}`) + displayUnit;
      dropdown.appendChild(option);
    }
  });
}

/**
 * Get YouTube Video ID from URL
 */
function getYouTubeId(url) {
  if (!url) return null;
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
}

function renderVideoThumbnail(thumbnailUrl, videoTitle, youtubeUrl, containerId = 'thumbnailContainer') {
  const container = getElement(containerId);
  if (!container) return;

  container.innerHTML = '';

  const videoId = getYouTubeId(youtubeUrl);

  if (videoId) {
    // Render Embedded Player
    const playerWrapper = document.createElement('div');
    playerWrapper.className = 'video-player-wrapper';

    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${videoId}`;
    iframe.title = videoTitle || 'YouTube video player';
    iframe.frameBorder = '0';
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.allowFullscreen = true;

    playerWrapper.appendChild(iframe);
    container.appendChild(playerWrapper);
  } else {
    // Fallback to thumbnail image if ID cannot be extracted
    const img = document.createElement('img');
    img.src = thumbnailUrl;
    img.alt = 'YouTube Thumbnail';
    img.loading = 'eager';
    img.onerror = () => {
      img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%23ccc" width="320" height="180"/%3E%3C/svg%3E';
    };
    container.appendChild(img);
  }

  const title = document.createElement('p');
  title.innerText = videoTitle || 'Untitled Video';
  title.style.cssText = 'font-weight:bold;margin-top:10px;';
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
    const formattedDate = publishedDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    const views = result.views ? formatViewCount(result.views) : 'N/A';
    const videoUrl = `https://www.youtube.com/watch?v=${result.video_id}`;

    card.innerHTML = `
      <img src="${result.thumbnail_url}" alt="${escapeHtml(result.title)}" class="search-result-thumb"
           onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22160%22 height=%2290%22%3E%3Crect fill=%22%23ccc%22 width=%22160%22 height=%2290%22/%3E%3C/svg%3E'">
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
  return String(text).replace(/[&<>"']/g, m => map[m]);
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
    console.log('UI Controller: Fetching YouTube metadata');
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
      console.log('UI Controller: Parsing ingredients from description');
      ingredientsFound = await parseIngredientsUI(description);
    }

    if (!ingredientsFound) {
      console.log('UI Controller: No ingredients in description, falling back to audio extraction');
      const loadingEl = getElement('loading');
      const originalHtml = loadingEl ? loadingEl.innerHTML : '';
      if (loadingEl) {
        loadingEl.classList.add('loading-panel');
        loadingEl.innerHTML = `
          <div class="audio-loading-panel" role="status" aria-live="polite">
            <div class="audio-loading-spinner" aria-hidden="true"></div>
            <p class="audio-loading-title">No ingredient list in description. Processing audio...</p>
            <p class="audio-loading-subtitle">This may take up to a minute.</p>
          </div>
        `;
      }

      await extractAudioIngredients(youtubeLink.trim());

      if (loadingEl) {
        loadingEl.innerHTML = originalHtml;
        loadingEl.classList.remove('loading-panel');
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

async function parseIngredientsUI(text) {
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    console.warn('UI Controller: No text to parse');
    return false;
  }

  try {
    console.log('UI Controller: Calling apiClient.parseIngredients()');
    const response = await apiClient.parseIngredients(text);

    if (response.success && response.ingredients && response.ingredients.length > 0) {
      renderIngredientsList(response.ingredients);
      // Use the global window.currentIngredients which was just populated & deduped by renderIngredientsList
      populateAvailableIngredientsDropdown(window.currentIngredients);
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

async function searchYouTubeUI(pageToken = '') {
  const query = document.getElementById('searchQuery')?.value || '';
  const category = document.getElementById('recipeCategory')?.value || '';

  if (!isValidSearchQuery(query)) {
    showError('Please enter a search term.');
    return;
  }

  showLoadingState();

  try {
    console.log('UI Controller: Searching YouTube', { query, category });
    const response = await apiClient.searchYouTube(query, category, pageToken);

    if (!response.success) {
      showError('YouTube search failed. Please try again.');
      renderSearchResults([]);
      renderPaginationButtons(false, false, '', '');
      return;
    }

    const results = response.results || [];
    const hasNext = !!response.next_page_token;
    const hasPrev = !!response.prev_page_token;

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
    console.log('UI Controller: Extracting ingredients from audio');
    const response = await apiClient.extractAudioIngredients(youtubeLink.trim());

    if (!response.success) {
      showError('Could not extract audio ingredients. Try fetching from description instead.');
      return;
    }

    if (response.ingredients && response.ingredients.length > 0) {
      console.log('UI Controller: Rendering ingredients from audio extraction');
      renderIngredientsList(response.ingredients);
      // Use the global window.currentIngredients which was just populated & deduped by renderIngredientsList
      populateAvailableIngredientsDropdown(window.currentIngredients);
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

// ============================================================================
// SCALE RECIPE  ← KEY FIX: send structured objects, format output correctly
// ============================================================================

window.scaleRecipe = async function () {
  const valueEl = document.getElementById("scaleValue") || document.getElementById("scalingValue");
  const typeEl = document.getElementById("scaleType") || document.getElementById("scalingOption");
  const value = valueEl ? Number(valueEl.value) : 1;
  const type = typeEl ? typeEl.value : "servings";

  if (!window.currentIngredients || window.currentIngredients.length === 0) {
    showError("No ingredients to scale. Please fetch a recipe first.");
    return;
  }

  let finalValue = value;
  if (type === 'available') {
    if (window.isAvailableCustom) {
      const ingIdx = Number(document.getElementById('availableIngredient').value);
      const amount = Number(document.getElementById('availableAmount').value);
      if (!isNaN(ingIdx) && amount > 0 && window.currentIngredients[ingIdx]) {
        const originalAmount = window.currentIngredients[ingIdx].quantity || 1;
        finalValue = amount / originalAmount;
      } else {
        showError("Please enter a valid amount.");
        hideLoadingState();
        return;
      }
    } else {
      finalValue = window.lastAvailableFactor || 1;
    }
  }

  try {
    showLoadingState();

    const response = await apiClient.scaleRecipe({
      ingredients: window.currentIngredients || [],
      value: finalValue,
      type: 'servings' // Send as servings multiplier to the API
    });

    if (response && response.ingredients) {
      // Build display strings (may contain Malayalam from card inputs)
      const cardInputs = document.querySelectorAll('#ingredientsList .ingredient-card input.ingredient-name');

      const scaledDisplay = response.ingredients.map((ing, idx) => {
        let qty = ing.quantity;
        let unit = ing.unit || '';
        let name = ing.name || '';

        const unitAsNum = parseFloat(unit);
        if (!isNaN(unitAsNum) && Math.abs(qty - value) < 0.001) {
          const originalQty = unitAsNum;
          const nameMatch = name.match(/^(\S+)\s+(.*)$/);
          if (nameMatch) { unit = nameMatch[1]; name = nameMatch[2]; }
          else { unit = ''; }
          qty = originalQty * value;
        }

        const formattedQty = formatQtyDisplay(qty);

        const isWhole = unit.trim().toLowerCase() === 'whole';
        const displayUnit = isWhole ? '' : unit;
        return [formattedQty, displayUnit, name].filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
      });

      // ── NEW: Build English-only strings from window.currentIngredients ──
      // window.currentIngredients.name is always the English whitelist name.
      const scaledEnglish = window.currentIngredients.map((orig, idx) => {
        const scaledIng = response.ingredients[idx] || orig;
        let qty = scaledIng.quantity || orig.quantity || 1;
        let unit = orig.unit || '';
        const name = orig.name || '';   // always English

        const unitAsNum = parseFloat(scaledIng.unit);
        if (!isNaN(unitAsNum) && Math.abs(qty - value) < 0.001) {
          qty = unitAsNum * value;
          unit = (scaledIng.name || '').split(' ')[0] || orig.unit || '';
        }

        const formattedQty = formatQtyDisplay(qty);

        const isWhole = unit.trim().toLowerCase() === 'whole';
        const displayUnit = isWhole ? '' : unit;
        return [formattedQty, displayUnit, name].filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
      });

      sessionStorage.setItem('scaledIngredients', JSON.stringify(scaledDisplay));
      sessionStorage.setItem('scaledIngredientsEnglish', JSON.stringify(scaledEnglish)); // ← NEW
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

// ============================================================================
// OTHER UI HELPERS
// ============================================================================

function setAvailableQuickScale(factor, btn) {
  // Update UI chips
  const container = document.getElementById('available-quick-chips');
  if (container) {
    container.querySelectorAll('.scale-chip').forEach(c => c.classList.remove('active'));
  }
  if (btn) btn.classList.add('active');

  // Hide custom input
  const customDiv = document.getElementById('available-custom-input');
  if (customDiv) customDiv.style.display = 'none';

  // Store the factor globally so scaleRecipe can use it
  window.lastAvailableFactor = factor;
  window.isAvailableCustom = false;
}

function showAvailableCustom(btn) {
  // Update UI chips
  const container = document.getElementById('available-quick-chips');
  if (container) {
    container.querySelectorAll('.scale-chip').forEach(c => c.classList.remove('active'));
  }
  if (btn) btn.classList.add('active');

  // Show custom input
  const customDiv = document.getElementById('available-custom-input');
  if (customDiv) customDiv.style.display = 'block';

  window.isAvailableCustom = true;
}

function updateScalingOptions() {
  const scalingOption = document.getElementById('scalingOption')?.value || 'servings';

  document.querySelectorAll('.scaling-method').forEach(m => { m.style.display = 'none'; });

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
      // Reset to 1x by default
      const defaultChip = document.querySelector('#available-quick-chips .scale-chip:nth-child(3)');
      if (defaultChip) setAvailableQuickScale(1, defaultChip);
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
  console.log('UI Controller: Loading saved recipes from localStorage');

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
        <button onclick="loadRecipeUI('${escapeHtml(recipe.id)}')"><i class="fas fa-eye"></i></button>
        <button onclick="deleteRecipeUI('${escapeHtml(recipe.id)}')"><i class="fas fa-trash"></i></button>
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

  if (getElement('saved-recipes')) {
    loadSavedRecipes();
  }

  document.querySelectorAll('.search-tab').forEach(tab => {
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
  if (scalingSelect) {
    scalingSelect.addEventListener('change', updateScalingOptions);
  }

  const enterRecipeBtn = getElement('enterRecipeManually');
  if (enterRecipeBtn) {
    enterRecipeBtn.addEventListener('click', () => {
      window.location.href = 'enter_recipe.html';
    });
  }

  const translateBtn = getElement('translateBtn');
  if (translateBtn) {
    translateBtn.addEventListener('click', translateIngredientsUI);
  }

  setTranslateSectionVisibility(false);

  console.log('UI Controller: Ready');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeUI);
} else {
  initializeUI();
}

window.initializeUI = initializeUI;