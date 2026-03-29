const API_KEY = 'AIzaSyCtGe8vWQ8-GOlz7SEYd-qq6VMMA-R6LE4'; // Replace with your actual API key

function getVideoId(url) {
  const regExp = /^.*(youtu.be\/|v\/|\/u\/\w\/|embed\/|watch\?v=|&v=|v=)([^#&?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
}

// Show loading spinner
function showLoading() {
  document.getElementById('loading').style.display = 'block';
}

// Hide loading spinner
function hideLoading() {
  document.getElementById('loading').style.display = 'none';
}

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

/**
 * Extract ingredients from YouTube video audio
 * Called when description is not available
 */
async function extractAudioIngredients() {
  const youtubeLink = document.getElementById("youtubeLink").value;

  if (!youtubeLink.trim()) {
    alert('Please enter a valid YouTube Video URL.');
    return;
  }

  // Show extraction stages
  const stagesContainer = document.getElementById('extractionStages');
  if (stagesContainer) {
    stagesContainer.style.display = 'block';
  }

  try {
    // Reset all stages to pending
    updateExtractionStage('downloading', 'pending');
    updateExtractionStage('transcribing', 'pending');
    updateExtractionStage('extracting', 'pending');

    // Call backend API for audio extraction
    const response = await apiClient.extractAudioIngredients(youtubeLink);

    // Mark stages as complete
    updateExtractionStage('downloading', 'complete');
    updateExtractionStage('transcribing', 'complete');
    updateExtractionStage('extracting', 'complete');

    if (response.success && response.ingredients) {
      // Display video title and thumbnail
      displayThumbnail(youtubeLink, response.video_title);

      // Display extracted ingredients
      displayIngredientsList(response.ingredients);

      // Populate scaling dropdown
      populateAvailableIngredients(response.ingredients);

      // Store ingredients in session storage for scaling
      sessionStorage.setItem('currentRecipeIngredients', JSON.stringify(response.ingredients));
      sessionStorage.setItem('youtubeVideoUrl', youtubeLink);

      alert(`✅ Successfully extracted ${response.ingredients.length} ingredients from video audio!`);
    } else {
      alert('Error: Could not extract ingredients from video audio');
    }
  } catch (error) {
    console.error('Error extracting audio ingredients:', error);

    // Mark stages as failed
    updateExtractionStage('downloading', 'error');
    updateExtractionStage('transcribing', 'error');
    updateExtractionStage('extracting', 'error');

    // Show specific error message
    let errorMsg = 'Error extracting ingredients from audio.';
    if (error.message.includes('download')) {
      errorMsg = '❌ Failed to download video audio. Check URL and try again.';
    } else if (error.message.includes('transcrib')) {
      errorMsg = '❌ Unable to transcribe video audio. Audio may be unclear.';
    } else if (error.message.includes('ingredient')) {
      errorMsg = '❌ No ingredients detected in video audio.';
    }

    alert(errorMsg);
  } finally {
    // Hide extraction stages after 3 seconds
    setTimeout(() => {
      const stagesContainer = document.getElementById('extractionStages');
      if (stagesContainer) {
        stagesContainer.style.display = 'none';
      }
    }, 3000);
  }
}

/**
 * Update extraction stage UI
 * @param {string} stageName - Name of stage (downloading, transcribing, extracting)
 * @param {string} status - Status (pending, complete, error)
 */
function updateExtractionStage(stageName, status) {
  const stageElement = document.getElementById(`stage-${stageName}`);
  if (!stageElement) return;

  // Remove previous status classes
  stageElement.classList.remove('pending', 'complete', 'error');
  stageElement.classList.add(status);

  // Update icon based on status
  const icon = stageElement.querySelector('.stage-icon');
  if (icon) {
    switch (status) {
      case 'pending':
        icon.textContent = '⏳';
        break;
      case 'complete':
        icon.textContent = '✅';
        break;
      case 'error':
        icon.textContent = '❌';
        break;
    }
  }
}

function displayThumbnail(thumbnailUrl, videoTitle) {
  const thumbnailContainer = document.getElementById("thumbnailContainer");
  if (thumbnailContainer) {
    thumbnailContainer.innerHTML = "";

    // Create thumbnail image with higher quality
    const img = document.createElement("img");

    // Handle both URL and video title as input
    if (videoTitle.startsWith('http')) {
      img.src = videoTitle; // If second param is URL, use it
    } else {
      img.src = thumbnailUrl;
    }

    img.alt = "YouTube Thumbnail";
    img.loading = "eager"; // Prioritize loading
    thumbnailContainer.appendChild(img);

    // Create recipe title
    const title = document.createElement("p");
    // If videoTitle looks like a title, use it; otherwise get from input
    if (!videoTitle.startsWith('http')) {
      title.innerText = videoTitle;
    } else {
      title.innerText = document.getElementById('youtubeLink').value;
    }
    thumbnailContainer.appendChild(title);

    // Get the YouTube link from the input field
    const youtubeLink = document.getElementById("youtubeLink").value;

    // Create "Watch on YouTube" link with styling moved to CSS
    const linkContainer = document.createElement("div");
    linkContainer.className = "video-source";

    const linkElement = document.createElement("a");
    linkElement.href = youtubeLink;
    linkElement.target = "_blank"; // Open in new tab
    linkElement.innerHTML = '<i class="fab fa-youtube"></i> Watch on YouTube';

    linkContainer.appendChild(linkElement);
    thumbnailContainer.appendChild(linkContainer);
  }
}

// Enhanced ingredient parsing with additional unit support and better recognition
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

    const quantity = ingredient.quantity != null ? ingredient.quantity : 1;
    const unit = ingredient.unit || '';
    const name = ingredient.name || '';

    // Create editable fields so users can adjust them before scaling
    div.innerHTML = `
      <input type="number" class="ingredient-quantity" step="0.1" value="${quantity}" style="width: 60px;">
      <input type="text" class="ingredient-unit" value="${unit}" style="width: 80px;" placeholder="Unit">
      <input type="text" class="ingredient-name" value="${name}" placeholder="Ingredient">
    `;
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

function scaleRecipe() {
  let fetchedIngredientsDiv = document.getElementById("ingredientsList");

  if (fetchedIngredientsDiv && fetchedIngredientsDiv.children.length > 0) {
    // Save notes before scaling (from enter_recipe page)
    if (typeof saveRecipeNotes === 'function') {
      saveRecipeNotes();
    }
    scaleFetchedIngredients();
    return;
  }

  // Save notes first (only if function exists)
  if (typeof saveRecipeNotes === 'function') {
    saveRecipeNotes();
  }

  let recipeName = document.getElementById("recipeName").value.trim();
  let mainIngredient = document.getElementById("mainIngredient").value.trim();
  let scalingOption = document.getElementById("scalingOption").value;
  let scalingValue = parseFloat(document.getElementById("scalingValue").value);

  if (!recipeName || !mainIngredient || isNaN(scalingValue) || scalingValue <= 0) {
    alert("Please enter valid recipe details and scaling value.");
    return;
  }

  let ingredients = document.querySelectorAll(".ingredient-entry");
  let ingredientData = [];

  let mainQuantity = 1;
  ingredients.forEach(ing => {
    let name = ing.querySelector(".ingredient-name").value.trim();
    let quantity = parseFloat(ing.querySelector(".ingredient-quantity").value);
    let unit = ing.querySelector(".ingredient-unit").value.trim();

    if (!name || isNaN(quantity) || quantity <= 0 || !unit) {
      alert("Please enter valid ingredient details.");
      return;
    }

    if (name.toLowerCase() === mainIngredient.toLowerCase()) {
      mainQuantity = quantity;
    }

    ingredientData.push({ name, quantity, unit });
  });

  let scaleFactor = scalingOption === "quantity" ? scalingValue / mainQuantity : scalingValue;

  let scaledIngredients = ingredientData.map(ing => {
    let newQuantity = (ing.quantity * scaleFactor).toFixed(2);
    return `${newQuantity} ${ing.unit} ${ing.name}`;
  });

  sessionStorage.setItem('recipeName', recipeName);
  sessionStorage.setItem('mainIngredient', `Main Ingredient: ${mainIngredient}`);
  sessionStorage.setItem('scaledIngredients', scaledIngredients.join("<br>"));
  sessionStorage.setItem('isManualRecipe', 'true');

  window.location.href = "scaled.html"; // ✅ Fixed: same tab to preserve sessionStorage
}

// Helper function to parse numbers, including simple fractions, mixed numbers, and ranges
function parseQuantity(qtyStr) {
  if (!qtyStr) return 1;

  // Standardize the input by removing double spaces and trimming
  qtyStr = qtyStr.replace(/\s+/g, ' ').trim();

  // Check if it's a range (e.g., "1-2" or "1 to 2")
  if (qtyStr.includes('-') || qtyStr.includes(' to ')) {
    // For ranges, take the average of the two values
    const range = qtyStr.includes('-') ?
      qtyStr.split('-') :
      qtyStr.split(' to ');

    if (range.length === 2) {
      const start = parseFloat(range[0].trim());
      const end = parseFloat(range[1].trim());
      if (!isNaN(start) && !isNaN(end)) {
        return (start + end) / 2; // Return average for scaling
      }
    }
  }

  // Handle mixed numbers like "2 1/2"
  if (qtyStr.includes(' ') && qtyStr.includes('/')) {
    const parts = qtyStr.split(' ');
    if (parts.length === 2) {
      const wholeNumber = parseFloat(parts[0]);
      // Check if the second part is a fraction
      if (parts[1].includes('/')) {
        const fractionParts = parts[1].split('/');
        if (fractionParts.length === 2) {
          const numerator = parseFloat(fractionParts[0]);
          const denominator = parseFloat(fractionParts[1]);
          if (!isNaN(wholeNumber) && !isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
            return wholeNumber + (numerator / denominator);
          }
        }
      }
    }
  }

  // Handle simple fractions
  if (qtyStr.includes('/')) {
    const parts = qtyStr.split('/');
    if (parts.length === 2 && !isNaN(parseFloat(parts[0])) && !isNaN(parseFloat(parts[1])) && parseFloat(parts[1]) !== 0) {
      return parseFloat(parts[0]) / parseFloat(parts[1]);
    }
  }

  const num = parseFloat(qtyStr);
  return isNaN(num) ? 1 : num;
}

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

    // Build ingredients list from current display using the structured inputs
    const ingredients = Array.from(ingredientElements).map((ing, index) => ({
      name: ing.querySelector(".ingredient-name").value.trim(),
      quantity: parseFloat(ing.querySelector(".ingredient-quantity").value) || 1,
      unit: ing.querySelector(".ingredient-unit").value.trim()
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
/*
      name: ingredientName, 
      quantity: originalQuantity, 
      unit,
      isRange,
      rangeText
    });
    
  });*/

let scaledIngredients = ingredientData.map(ing => {
  // Check if quantity is valid before scaling
  if (isNaN(ing.quantity)) {
    console.warn("Invalid quantity found for:", ing.name);
    return ing.name; // Return just the name if quantity is invalid
  }

  // Handle ranges specially
  if (ing.isRange && ing.rangeText) {
    // Parse the range and scale each number
    const rangeMatch = ing.rangeText.match(/([\d.\/]+)\s*[-to]+\s*([\d.\/]+)/i);
    if (rangeMatch && rangeMatch.length === 3) {
      const start = parseQuantity(rangeMatch[1]);
      const end = parseQuantity(rangeMatch[2]);

      // Scale both numbers
      const scaledStart = (start * scalingValue);
      const scaledEnd = (end * scalingValue);

      // Format the scaled range
      const formattedStart = formatQuantity(scaledStart);
      const formattedEnd = formatQuantity(scaledEnd);

      // Only add unit if it exists
      const unitString = ing.unit ? ` ${ing.unit}` : '';
      return `${formattedStart}-${formattedEnd}${unitString} ${ing.name}`;
    }
  }

  // Normal quantity scaling
  let newQuantity = (ing.quantity * scalingValue);
  let displayQuantity = formatQuantity(newQuantity);

  // Only add unit if it exists
  const unitString = ing.unit ? ` ${ing.unit}` : '';
  return `${displayQuantity}${unitString} ${ing.name}`;
});

// If something went wrong and we have no ingredients, show an error
if (scaledIngredients.length === 0) {
  alert("Failed to scale ingredients. Please try again with a different video.");
  return;
}

// Make sure we have a valid title (using the existing titleElement from above)
const finalTitle = (titleElement && titleElement.innerText) ?
  titleElement.innerText :
  (videoTitle || "Scaled Recipe");

// Store the results in session storage for the scaled page
sessionStorage.setItem('recipeName', finalTitle);
sessionStorage.setItem('mainIngredient', '');
sessionStorage.setItem('scaledIngredients', scaledIngredients.join("<br>"));
sessionStorage.setItem('youtubeVideoUrl', youtubeLink);
sessionStorage.setItem('isManualRecipe', 'false');

window.location.href = "scaled.html";
}

// Helper function to format quantities nicely using proper cooking fractions
function formatQuantity(quantity) {
  if (!quantity) return "";

  // Handle common fractions directly with unicode
  if (Math.abs(quantity - 0.5) < 0.01) return "½";
  if (Math.abs(quantity - 0.25) < 0.01) return "¼";
  if (Math.abs(quantity - 0.75) < 0.01) return "¾";
  if (Math.abs(quantity - 0.33) < 0.01) return "⅓";
  if (Math.abs(quantity - 0.67) < 0.01) return "⅔";

  // Basic fraction conversion for mixed numbers
  if (quantity > 1) {
    if (Math.abs((quantity % 1) - 0.5) < 0.01) return `${Math.floor(quantity)} ½`;
    if (Math.abs((quantity % 1) - 0.25) < 0.01) return `${Math.floor(quantity)} ¼`;
    if (Math.abs((quantity % 1) - 0.75) < 0.01) return `${Math.floor(quantity)} ¾`;
    if (Math.abs((quantity % 1) - 0.33) < 0.01) return `${Math.floor(quantity)} ⅓`;
    if (Math.abs((quantity % 1) - 0.67) < 0.01) return `${Math.floor(quantity)} ⅔`;
  }

  // For whole numbers, don't show decimal places
  if (quantity % 1 === 0) return quantity.toString();

  // Use decimal representation if no precise fraction match, capped at 2 trailing units
  return parseFloat(quantity.toFixed(2)).toString();
}

// Update scaling options based on selected scaling method
function updateScalingOptions() {
  const scalingOption = document.getElementById("scalingOption").value;

  // Hide all scaling methods first
  document.querySelectorAll('.scaling-method').forEach(el => {
    el.style.display = 'none';
  });

  // Show the selected scaling method
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

// Save recipe to local storage
function saveRecipe() {
  const recipeName = document.getElementById('recipeName').innerText;
  const mainIngredient = document.getElementById('mainIngredient').innerText;
  const ingredients = [];

  // Get ingredients from the list
  const ingredientItems = document.querySelectorAll('#scaledIngredients li');
  ingredientItems.forEach(item => {
    ingredients.push(item.innerText);
  });

  // Get YouTube link if available
  const youtubeLink = sessionStorage.getItem('youtubeVideoUrl') || '';

  const recipe = {
    id: Date.now().toString(),
    name: recipeName,
    mainIngredient,
    ingredients,
    youtubeLink,
    savedDate: new Date().toISOString()
  };

  // Get existing recipes from localStorage
  let savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];

  // Add new recipe
  savedRecipes.push(recipe);

  // Save back to localStorage
  localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));

  alert('Recipe saved successfully!');
}

// Load saved recipes
function loadSavedRecipes() {
  const savedRecipesContainer = document.getElementById('saved-recipes');
  const savedRecipesList = document.getElementById('saved-recipes-list');

  if (!savedRecipesContainer || !savedRecipesList) return;

  // Get recipes from localStorage
  const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];

  if (savedRecipes.length === 0) {
    savedRecipesContainer.style.display = 'none';
    return;
  }

  savedRecipesContainer.style.display = 'block';
  savedRecipesList.innerHTML = '';

  // Display each saved recipe
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

// Load a specific recipe
function loadRecipe(recipeId) {
  const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  const recipe = savedRecipes.find(r => r.id === recipeId);

  if (recipe) {
    sessionStorage.setItem('recipeName', recipe.name);
    sessionStorage.setItem('mainIngredient', recipe.mainIngredient);
    sessionStorage.setItem('scaledIngredients', recipe.ingredients.join('<br>'));

    if (recipe.youtubeLink) {
      sessionStorage.setItem('youtubeVideoUrl', recipe.youtubeLink);
    }

    window.location.href = 'scaled.html';
  }
}

// Delete a recipe
function deleteRecipe(recipeId) {
  if (confirm('Are you sure you want to delete this recipe?')) {
    let savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
    savedRecipes = savedRecipes.filter(r => r.id !== recipeId);
    localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));
    loadSavedRecipes();
  }
}

// Print recipe
function printRecipe() {
  window.print();
}

// Export recipe as PDF
function exportPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  const recipeName = document.getElementById('recipeName').innerText;
  const mainIngredient = document.getElementById('mainIngredient').innerText;
  const ingredients = [];

  // Get ingredients from the list
  const ingredientItems = document.querySelectorAll('#scaledIngredients li');
  ingredientItems.forEach(item => {
    ingredients.push(item.innerText);
  });

  // Add content to PDF
  doc.setFontSize(18);
  doc.text(recipeName, 20, 20);

  doc.setFontSize(12);
  doc.text(mainIngredient, 20, 30);

  doc.setFontSize(14);
  doc.text('Ingredients:', 20, 40);

  let y = 50;
  ingredients.forEach(ingredient => {
    doc.setFontSize(12);
    doc.text('• ' + ingredient, 25, y);
    y += 10;

    // Add new page if needed
    if (y > 280) {
      doc.addPage();
      y = 20;
    }
  });

  // Save the PDF
  doc.save(`${recipeName.replace(/\s+/g, '_')}.pdf`);
}

// Export recipe as text
function exportText() {
  const recipeName = document.getElementById('recipeName').innerText;
  const mainIngredient = document.getElementById('mainIngredient').innerText;
  const ingredients = [];

  // Get ingredients from the list
  const ingredientItems = document.querySelectorAll('#scaledIngredients li');
  ingredientItems.forEach(item => {
    ingredients.push(item.innerText);
  });

  // Create text content
  let content = `${recipeName}\n\n`;
  content += `${mainIngredient}\n\n`;
  content += `Ingredients:\n`;
  ingredients.forEach(ingredient => {
    content += `- ${ingredient}\n`;
  });

  // Create a download link
  const element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
  element.setAttribute('download', `${recipeName.replace(/\s+/g, '_')}.txt`);
  element.style.display = 'none';

  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

// Send recipe via email
function emailRecipe() {
  const recipeName = document.getElementById('recipeName').innerText;
  const mainIngredient = document.getElementById('mainIngredient').innerText;
  const ingredients = [];

  // Get ingredients from the list
  const ingredientItems = document.querySelectorAll('#scaledIngredients li');
  ingredientItems.forEach(item => {
    ingredients.push(item.innerText);
  });

  // Create email body
  let body = `${recipeName}%0D%0A%0D%0A`;
  body += `${mainIngredient}%0D%0A%0D%0A`;
  body += `Ingredients:%0D%0A`;
  ingredients.forEach(ingredient => {
    body += `- ${ingredient}%0D%0A`;
  });

  // Open email client
  window.location.href = `mailto:?subject=Recipe: ${recipeName}&body=${body}`;
}

// YouTube search functionality
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

// Filter search results to exclude shorts and prefer videos with ingredients in description
function filterSearchResults(searchItems, videoItems) {
  if (!videoItems || videoItems.length === 0) return [];

  // Keywords that suggest a video description might contain ingredients
  const ingredientKeywords = [
    'ingredient', 'ingredients', 'recipe', 'cup', 'tablespoon', 'teaspoon',
    'gram', 'oz', 'pound', 'ml', 'liter', 'kg'
  ];

  // Score and rank videos
  const scoredVideos = searchItems.map(searchItem => {
    const videoId = searchItem.id.videoId;
    const videoDetail = videoItems.find(v => v.id === videoId);

    if (!videoDetail) return { searchItem, score: 0 };

    // Check if it's not a short video
    const isShort = isYoutubeShort(videoDetail);
    if (isShort) return { searchItem, score: -100 }; // Give shorts a very low score

    let score = 0;

    // Check description for ingredient-related keywords
    const description = videoDetail.snippet.description.toLowerCase();

    ingredientKeywords.forEach(keyword => {
      if (description.includes(keyword)) {
        score += 5;
      }
    });

    // Check if description likely contains ingredient list (lines with measurements)
    const lines = description.split('\n');
    const potentialIngredientLines = lines.filter(line => {
      // Look for lines that might be ingredients
      const hasNumbers = /\d+/.test(line);
      const hasUnits = /(cup|tbsp|tsp|tablespoon|teaspoon|gram|g|oz|pound|lb|ml|l)s?\b/i.test(line);
      return hasNumbers && hasUnits;
    });

    // Boost score based on potential ingredient lines
    score += potentialIngredientLines.length * 3;

    // Longer videos are preferred (less likely to be shorts)
    const duration = videoDetail.contentDetails.duration;
    const durationInSeconds = parseDuration(duration);

    if (durationInSeconds > 180) score += 10; // Prefer videos > 3 minutes
    if (durationInSeconds < 90) score -= 5;  // Penalize very short videos

    return { searchItem, score };
  });

  // Sort by score (highest first) and return the search items
  return scoredVideos
    .sort((a, b) => b.score - a.score)
    .map(item => item.searchItem);
}

// Helper function to check if a video is a YouTube Short
function isYoutubeShort(videoDetail) {
  if (!videoDetail) return false;

  // Check if title contains #shorts
  const hasShortHashtag = videoDetail.snippet.title.toLowerCase().includes('#short');

  // Check aspect ratio (shorts are typically vertical)
  // YouTube doesn't expose aspect ratio directly, but shorts are typically < 60 seconds
  const duration = videoDetail.contentDetails.duration;
  const durationInSeconds = parseDuration(duration);
  const isShortDuration = durationInSeconds < 60;

  // Check description for shorts indicators
  const description = videoDetail.snippet.description.toLowerCase();
  const hasShortInDescription = description.includes('#short');

  return (hasShortHashtag || hasShortInDescription || (isShortDuration && (hasShortHashtag || hasShortInDescription)));
}

// Parse ISO 8601 duration format (PT1H2M3S) to seconds
function parseDuration(duration) {
  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  const hours = parseInt(match[1] || 0, 10);
  const minutes = parseInt(match[2] || 0, 10);
  const seconds = parseInt(match[3] || 0, 10);

  return hours * 3600 + minutes * 60 + seconds;
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
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  } else if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
}

function useVideo(videoUrl) {
  document.getElementById('youtubeLink').value = videoUrl;

  // Switch to direct link tab
  document.querySelectorAll('.search-tab').forEach(tab => {
    tab.classList.remove('active');
  });
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.remove('active');
  });

  document.querySelector('[data-tab="direct-link"]').classList.add('active');
  document.getElementById('direct-link').classList.add('active');

  // Clear any previous ingredients and thumbnails
  document.getElementById('thumbnailContainer').innerHTML = '';
  document.getElementById('ingredientsList').innerHTML = '';

  // Fetch ingredients automatically
  fetchIngredients();
}

// ============================================================================
// INTEGRATION WITH RECIPE ENHANCEMENTS
// ============================================================================

// Enhanced scaleRecipe with notes integration
function scaleRecipeWithNotes() {
  // Save notes before scaling
  saveRecipeNotes();

  // Call original scale function
  scaleRecipe();
}

// Update the ingredient entry display with categorization
function parseIngredientsWithCategorization(description) {
  const units = [
    'cup', 'cups', 'teaspoon', 'teaspoons', 'tablespoon', 'tablespoons',
    'tbsp', 'tsp', 'gram', 'grams', 'g', 'kg', 'kilogram', 'kilograms',
    'ounce', 'ounces', 'oz', 'lb', 'pound', 'pounds', 'ml', 'milliliter',
    'milliliters', 'liter', 'liters', 'l', 'dash', 'pinch', 'handful',
    'clove', 'cloves', 'bunch', 'can', 'cans', 'jar', 'jars', 'slice', 'slices'
  ];

  const unnecessaryKeywords = [
    'degree', 'minutes', 'oven', 'preheat', 'temperature', 'time',
    'instagram', 'http', 'https', 'video', 'subscribe', 'cook', 'cooking',
    'yield', 'serves', 'servings', 'written', 'follow', 'comment', 'like'
  ];

  const instructionIndicators = [
    'stir', 'mix', 'combine', 'heat', 'add', 'put', 'place', 'rub', 'coat',
    'sprinkle', 'bake', 'boil', 'simmer', 'chop', 'dice', 'slice', 'prepare',
    'wash', 'clean', 'drain', 'strain', 'grill', 'broil', 'season', 'marinate',
    'rest', 'cool', 'chill', 'refrigerate', 'store', 'pour', 'transfer',
    'remove', 'discard', 'serve', 'garnish', 'top', 'arrange', 'assemble',
    'until', 'when', 'while', 'then', 'next', 'step', 'repeat', 'continue'
  ];

  const lines = description.split('\n');

  let startLine = -1;
  let endLine = lines.length;

  for (let i = 0; i < lines.length; i++) {
    const lowerLine = lines[i].toLowerCase();
    if (lowerLine.includes('ingredient') && lowerLine.endsWith(':')) {
      startLine = i + 1;
    }
    if (startLine >= 0 && (lowerLine.includes('instruction') || lowerLine.includes('direction'))) {
      endLine = i;
      break;
    }
  }

  const ingredientRange = startLine >= 0 ? lines.slice(startLine, endLine) : lines;

  const ingredients = ingredientRange.filter(line => {
    const lowerLine = line.toLowerCase().trim();
    if (lowerLine.length < 3) return false;
    if (/^[-*=]{5,}$/.test(lowerLine)) return false;
    if (unnecessaryKeywords.some(keyword => lowerLine.includes(keyword))) return false;
    if (/^\d+\./.test(lowerLine)) return false;
    if (instructionIndicators.some(indicator => {
      const withoutNumbersPrefix = lowerLine.replace(/^[\d\s\.]+/, '').trim();
      return withoutNumbersPrefix.startsWith(indicator);
    })) return false;
    if (lowerLine.split(' ').length > 10 && !lowerLine.includes(',')) return false;

    const hasUnit = units.some(unit => {
      const regex = new RegExp(`\\b${unit}\\b`, 'i');
      return regex.test(lowerLine);
    });
    const startsWithNumber = /^\d+[\d\/\.\s]*/.test(lowerLine);
    const hasBulletPoint = /^[-•*]/.test(lowerLine);

    return hasUnit || startsWithNumber || hasBulletPoint;
  });

  return ingredients;
}

