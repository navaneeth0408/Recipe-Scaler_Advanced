const API_KEY = 'AIzaSyCtGe8vWQ8-GOlz7SEYd-qq6VMMA-R6LE4';

function getVideoId(url) {
  const regExp = /^.*(youtu.be\/|v\/|\/u\/\w\/|embed\/|watch\?v=|&v=|v=)([^#&?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
}

function showLoading() {
  document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
  document.getElementById('loading').style.display = 'none';
}

// NOTE: fetchIngredients, scaleRecipe, extractAudioIngredients are all defined
// in ui-controller.js which is loaded AFTER this file in index.html.
// The versions here are kept only for enter_recipe.html (manual recipe entry)
// which does NOT load ui-controller.js.

async function fetchIngredients() {
  const youtubeLink = document.getElementById("youtubeLink").value;
  if (!youtubeLink.trim()) {
    alert('Please enter a valid YouTube Video URL.');
    return;
  }
  showLoading();
  try {
    const response = await apiClient.extractYouTubeMetadata(youtubeLink);
    if (response.success && response.metadata) {
      const metadata = response.metadata;
      displayThumbnail(metadata.thumbnail_url, metadata.title);
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

function displayThumbnail(thumbnailUrl, videoTitle) {
  const thumbnailContainer = document.getElementById("thumbnailContainer");
  if (thumbnailContainer) {
    thumbnailContainer.innerHTML = "";
    const img = document.createElement("img");
    img.src = thumbnailUrl;
    img.alt = "YouTube Thumbnail";
    img.loading = "eager";
    thumbnailContainer.appendChild(img);
    const title = document.createElement("p");
    title.innerText = videoTitle;
    thumbnailContainer.appendChild(title);
    const youtubeLink = document.getElementById("youtubeLink").value;
    const linkContainer = document.createElement("div");
    linkContainer.className = "video-source";
    const linkElement = document.createElement("a");
    linkElement.href = youtubeLink;
    linkElement.target = "_blank";
    linkElement.innerHTML = '<i class="fab fa-youtube"></i> Watch on YouTube';
    linkContainer.appendChild(linkElement);
    thumbnailContainer.appendChild(linkContainer);
  }
}

async function parseIngredients(description) {
  if (!description) return;
  try {
    const response = await apiClient.parseIngredients(description);
    if (response.success && response.ingredients) {
      populateAvailableIngredients(response.ingredients);
      displayIngredientsList(response.ingredients);
    } else {
      displayIngredientsList([]);
    }
  } catch (error) {
    console.error('Error parsing ingredients:', error);
    displayIngredientsList([]);
  }
}

function displayIngredientsList(ingredients) {
  const ingredientsList = document.getElementById("ingredientsList");
  if (!ingredientsList) return;
  ingredientsList.innerHTML = "";
  ingredients.forEach(ingredient => {
    const div = document.createElement("div");
    div.className = "ingredient-entry";
    const quantity = ingredient.quantity != null ? ingredient.quantity : 1;
    const unit = ingredient.unit || '';
    const name = ingredient.name || '';
    div.innerHTML = `
      <input type="number" class="ingredient-quantity" step="0.1" value="${quantity}" style="width: 60px;">
      <input type="text" class="ingredient-unit" value="${unit}" style="width: 80px;" placeholder="Unit">
      <input type="text" class="ingredient-name" value="${name}" placeholder="Ingredient">
    `;
    ingredientsList.appendChild(div);
  });
}

function populateAvailableIngredients(ingredients) {
  const dropdown = document.getElementById("availableIngredient");
  if (!dropdown) return;
  dropdown.innerHTML = '';

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

function addIngredient() {
  const ingredientsDiv = document.getElementById("recipeIngredientsList");
  if (ingredientsDiv) {
    const div = document.createElement("div");
    div.className = "ingredient-entry";
    div.innerHTML = `
      <input type="text" placeholder="Ingredient Name" class="ingredient-name">
      <input type="number" placeholder="Quantity" class="ingredient-quantity" min="0">
      <input type="text" placeholder="Unit (e.g., cups, tsp)" class="ingredient-unit">
    `;
    ingredientsDiv.appendChild(div);
  }
}

// ============================================================================
// scaleRecipe for enter_recipe.html (manual entry — no backend ingredients)
// For index.html the ui-controller.js version takes precedence (loaded after).
// ============================================================================
function scaleRecipe() {
  // If we are on the index page and have fetched ingredients, delegate to
  // the ui-controller.js version (window.scaleRecipe is set there as an
  // async function that calls the API).
  // This fallback only runs on enter_recipe.html or when no fetched ingredients exist.
  const fetchedIngredientsDiv = document.getElementById("ingredientsList");
  if (fetchedIngredientsDiv && fetchedIngredientsDiv.children.length > 0) {
    // On index.html: ui-controller's window.scaleRecipe handles this.
    // But since script.js is loaded first on enter_recipe.html and there is
    // no ui-controller.js there, we call the manual path below.
    if (typeof window._uiControllerLoaded !== 'undefined') {
      // ui-controller is loaded — its version already overrode window.scaleRecipe
      return;
    }
    scaleFetchedIngredients();
    return;
  }

  // Manual recipe entry path (enter_recipe.html)
  if (typeof saveRecipeNotes === 'function') saveRecipeNotes();

  const recipeName = document.getElementById("recipeName").value.trim();
  const mainIngredient = document.getElementById("mainIngredient").value.trim();
  const scalingOption = document.getElementById("scalingOption").value;
  const scalingValue = parseFloat(document.getElementById("scalingValue").value);

  if (!recipeName || !mainIngredient || isNaN(scalingValue) || scalingValue <= 0) {
    alert("Please enter valid recipe details and scaling value.");
    return;
  }

  const ingredients = document.querySelectorAll(".ingredient-entry");
  const ingredientData = [];
  let mainQuantity = 1;

  ingredients.forEach(ing => {
    const name = ing.querySelector(".ingredient-name").value.trim();
    const quantity = parseFloat(ing.querySelector(".ingredient-quantity").value);
    const unit = ing.querySelector(".ingredient-unit").value.trim();

    if (!name || isNaN(quantity) || quantity <= 0 || !unit) {
      alert("Please enter valid ingredient details.");
      return;
    }
    if (name.toLowerCase() === mainIngredient.toLowerCase()) mainQuantity = quantity;
    ingredientData.push({ name, quantity, unit });
  });

  const scaleFactor = scalingOption === "quantity" ? scalingValue / mainQuantity : scalingValue;

  const scaledIngredients = ingredientData.map(ing => {
    const newQty = formatQuantity(ing.quantity * scaleFactor);
    return `${newQty} ${ing.unit} ${ing.name}`;
  });

  sessionStorage.setItem('recipeName', recipeName);
  sessionStorage.setItem('mainIngredient', `Main Ingredient: ${mainIngredient}`);
  sessionStorage.setItem('scaledIngredients', JSON.stringify(scaledIngredients));
  sessionStorage.setItem('isManualRecipe', 'true');

  window.location.href = "scaled.html";
}

// Helper kept for backward-compat but should not run on index.html anymore
async function scaleFetchedIngredients() {
  const scalingValue = parseFloat(document.getElementById("scalingValue").value);
  if (isNaN(scalingValue) || scalingValue <= 0) {
    alert("Please enter a valid scaling value.");
    return;
  }

  showLoading();

  try {
    const ingredientElements = document.querySelectorAll("#ingredientsList .ingredient-entry");
    if (ingredientElements.length === 0) {
      alert("No ingredients found. Please fetch ingredients first.");
      return;
    }

    const ingredients = Array.from(ingredientElements).map(ing => ({
      name: ing.querySelector(".ingredient-name").value.trim(),
      quantity: parseFloat(ing.querySelector(".ingredient-quantity").value) || 1,
      unit: ing.querySelector(".ingredient-unit").value.trim()
    }));

    const response = await apiClient.scaleRecipe({
      ingredients,
      value: scalingValue,
      type: 'servings'
    });

    if (response.success && response.ingredients) {
      const scaledIngredients = response.ingredients.map(ing => {
        const qty = ing.quantity;
        const unit = (ing.unit || '').trim();
        const name = (ing.name || '').trim();
        const isWhole = unit.toLowerCase() === 'whole';
        if (isWhole || unit === '') return `${qty} ${name}`.trim();
        return `${qty} ${unit} ${name}`.trim();
      });

      const titleElement = document.querySelector("#thumbnailContainer p");
      const recipeName = titleElement ? titleElement.innerText : "Scaled Recipe";

      sessionStorage.setItem('recipeName', recipeName);
      sessionStorage.setItem('mainIngredient', '');
      sessionStorage.setItem('scaledIngredients', JSON.stringify(scaledIngredients));
      sessionStorage.setItem('youtubeVideoUrl', document.getElementById("youtubeLink").value);
      sessionStorage.setItem('isManualRecipe', 'false');

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

function parseQuantity(qtyStr) {
  if (!qtyStr) return 1;
  qtyStr = qtyStr.replace(/\s+/g, ' ').trim();
  if (qtyStr.includes('-') || qtyStr.includes(' to ')) {
    const range = qtyStr.includes('-') ? qtyStr.split('-') : qtyStr.split(' to ');
    if (range.length === 2) {
      const start = parseFloat(range[0].trim());
      const end = parseFloat(range[1].trim());
      if (!isNaN(start) && !isNaN(end)) return (start + end) / 2;
    }
  }
  if (qtyStr.includes(' ') && qtyStr.includes('/')) {
    const parts = qtyStr.split(' ');
    if (parts.length === 2) {
      const whole = parseFloat(parts[0]);
      if (parts[1].includes('/')) {
        const fracParts = parts[1].split('/');
        if (fracParts.length === 2) {
          const num = parseFloat(fracParts[0]);
          const den = parseFloat(fracParts[1]);
          if (!isNaN(whole) && !isNaN(num) && !isNaN(den) && den !== 0)
            return whole + (num / den);
        }
      }
    }
  }
  if (qtyStr.includes('/')) {
    const parts = qtyStr.split('/');
    if (parts.length === 2 && !isNaN(parseFloat(parts[0])) && !isNaN(parseFloat(parts[1])) && parseFloat(parts[1]) !== 0)
      return parseFloat(parts[0]) / parseFloat(parts[1]);
  }
  const num = parseFloat(qtyStr);
  return isNaN(num) ? 1 : num;
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

function updateScalingOptions() {
  const scalingOption = document.getElementById("scalingOption").value;
  document.querySelectorAll('.scaling-method').forEach(el => { el.style.display = 'none'; });
  switch (scalingOption) {
    case 'servings':
    case 'quantity':
      document.getElementById('standard-scaling').style.display = 'block';
      break;
    case 'available':
      document.getElementById('available-scaling').style.display = 'block';
      break;
    case 'custom':
      document.getElementById('custom-scaling').style.display = 'block';
      break;
  }
}

function saveRecipe() {
  const recipeName = document.getElementById('recipeName').innerText;
  const mainIngredient = document.getElementById('mainIngredient').innerText;
  const ingredients = [];
  document.querySelectorAll('#scaledIngredients li').forEach(item => { ingredients.push(item.innerText); });
  const youtubeLink = sessionStorage.getItem('youtubeVideoUrl') || '';
  const recipe = {
    id: Date.now().toString(),
    name: recipeName,
    mainIngredient,
    ingredients,
    youtubeLink,
    savedDate: new Date().toISOString()
  };
  let savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  savedRecipes.push(recipe);
  localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));
  alert('Recipe saved successfully!');
}

function loadSavedRecipes() {
  const savedRecipesContainer = document.getElementById('saved-recipes');
  const savedRecipesList = document.getElementById('saved-recipes-list');
  if (!savedRecipesContainer || !savedRecipesList) return;
  const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  if (savedRecipes.length === 0) { savedRecipesContainer.style.display = 'none'; return; }
  savedRecipesContainer.style.display = 'block';
  savedRecipesList.innerHTML = '';
  savedRecipes.forEach(recipe => {
    const item = document.createElement('div');
    item.className = 'saved-recipe-item';
    item.innerHTML = `
      <h3>${recipe.name}</h3>
      <p>${recipe.ingredients.length} ingredients</p>
      <div class="saved-recipe-actions">
        <button onclick="loadRecipe('${recipe.id}')"><i class="fas fa-eye"></i></button>
        <button onclick="deleteRecipe('${recipe.id}')"><i class="fas fa-trash"></i></button>
      </div>
    `;
    savedRecipesList.appendChild(item);
  });
}

function loadRecipe(recipeId) {
  const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  const recipe = savedRecipes.find(r => r.id === recipeId);
  if (recipe) {
    sessionStorage.setItem('recipeName', recipe.name);
    sessionStorage.setItem('mainIngredient', recipe.mainIngredient);
    sessionStorage.setItem('scaledIngredients', JSON.stringify(recipe.ingredients));
    if (recipe.youtubeLink) sessionStorage.setItem('youtubeVideoUrl', recipe.youtubeLink);
    window.location.href = 'scaled.html';
  }
}

function deleteRecipe(recipeId) {
  if (confirm('Are you sure you want to delete this recipe?')) {
    let savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
    savedRecipes = savedRecipes.filter(r => r.id !== recipeId);
    localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));
    loadSavedRecipes();
  }
}

function printRecipe() { window.print(); }

function exportPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  const recipeName = document.getElementById('recipeName').innerText;
  doc.setFontSize(18);
  doc.text(recipeName, 20, 20);
  let y = 40;
  document.querySelectorAll('#scaledIngredients li').forEach(item => {
    doc.setFontSize(12);
    doc.text('• ' + item.innerText, 25, y);
    y += 10;
    if (y > 280) { doc.addPage(); y = 20; }
  });
  doc.save(`${recipeName.replace(/\s+/g, '_')}.pdf`);
}

function exportText() {
  const recipeName = document.getElementById('recipeName').innerText;
  let content = `${recipeName}\n\nIngredients:\n`;
  document.querySelectorAll('#scaledIngredients li').forEach(item => {
    content += `- ${item.innerText}\n`;
  });
  const element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
  element.setAttribute('download', `${recipeName.replace(/\s+/g, '_')}.txt`);
  element.style.display = 'none';
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

function emailRecipe() {
  const recipeName = document.getElementById('recipeName').innerText;
  let body = `${recipeName}%0D%0A%0D%0AIngredients:%0D%0A`;
  document.querySelectorAll('#scaledIngredients li').forEach(item => {
    body += `- ${item.innerText}%0D%0A`;
  });
  window.location.href = `mailto:?subject=Recipe: ${recipeName}&body=${body}`;
}

// YouTube search (kept from original, used by index.html search tab)
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
  if (!query) { hideLoading(); alert('Please enter a search term'); return; }
  try {
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
    const publishedDate = new Date(result.published_date);
    const formattedDate = publishedDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
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

function formatViewCount(viewCount) {
  const count = parseInt(viewCount);
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return count.toString();
}

function useVideo(videoUrl) {
  document.getElementById('youtubeLink').value = videoUrl;
  document.querySelectorAll('.search-tab').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
  document.querySelector('[data-tab="direct-link"]').classList.add('active');
  document.getElementById('direct-link').classList.add('active');
  document.getElementById('thumbnailContainer').innerHTML = '';
  document.getElementById('ingredientsList').innerHTML = '';
  fetchIngredients();
}
