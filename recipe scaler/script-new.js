document.addEventListener('DOMContentLoaded', function () {
  let recipeName = sessionStorage.getItem('recipeName');
  let mainIngredient = sessionStorage.getItem('mainIngredient');
  let scaledIngredients = sessionStorage.getItem('scaledIngredients');
  let youtubeVideoUrl = sessionStorage.getItem('youtubeVideoUrl');
  let isManualRecipe = sessionStorage.getItem('isManualRecipe');

  // ── DEBUG: log raw sessionStorage value so we can see what was stored ──
  console.log('[scaled.html] raw scaledIngredients from sessionStorage:', scaledIngredients);
  console.log('[scaled.html] recipeName:', recipeName);

  if (recipeName && scaledIngredients) {
    document.getElementById('recipeName').innerText = recipeName;
    document.getElementById('mainIngredient').innerText = mainIngredient || '';

    // Support both JSON array of strings and legacy <br>-separated strings
    let lines;
    try {
      const parsed = JSON.parse(scaledIngredients);
      if (Array.isArray(parsed)) {
        lines = parsed;
      } else {
        // It was stored as a JSON object — shouldn't happen but handle gracefully
        lines = [String(parsed)];
      }
    } catch (e) {
      // Fallback: old <br> format
      lines = scaledIngredients.split('<br>').filter(Boolean);
    }

    console.log('[scaled.html] lines to render:', lines);

    const ul = document.getElementById('scaledIngredients');
    ul.innerHTML = '';

    lines.forEach(line => {
      const trimmed = line.trim();
      // Skip blank lines or separator lines (lots of dashes etc.)
      if (!trimmed || /^[-*=]{5,}$/.test(trimmed)) return;

      const li = document.createElement('li');
      li.textContent = trimmed;
      li.style.cursor = 'pointer';
      li.style.padding = '8px';
      li.style.borderRadius = '4px';
      li.style.transition = 'all 0.3s ease';

      // Make editable on click
      li.addEventListener('click', function () {
        if (this.querySelector('input')) return;
        const originalText = this.textContent;
        const input = document.createElement('input');
        input.type = 'text';
        input.value = originalText;
        input.style.cssText = 'width:100%;padding:8px;border:2px solid #D96B43;border-radius:4px;font-size:16px;';

        this.textContent = '';
        this.appendChild(input);
        input.focus();
        input.select();

        const saveEdit = () => { this.textContent = input.value.trim(); };
        input.addEventListener('blur', saveEdit);
        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') saveEdit(); });
      });

      ul.appendChild(li);
    });

    // Add YouTube video link only if it's not a manually entered recipe
    if (youtubeVideoUrl && isManualRecipe !== 'true') {
      const sourceDiv = document.createElement('div');
      sourceDiv.className = 'video-source';
      sourceDiv.innerHTML = `
        <p>Original Recipe:
          <a href="${youtubeVideoUrl}" target="_blank">Watch on YouTube</a>
        </p>
      `;
      const mainIngredientElement = document.getElementById('mainIngredient');
      if (mainIngredientElement.nextSibling) {
        mainIngredientElement.parentNode.insertBefore(sourceDiv, mainIngredientElement.nextSibling);
      } else {
        mainIngredientElement.parentNode.appendChild(sourceDiv);
      }
    }

    displayRecipeNotes();
  } else {
    document.getElementById('recipeName').innerText = 'No Recipe';
    document.getElementById('mainIngredient').innerText = 'N/A';
    document.getElementById('scaledIngredients').innerHTML =
      '<li>No scaled recipe found. Please return to the main page and scale your recipe again.</li>';
  }
});

// ============================================================================
// Display recipe notes and instructions
// ============================================================================
function displayRecipeNotes() {
  const notes = sessionStorage.getItem('recipeNotes');
  const stepsJson = sessionStorage.getItem('recipeSteps');
  if (!notes && !stepsJson) return;

  const notesDisplay = document.getElementById('recipeNotesDisplay');
  if (!notesDisplay) return;
  notesDisplay.innerHTML = '';

  if (notes) {
    const notesDiv = document.createElement('div');
    notesDiv.className = 'recipe-notes-box';
    notesDiv.innerHTML = `<h3>📝 Cooking Notes</h3><p>${notes.replace(/\n/g, '<br>')}</p>`;
    notesDisplay.appendChild(notesDiv);
  }

  if (stepsJson) {
    const steps = JSON.parse(stepsJson);
    const stepsDiv = document.createElement('div');
    stepsDiv.className = 'recipe-instructions-box';
    stepsDiv.innerHTML = '<h3>👨‍🍳 Instructions</h3>';
    const ol = document.createElement('ol');
    steps.forEach(step => {
      if (step.trim()) {
        const li = document.createElement('li');
        li.textContent = step;
        ol.appendChild(li);
      }
    });
    stepsDiv.appendChild(ol);
    notesDisplay.appendChild(stepsDiv);
  }
}

// ============================================================================
// Save / export helpers
// ============================================================================
function saveRecipeWithNotes() {
  const recipeName = document.getElementById('recipeName').innerText;
  const mainIngredient = document.getElementById('mainIngredient').innerText;
  const ingredients = [];
  document.querySelectorAll('#scaledIngredients li').forEach(item => { ingredients.push(item.innerText); });

  const notes = sessionStorage.getItem('recipeNotes') || '';
  const stepsJson = sessionStorage.getItem('recipeSteps') || '[]';
  const youtubeLink = sessionStorage.getItem('youtubeVideoUrl') || '';

  const recipe = {
    id: Date.now().toString(),
    name: recipeName,
    mainIngredient,
    ingredients,
    notes,
    steps: JSON.parse(stepsJson),
    youtubeLink,
    savedDate: new Date().toISOString()
  };

  let savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  savedRecipes.push(recipe);
  localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));
  alert('Recipe saved successfully!');
}

function saveRecipe() { saveRecipeWithNotes(); }

function modifyScaling() {
  sessionStorage.setItem('modifyingRecipe', 'true');
  window.location.href = 'index.html';
}

function printRecipe() { window.print(); }
// ============================================================================
// PDF SAFE TEXT HELPER
// ============================================================================
// ============================================================================
// PDF SAFE TEXT — handles fractions and typographic chars, strips non-Latin-1
// ============================================================================
function pdfSafeText(str) {
  if (!str) return '';
  return str
    .replace(/½/g, '1/2').replace(/¼/g, '1/4').replace(/¾/g, '3/4')
    .replace(/⅓/g, '1/3').replace(/⅔/g, '2/3').replace(/⅛/g, '1/8')
    .replace(/⅜/g, '3/8').replace(/⅝/g, '5/8').replace(/⅞/g, '7/8')
    .replace(/[\u2018\u2019]/g, "'").replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2013/g, '-').replace(/\u2014/g, '--').replace(/\u2026/g, '...')
    // Allow Malayalam (\u0D00-\u0D7F) and common Latin chars
    .replace(/[^\x00-\xFF\u0D00-\u0D7F]/g, '');
}

// ============================================================================
// GET SAFE ENGLISH INGREDIENT LINES FOR PDF
// Reads the English-only key saved at scale time — never touches displayed text
// ============================================================================
function getSafeIngredientLines() {
  // PRIMARY: English strings saved by scaleRecipe at scale time
  try {
    const eng = sessionStorage.getItem('scaledIngredientsEnglish');
    if (eng) {
      const parsed = JSON.parse(eng);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed.map(pdfSafeText).filter(Boolean);
      }
    }
  } catch (e) { /* fall through */ }

  // FALLBACK 1: window.currentIngredients (English names, structured)
  if (window.currentIngredients && window.currentIngredients.length > 0) {
    return window.currentIngredients.map(ing => {
      const qty = ing.quantity || '';
      const unit = (ing.unit && ing.unit.toLowerCase() !== 'whole') ? ing.unit : '';
      const name = ing.name || '';
      return pdfSafeText([qty, unit, name].filter(Boolean).join(' ').trim());
    }).filter(Boolean);
  }

  // FALLBACK 2: scaledIngredients JSON (display strings — Malayalam stripped)
  try {
    const raw = sessionStorage.getItem('scaledIngredients');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed.map(pdfSafeText).filter(Boolean);
      }
    }
  } catch (e) { /* fall through */ }

  // FALLBACK 3: DOM scrape (last resort)
  const lines = [];
  document.querySelectorAll('#scaledIngredients li').forEach(li => {
    lines.push(pdfSafeText(li.innerText.trim()));
  });
  return lines.filter(Boolean);
}

// ============================================================================
// PDF EXPORT
// ============================================================================
function exportPDFWithNotes() {
  const element = document.querySelector('.scaled-recipe');
  const recipeName = (document.getElementById('recipeName').innerText || 'Recipe').trim();
  const safeFileName = recipeName.replace(/[^a-zA-Z0-9_\- ]/g, '').replace(/\s+/g, '_') || 'recipe';

  // --- PREPARE FOR EXPORT ---
  const originalDisplay = new Map();
  const originalStyles = {
    maxWidth: element.style.maxWidth,
    width: element.style.width,
    margin: element.style.margin,
    padding: element.style.padding,
    boxShadow: element.style.boxShadow,
    backgroundColor: element.style.backgroundColor
  };

  const mainIngredientEl = document.getElementById('mainIngredient');
  const originalMainDisplay = mainIngredientEl ? mainIngredientEl.style.display : '';
  if (mainIngredientEl && (mainIngredientEl.innerText.trim() === '' || mainIngredientEl.innerText.trim().toLowerCase() === 'main ingredient:')) {
    mainIngredientEl.style.display = 'none';
  }

  const selectorsToHide = [
    '.recipe-actions',
    '.nav-buttons',
    '.recipe-controls',
    '.recipe-hint',
    '.video-source'
  ];

  selectorsToHide.forEach(selector => {
    const el = document.querySelector(selector);
    if (el) {
      originalDisplay.set(selector, el.style.display);
      el.style.display = 'none';
    }
  });

  // Temporarily normalize element for clean capture
  element.style.width = '710px';
  element.style.maxWidth = '710px';
  element.style.margin = '0';
  element.style.padding = '25px';
  element.style.backgroundColor = 'white';
  element.style.boxShadow = 'none';

  const opt = {
    margin: 10,
    filename: `${safeFileName}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      logging: false,
      scrollY: 0,
      scrollX: 0
    },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pagebreak: {
      mode: ['css', 'legacy'],
      avoid: 'li, h2, p, .recipe-notes-box h3, .recipe-instructions-box h3'
    }
  };

  // Trigger export
  window.html2pdf().set(opt).from(element).save().then(() => {
    // --- RESTORE AFTER EXPORT ---
    element.style.maxWidth = originalStyles.maxWidth;
    element.style.width = originalStyles.width;
    element.style.margin = originalStyles.margin;
    element.style.padding = originalStyles.padding;
    element.style.boxShadow = originalStyles.boxShadow;
    element.style.backgroundColor = originalStyles.backgroundColor;
    if (mainIngredientEl) mainIngredientEl.style.display = originalMainDisplay;

    selectorsToHide.forEach(selector => {
      const el = document.querySelector(selector);
      if (el) {
        el.style.display = originalDisplay.get(selector) || '';
      }
    });
  }).catch(err => {
    console.error('PDF Export Error:', err);
    alert('Failed to export PDF. Please try again.');

    element.style.maxWidth = originalStyles.maxWidth;
    element.style.width = originalStyles.width;
    element.style.margin = originalStyles.margin;
    element.style.padding = originalStyles.padding;
    element.style.boxShadow = originalStyles.boxShadow;
    element.style.backgroundColor = originalStyles.backgroundColor;
    if (mainIngredientEl) mainIngredientEl.style.display = originalMainDisplay;

    selectorsToHide.forEach(selector => {
      const el = document.querySelector(selector);
      if (el) {
        el.style.display = originalDisplay.get(selector) || '';
      }
    });
  });
}

function exportPDF() { exportPDFWithNotes(); }
function exportTextWithNotes() {
  const recipeName = document.getElementById('recipeName').innerText;
  const ingredients = [];
  document.querySelectorAll('#scaledIngredients li').forEach(item => { ingredients.push(item.innerText); });
  const notes = sessionStorage.getItem('recipeNotes');
  const stepsJson = sessionStorage.getItem('recipeSteps');
  const steps = stepsJson ? JSON.parse(stepsJson) : [];

  let content = `${recipeName}\n\nIngredients:\n`;
  ingredients.forEach(i => { content += `- ${i}\n`; });
  if (notes) content += `\nCooking Notes:\n${notes}\n`;
  if (steps.length > 0) {
    content += '\nInstructions:\n';
    steps.forEach((s, i) => { if (s.trim()) content += `${i + 1}. ${s}\n`; });
  }

  const el = document.createElement('a');
  el.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
  el.setAttribute('download', `${recipeName.replace(/\s+/g, '_')}.txt`);
  el.style.display = 'none';
  document.body.appendChild(el);
  el.click();
  document.body.removeChild(el);
}

function exportText() { exportTextWithNotes(); }

function emailRecipe() {
  const recipeName = document.getElementById('recipeName').innerText;
  let body = `${recipeName}%0D%0A%0D%0AIngredients:%0D%0A`;
  document.querySelectorAll('#scaledIngredients li').forEach(item => {
    body += `- ${item.innerText}%0D%0A`;
  });
  window.location.href = `mailto:?subject=Recipe: ${recipeName}&body=${body}`;
}

// ============================================================================
// Unit conversion
// ============================================================================
const unitConversionMap = {
  'gram': { 'oz': 0.035274, 'lb': 0.00220462 },
  'g': { 'oz': 0.035274, 'lb': 0.00220462 },
  'kg': { 'oz': 35.274, 'lb': 2.20462 },
  'oz': { 'gram': 28.3495, 'g': 28.3495, 'kg': 0.0283495 },
  'lb': { 'gram': 453.592, 'g': 453.592, 'kg': 0.453592 },
  'ml': { 'cup': 0.00423344, 'tbsp': 0.067628, 'tsp': 0.202884, 'oz': 0.033814 },
  'l': { 'cup': 4.22675, 'tbsp': 67.628, 'tsp': 202.884, 'oz': 33.814 },
  'liter': { 'cup': 4.22675, 'tbsp': 67.628, 'tsp': 202.884, 'oz': 33.814 },
  'cup': { 'ml': 236.588, 'tbsp': 16, 'tsp': 48, 'oz': 8 },
  'cups': { 'ml': 236.588, 'tbsp': 16, 'tsp': 48, 'oz': 8 },
  'tbsp': { 'ml': 14.7868, 'cup': 0.0625, 'tsp': 3, 'oz': 0.5 },
  'tsp': { 'ml': 4.92892, 'cup': 0.0208333, 'tbsp': 0.333333, 'oz': 0.166667 },
};

function convertUnit(quantity, fromUnit, toUnit) {
  if (fromUnit === toUnit) return quantity;
  const f = fromUnit.toLowerCase();
  const t = toUnit.toLowerCase();
  if (unitConversionMap[f] && unitConversionMap[f][t]) return quantity * unitConversionMap[f][t];
  return quantity;
}

function formatQuantity(qty) {
  const n = parseFloat(qty);
  if (isNaN(n)) return '1';
  if (Number.isInteger(n)) return String(n);

  const whole = Math.floor(n);
  const rem = parseFloat((n - whole).toFixed(3));

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
  return parseFloat(n.toFixed(2)).toString();
}

function parseIngredientForConversion(ingredientStr) {
  const match = ingredientStr.match(/^([\d.,\s\/½¼¾⅓⅔⅛⅙]+)\s*(\w+)\s+(.*)$/);
  if (match) {
    return { quantity: parseFloat(match[1].replace(/,/g, '').replace(/[½¼¾⅓⅔⅛⅙]/g, '0')) || 1, unit: match[2], name: match[3] };
  }
  return { quantity: 1, unit: '', name: ingredientStr };
}

function formatConvertedIngredient(quantity, unit, name) {
  const formatted = formatQuantity(quantity);
  return `${formatted} ${unit} ${name}`.trim();
}

function switchUnitSystem(system) {
  const ul = document.getElementById('scaledIngredients');
  if (!ul) return;
  const items = ul.querySelectorAll('li');
  const originalIngredients = sessionStorage.getItem('scaledIngredients_original');

  if (!originalIngredients) {
    const originals = [];
    items.forEach(item => { originals.push(item.textContent); });
    sessionStorage.setItem('scaledIngredients_original', JSON.stringify(originals));
  }

  if (system === 'original') {
    if (originalIngredients) {
      const originals = JSON.parse(originalIngredients);
      items.forEach((item, i) => { if (originals[i]) item.textContent = originals[i]; });
    }
  } else if (system === 'metric') {
    const originals = originalIngredients ? JSON.parse(originalIngredients) : [];
    items.forEach((item, i) => {
      const original = originals[i] || item.textContent;
      const parsed = parseIngredientForConversion(original);
      if (parsed.unit && unitConversionMap[parsed.unit.toLowerCase()]) {
        let newUnit = parsed.unit, newQty = parsed.quantity;
        if (['oz', 'cup', 'cups', 'tbsp', 'tsp'].includes(newUnit.toLowerCase())) { newUnit = 'ml'; newQty = convertUnit(newQty, parsed.unit, newUnit); }
        else if (['lb'].includes(newUnit.toLowerCase())) { newUnit = 'g'; newQty = convertUnit(newQty, parsed.unit, newUnit); }
        item.textContent = formatConvertedIngredient(newQty, newUnit, parsed.name);
      }
    });
  } else if (system === 'imperial') {
    const originals = originalIngredients ? JSON.parse(originalIngredients) : [];
    items.forEach((item, i) => {
      const original = originals[i] || item.textContent;
      const parsed = parseIngredientForConversion(original);
      if (parsed.unit && unitConversionMap[parsed.unit.toLowerCase()]) {
        let newUnit = parsed.unit, newQty = parsed.quantity;
        if (['ml', 'l', 'liter'].includes(newUnit.toLowerCase())) { newUnit = 'cup'; newQty = convertUnit(newQty, parsed.unit, newUnit); }
        else if (['g', 'kg'].includes(newUnit.toLowerCase())) { newUnit = 'oz'; newQty = convertUnit(newQty, parsed.unit, newUnit); }
        item.textContent = formatConvertedIngredient(newQty, newUnit, parsed.name);
      }
    });
  }
}
