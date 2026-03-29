document.addEventListener('DOMContentLoaded', function () {
  let recipeName = sessionStorage.getItem('recipeName');
  let mainIngredient = sessionStorage.getItem('mainIngredient');
  let scaledIngredients = sessionStorage.getItem('scaledIngredients');
  let youtubeVideoUrl = sessionStorage.getItem('youtubeVideoUrl');
  let isManualRecipe = sessionStorage.getItem('isManualRecipe');

  if (recipeName && scaledIngredients) {
    document.getElementById('recipeName').innerText = recipeName;
    document.getElementById('mainIngredient').innerText = mainIngredient;

    let lines;
    try {
      lines = JSON.parse(scaledIngredients) || [];
    } catch (e) {
      // fallback to old <br> format
      lines = scaledIngredients.split('<br>').filter(Boolean);
    }

    const ul = document.getElementById('scaledIngredients');
    ul.innerHTML = '';
    lines.forEach(line => {
      // Skip lines that are just separators (like lots of dashes)
      if (/^[-*=]{5,}$/.test(line.trim())) return;
      
      const li = document.createElement('li');
      li.textContent = line.trim();
      li.style.cursor = 'pointer';
      li.style.padding = '8px';
      li.style.borderRadius = '4px';
      li.style.transition = 'all 0.3s ease';
      
      // Make editable on click
      li.addEventListener('click', function() {
        if (this.querySelector('input')) return;
        const originalText = this.textContent;
        const input = document.createElement('input');
        input.type = 'text';
        input.value = originalText;
        input.style.width = '100%';
        input.style.padding = '8px';
        input.style.border = '2px solid #D96B43';
        input.style.borderRadius = '4px';
        input.style.fontSize = '16px';
        
        this.textContent = '';
        this.appendChild(input);
        input.focus();
        input.select();
        
        const saveEdit = () => {
          const newValue = input.value.trim();
          this.textContent = newValue;
          sessionStorage.setItem(`li_${lines.indexOf(line)}`, newValue);
        };
        
        input.addEventListener('blur', saveEdit);
        input.addEventListener('keypress', (e) => {
          if (e.key === 'Enter') saveEdit();
        });
      });
      
      ul.appendChild(li);
    });

    // Load stored edits
    const stored = sessionStorage.getItem('editedIngredients');
    if (stored) {
      const edits = JSON.parse(stored);
      ul.querySelectorAll('li').forEach((li, idx) => {
        if (edits[idx]) li.textContent = edits[idx];
      });
    }

    // Add YouTube video link only if it's not a manually entered recipe
    if (youtubeVideoUrl && isManualRecipe !== 'true') {
      const sourceDiv = document.createElement('div');
      sourceDiv.className = 'video-source';
      sourceDiv.innerHTML = `
        <p>Original Recipe: 
          <a href="${youtubeVideoUrl}" target="_blank">Watch on YouTube</a>
        </p>
      `;
      
      // Insert after main ingredient
      const mainIngredientElement = document.getElementById('mainIngredient');
      if (mainIngredientElement.nextSibling) {
        mainIngredientElement.parentNode.insertBefore(sourceDiv, mainIngredientElement.nextSibling);
      } else {
        mainIngredientElement.parentNode.appendChild(sourceDiv);
      }
    }
    
    // Display recipe notes if available
    displayRecipeNotes();
  } else {
    document.getElementById('recipeName').innerText = "No Recipe";
    document.getElementById('mainIngredient').innerText = "N/A";
    document.getElementById('scaledIngredients').innerHTML = '<li>No scaled recipe found. Please return to the main page and scale your recipe again.</li>';
  }
});

// Display recipe notes and instructions
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
    notesDiv.innerHTML = `
      <h3>📝 Cooking Notes</h3>
      <p>${notes.replace(/\n/g, '<br>')}</p>
    `;
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

// Save recipe to local storage
function saveRecipeWithNotes() {
  const recipeName = document.getElementById('recipeName').innerText;
  const mainIngredient = document.getElementById('mainIngredient').innerText;
  const ingredients = [];
  
  // Get ingredients from the list
  const ingredientItems = document.querySelectorAll('#scaledIngredients li');
  ingredientItems.forEach(item => {
    ingredients.push(item.innerText);
  });
  
  // Get notes and steps
  const notes = sessionStorage.getItem('recipeNotes') || '';
  const stepsJson = sessionStorage.getItem('recipeSteps') || '[]';
  
  // Get YouTube link if available
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
  
  // Get existing recipes from localStorage
  let savedRecipes = JSON.parse(localStorage.getItem('savedRecipes')) || [];
  
  // Add new recipe
  savedRecipes.push(recipe);
  
  // Save back to localStorage
  localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));
  
  alert('Recipe saved successfully!');
}

// Save recipe to local storage (old function for backward compatibility)
function saveRecipe() {
  saveRecipeWithNotes();
}

// Return to the scaling UI with current recipe data
function modifyScaling() {
  // Store current recipe state in sessionStorage with a special flag
  sessionStorage.setItem('modifyingRecipe', 'true');
  // The other data (recipeName, scaledIngredients, youtubeVideoUrl) is already in sessionStorage
  
  // Navigate back to the main page
  window.location.href = 'index.html';
}

// Print recipe
function printRecipe() {
  window.print();
}

// Export recipe as PDF
function exportPDFWithNotes() {
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
  
  // Get notes and steps
  const notes = sessionStorage.getItem('recipeNotes');
  const stepsJson = sessionStorage.getItem('recipeSteps');
  const steps = stepsJson ? JSON.parse(stepsJson) : [];
  
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
    
    if (y > 250) {
      doc.addPage();
      y = 20;
    }
  });
  
  // Add notes if available
  if (notes) {
    y += 10;
    if (y > 250) {
      doc.addPage();
      y = 20;
    }
    doc.setFontSize(14);
    doc.text('Cooking Notes:', 20, y);
    y += 10;
    
    doc.setFontSize(12);
    const noteLines = doc.splitTextToSize(notes, 170);
    noteLines.forEach(line => {
      if (y > 250) {
        doc.addPage();
        y = 20;
      }
      doc.text(line, 25, y);
      y += 10;
    });
  }
  
  // Add instructions if available
  if (steps.length > 0) {
    y += 10;
    if (y > 250) {
      doc.addPage();
      y = 20;
    }
    doc.setFontSize(14);
    doc.text('Instructions:', 20, y);
    y += 10;
    
    doc.setFontSize(12);
    steps.forEach((step, index) => {
      if (step.trim()) {
        if (y > 250) {
          doc.addPage();
          y = 20;
        }
        doc.text(`${index + 1}. ${step}`, 25, y);
        y += 10;
      }
    });
  }
  
  // Save the PDF
  doc.save(`${recipeName.replace(/\s+/g, '_')}.pdf`);
}

// Export recipe as PDF (old function for backward compatibility)
function exportPDF() {
  exportPDFWithNotes();
}

// Export recipe as text
function exportTextWithNotes() {
  const recipeName = document.getElementById('recipeName').innerText;
  const mainIngredient = document.getElementById('mainIngredient').innerText;
  const ingredients = [];
  
  // Get ingredients from the list
  const ingredientItems = document.querySelectorAll('#scaledIngredients li');
  ingredientItems.forEach(item => {
    ingredients.push(item.innerText);
  });
  
  // Get notes and steps
  const notes = sessionStorage.getItem('recipeNotes');
  const stepsJson = sessionStorage.getItem('recipeSteps');
  const steps = stepsJson ? JSON.parse(stepsJson) : [];
  
  // Create text content
  let content = `${recipeName}\n\n`;
  content += `${mainIngredient}\n\n`;
  content += `Ingredients:\n`;
  ingredients.forEach(ingredient => {
    content += `- ${ingredient}\n`;
  });
  
  if (notes) {
    content += `\nCooking Notes:\n${notes}\n`;
  }
  
  if (steps.length > 0) {
    content += `\nInstructions:\n`;
    steps.forEach((step, index) => {
      if (step.trim()) {
        content += `${index + 1}. ${step}\n`;
      }
    });
  }
  
  // Create a download link
  const element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
  element.setAttribute('download', `${recipeName.replace(/\s+/g, '_')}.txt`);
  element.style.display = 'none';
  
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

// Export recipe as text (old function for backward compatibility)
function exportText() {
  exportTextWithNotes();
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

// ============================================================================
// UNIT CONVERSION FEATURE
// ============================================================================

const unitConversionMap = {
  // Weight conversions
  'gram': { 'oz': 0.035274, 'lb': 0.00220462 },
  'g': { 'oz': 0.035274, 'lb': 0.00220462 },
  'kg': { 'oz': 35.274, 'lb': 2.20462 },
  'oz': { 'gram': 28.3495, 'g': 28.3495, 'kg': 0.0283495 },
  'lb': { 'gram': 453.592, 'g': 453.592, 'kg': 0.453592 },
  
  // Volume conversions
  'ml': { 'cup': 0.00423344, 'tbsp': 0.067628, 'tsp': 0.202884, 'oz': 0.033814 },
  'l': { 'cup': 4.22675, 'tbsp': 67.628, 'tsp': 202.884, 'oz': 33.814 },
  'liter': { 'cup': 4.22675, 'tbsp': 67.628, 'tsp': 202.884, 'oz': 33.814 },
  'cup': { 'ml': 236.588, 'tbsp': 16, 'tsp': 48, 'oz': 8 },
  'cups': { 'ml': 236.588, 'tbsp': 16, 'tsp': 48, 'oz': 8 },
  'tbsp': { 'ml': 14.7868, 'cup': 0.0625, 'tsp': 3, 'oz': 0.5 },
  'tsp': { 'ml': 4.92892, 'cup': 0.0208333, 'tbsp': 0.333333, 'oz': 0.166667 },
  'oz': { 'ml': 29.5735, 'l': 0.0295735, 'cup': 0.125, 'tbsp': 2, 'tsp': 6 }
};

function convertUnit(quantity, fromUnit, toUnit) {
  if (fromUnit === toUnit) return quantity;
  
  const normalizedFrom = fromUnit.toLowerCase();
  const normalizedTo = toUnit.toLowerCase();
  
  if (unitConversionMap[normalizedFrom] && unitConversionMap[normalizedFrom][normalizedTo]) {
    return quantity * unitConversionMap[normalizedFrom][normalizedTo];
  }
  
  return quantity;
}

function parseIngredientForConversion(ingredientStr) {
  // Extract quantity and unit from ingredient string like "2 cups flour"
  const match = ingredientStr.match(/^([\d.,\s\/]+)\s*(\w+)\s+(.*)$/);
  
  if (match) {
    return {
      quantity: parseFloat(match[1].replace(/,/g, '')) || 1,
      unit: match[2],
      name: match[3]
    };
  }
  
  return { quantity: 1, unit: '', name: ingredientStr };
}

function formatConvertedIngredient(quantity, unit, name) {
  // Format quantity nicely
  let formatted;
  if (quantity % 1 === 0) {
    formatted = quantity.toString();
  } else {
    formatted = quantity.toFixed(2).replace(/\.?0+$/, '');
  }
  
  return `${formatted} ${unit} ${name}`.trim();
}

function switchUnitSystem(system) {
  const ul = document.getElementById('scaledIngredients');
  if (!ul) return;
  
  const items = ul.querySelectorAll('li');
  const originalIngredients = sessionStorage.getItem('scaledIngredients_original');
  
  // Store original if not already stored
  if (!originalIngredients) {
    const originals = [];
    items.forEach(item => {
      originals.push(item.textContent);
    });
    sessionStorage.setItem('scaledIngredients_original', JSON.stringify(originals));
  }
  
  if (system === 'original') {
    // Restore original ingredients
    if (originalIngredients) {
      const originals = JSON.parse(originalIngredients);
      items.forEach((item, index) => {
        if (originals[index]) {
          item.textContent = originals[index];
        }
      });
    }
  } else if (system === 'metric') {
    const originals = originalIngredients ? JSON.parse(originalIngredients) : [];
    items.forEach((item, index) => {
      const original = originals[index] || item.textContent;
      const parsed = parseIngredientForConversion(original);
      
      // Only convert if we recognize the unit
      if (parsed.unit && unitConversionMap[parsed.unit.toLowerCase()]) {
        // Convert to metric
        let newUnit = parsed.unit;
        let newQuantity = parsed.quantity;
        
        if (['oz', 'cup', 'cups', 'tbsp', 'tsp'].includes(newUnit.toLowerCase())) {
          newUnit = 'ml';
          newQuantity = convertUnit(newQuantity, parsed.unit, newUnit);
        } else if (['lb'].includes(newUnit.toLowerCase())) {
          newUnit = 'g';
          newQuantity = convertUnit(newQuantity, parsed.unit, newUnit);
        }
        
        item.textContent = formatConvertedIngredient(newQuantity, newUnit, parsed.name);
      }
    });
  } else if (system === 'imperial') {
    const originals = originalIngredients ? JSON.parse(originalIngredients) : [];
    items.forEach((item, index) => {
      const original = originals[index] || item.textContent;
      const parsed = parseIngredientForConversion(original);
      
      if (parsed.unit && unitConversionMap[parsed.unit.toLowerCase()]) {
        // Convert to imperial
        let newUnit = parsed.unit;
        let newQuantity = parsed.quantity;
        
        if (['ml', 'l', 'liter'].includes(newUnit.toLowerCase())) {
          newUnit = 'cup';
          newQuantity = convertUnit(newQuantity, parsed.unit, newUnit);
        } else if (['g', 'kg'].includes(newUnit.toLowerCase())) {
          newUnit = 'oz';
          newQuantity = convertUnit(newQuantity, parsed.unit, newUnit);
        }
        
        item.textContent = formatConvertedIngredient(newQuantity, newUnit, parsed.name);
      }
    });
  }
}

