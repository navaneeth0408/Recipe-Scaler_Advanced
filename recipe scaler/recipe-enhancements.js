// ============================================================================
// RECIPE SCALER ENHANCEMENTS
// Features: Categorization, Unit Conversion, Editable Output, Duplicate
// Detection, Recipe Notes & Instructions
// ============================================================================

// ============================================================================
// 1. INGREDIENT CATEGORIZATION
// ============================================================================

const ingredientCategories = {
  spices: [
    'salt', 'pepper', 'paprika', 'cumin', 'chili', 'curry', 'basil', 'oregano',
    'thyme', 'rosemary', 'garlic', 'ginger', 'cinnamon', 'nutmeg', 'cloves',
    'cardamom', 'turmeric', 'coriander', 'fennel', 'caraway', 'dill', 'parsley',
    'cilantro', 'sage', 'chives', 'mint', 'vanilla', 'allspice', 'peppercorn'
  ],
  liquids: [
    'water', 'milk', 'cream', 'juice', 'wine', 'beer', 'stock', 'broth',
    'vinegar', 'oil', 'olive oil', 'butter', 'honey', 'syrup', 'sauce',
    'yogurt', 'sour cream', 'coconut milk', 'almond milk', 'beef broth',
    'chicken broth', 'vegetable broth', 'coffee', 'tea', 'lemon juice',
    'lime juice', 'soy sauce', 'worcestershire'
  ],
  proteins: [
    'chicken', 'beef', 'pork', 'lamb', 'turkey', 'fish', 'salmon', 'tuna',
    'shrimp', 'prawn', 'egg', 'eggs', 'tofu', 'tempeh', 'bean', 'beans',
    'lentil', 'lentils', 'chickpea', 'chickpeas', 'meat', 'steak', 'ground'
  ],
  garnish: [
    'garnish', 'chopped', 'fresh', 'green', 'parmesan', 'cheese', 'breadcrumb',
    'lime', 'lemon', 'coriander', 'cilantro', 'parsley', 'mint', 'basil',
    'scallion', 'chive', 'sesame', 'seeds', 'nut', 'nuts', 'almond', 'peanut'
  ]
};

function categorizeIngredient(ingredientName) {
  const lower = ingredientName.toLowerCase();

  for (const [category, keywords] of Object.entries(ingredientCategories)) {
    if (keywords.some(keyword => lower.includes(keyword))) {
      return category;
    }
  }

  return 'main'; // Default category for main ingredients
}

function groupIngredientsByCategory(ingredients) {
  const grouped = {
    main: [],
    spices: [],
    liquids: [],
    proteins: [],
    garnish: []
  };

  ingredients.forEach(ingredient => {
    const category = categorizeIngredient(ingredient.name || ingredient);
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(ingredient);
  });

  return grouped;
}

function displayCategorizedIngredients(ingredientsList) {
  const container = document.getElementById('ingredientsList') || document.getElementById('scaledIngredients');
  if (!container) return;

  // Parse ingredients if they're strings
  const parsedIngredients = typeof ingredientsList[0] === 'string'
    ? ingredientsList.map(ing => ({ name: ing, full: ing }))
    : ingredientsList;

  const grouped = groupIngredientsByCategory(parsedIngredients);

  container.innerHTML = '';

  const categoryLabels = {
    main: '🥘 Main Ingredients',
    spices: '🧂 Spices & Seasonings',
    liquids: '💧 Liquids',
    proteins: '🍗 Proteins',
    garnish: '✨ Garnish & Toppings'
  };

  Object.entries(grouped).forEach(([category, items]) => {
    if (items.length === 0) return;

    const section = document.createElement('div');
    section.className = `ingredient-category-section`;

    const header = document.createElement('h3');
    header.className = 'category-header';
    header.textContent = categoryLabels[category] || category;
    section.appendChild(header);

    const list = document.createElement('div');
    list.className = 'category-ingredients';

    items.forEach(item => {
      const div = document.createElement('div');
      div.className = 'ingredient-entry category-item';
      const ingredient = item.full || item.name || item;
      div.innerHTML = `<input type="text" value="${ingredient}" readonly class="ingredient-name">`;
      list.appendChild(div);
    });

    section.appendChild(list);
    container.appendChild(section);
  });
}

// ============================================================================
// 2. UNIT CONVERSION
// ============================================================================

const unitConversions = {
  metric: {
    gram: 1,
    ml: 1,
    liter: 1000,
    kg: 1000
  },
  imperial: {
    oz: 1,
    cup: 1,
    tbsp: 1,
    tsp: 1,
    lb: 16
  }
};

const unitConversionMapEnh = {
  // Weight conversions
  'gram': { 'oz': 0.035274, 'lb': 0.00220462 },
  'kg': { 'oz': 35.274, 'lb': 2.20462 },
  'oz': { 'gram': 28.3495, 'kg': 0.0283495 },
  'lb': { 'gram': 453.592, 'kg': 0.453592 },

  // Volume conversions
  'ml': { 'cup': 0.00423344, 'tbsp': 0.067628, 'tsp': 0.202884, 'oz': 0.033814 },
  'liter': { 'cup': 4.22675, 'tbsp': 67.628, 'tsp': 202.884, 'oz': 33.814 },
  'cup': { 'ml': 236.588, 'tbsp': 16, 'tsp': 48, 'oz': 8 },
  'tbsp': { 'ml': 14.7868, 'cup': 0.0625, 'tsp': 3, 'oz': 0.5 },
  'tsp': { 'ml': 4.92892, 'cup': 0.0208333, 'tbsp': 0.333333, 'oz': 0.166667 },
  'oz': { 'ml': 29.5735, 'liter': 0.0295735, 'cup': 0.125, 'tbsp': 2, 'tsp': 6 }
};

function convertUnit(quantity, fromUnit, toUnit) {
  if (fromUnit === toUnit) return quantity;

  if (unitConversionMapEnh[fromUnit] && unitConversionMapEnh[fromUnit][toUnit]) {
    return quantity * unitConversionMapEnh[fromUnit][toUnit];
  }

  return quantity; // Return unchanged if no conversion available
}

function parseIngredientWithUnit(ingredientStr) {
  // Extract quantity and unit from ingredient string like "2 cups flour"
  const match = ingredientStr.match(/^([\d.\/\s-]+)\s*(\w+)\s+(.*)$/);

  if (match) {
    return {
      quantity: match[1].trim(),
      unit: match[2].toLowerCase(),
      name: match[3]
    };
  }

  return {
    quantity: '',
    unit: '',
    name: ingredientStr
  };
}

function formatIngredientWithUnit(quantity, unit, name) {
  const formattedQty = parseFloat(quantity).toFixed(2).replace(/\.?0+$/, '');
  return `${formattedQty} ${unit} ${name}`.trim();
}

function toggleUnitSystem(ingredients, targetSystem) {
  // targetSystem: 'metric' or 'imperial'
  return ingredients.map(ingredient => {
    const parsed = parseIngredientWithUnit(ingredient);

    if (!parsed.unit) return ingredient;

    const fromUnit = parsed.unit.toLowerCase();
    let toUnit = fromUnit;

    if (targetSystem === 'metric') {
      if (['oz', 'cup', 'tbsp', 'tsp', 'lb'].includes(fromUnit)) {
        // Convert to appropriate metric
        if (['cup', 'tbsp', 'tsp', 'oz'].includes(fromUnit)) {
          toUnit = 'ml';
        } else if (fromUnit === 'lb') {
          toUnit = 'gram';
        }
      }
    } else if (targetSystem === 'imperial') {
      if (['ml', 'liter', 'gram', 'kg'].includes(fromUnit)) {
        // Convert to appropriate imperial
        if (['ml', 'liter'].includes(fromUnit)) {
          toUnit = 'cup';
        } else if (['gram', 'kg'].includes(fromUnit)) {
          toUnit = 'oz';
        }
      }
    }

    const newQuantity = convertUnit(parseFloat(parsed.quantity) || 1, fromUnit, toUnit);
    return formatIngredientWithUnit(newQuantity, toUnit, parsed.name);
  });
}

// ============================================================================
// 3. DUPLICATE INGREDIENT DETECTION & MERGING
// ============================================================================

function normalizeName(name) {
  return name.toLowerCase()
    .replace(/s\b/g, '') // Remove trailing 's'
    .replace(/\s+/g, ' ') // Normalize spaces
    .trim();
}

function areSimilarIngredients(name1, name2) {
  const norm1 = normalizeName(name1);
  const norm2 = normalizeName(name2);

  return norm1 === norm2 || norm1.includes(norm2) || norm2.includes(norm1);
}

function mergeDuplicateIngredients(ingredientList) {
  const merged = {};

  ingredientList.forEach(ingredient => {
    const parsed = parseIngredientWithUnit(ingredient);
    const normalizedName = normalizeName(parsed.name);

    if (!merged[normalizedName]) {
      merged[normalizedName] = {
        name: parsed.name, // Keep original name
        quantity: parseFloat(parsed.quantity) || 1,
        unit: parsed.unit,
        originalName: normalizedName
      };
    } else {
      // Merge quantities if units match
      if (merged[normalizedName].unit === parsed.unit) {
        merged[normalizedName].quantity += parseFloat(parsed.quantity) || 1;
      }
    }
  });

  return Object.values(merged).map(item =>
    formatIngredientWithUnit(item.quantity, item.unit, item.name)
  );
}

// ============================================================================
// 4. EDITABLE SCALED OUTPUT
// ============================================================================

function makeIngredientsEditable(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const items = container.querySelectorAll('li, .ingredient-entry input');

  items.forEach((item, index) => {
    const isListItem = item.tagName === 'LI';
    const contentElement = isListItem ? item : item.parentElement;
    const originalContent = isListItem ? item.textContent : item.value;

    if (isListItem) {
      contentElement.style.cursor = 'pointer';
      contentElement.style.padding = '8px';
      contentElement.style.margin = '5px 0';
      contentElement.style.borderRadius = '4px';
      contentElement.style.backgroundColor = '#f9f9f9';
      contentElement.style.transition = 'all 0.3s ease';

      contentElement.addEventListener('click', function () {
        if (this.querySelector('input')) return; // Already editing

        const input = document.createElement('input');
        input.type = 'text';
        input.value = originalContent.trim();
        input.className = 'ingredient-edit-input';
        input.style.width = '100%';
        input.style.padding = '8px';
        input.style.border = '2px solid #D96B43';
        input.style.borderRadius = '4px';
        input.style.fontSize = '16px';
        input.style.fontFamily = "'Montserrat', sans-serif";

        this.textContent = '';
        this.appendChild(input);
        input.focus();
        input.select();

        const saveEdit = () => {
          const newValue = input.value.trim();
          contentElement.textContent = newValue;
          sessionStorage.setItem(`ingredient_${index}`, newValue);
        };

        input.addEventListener('blur', saveEdit);
        input.addEventListener('keypress', (e) => {
          if (e.key === 'Enter') saveEdit();
        });
      });
    }
  });
}

function loadEditedIngredients(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const items = container.querySelectorAll('li');
  items.forEach((item, index) => {
    const saved = sessionStorage.getItem(`ingredient_${index}`);
    if (saved) {
      item.textContent = saved;
    }
  });
}

// ============================================================================
// 5. RECIPE NOTES & INSTRUCTIONS
// ============================================================================

function addRecipeNotesSection(containerId = 'main-content') {
  const container = document.getElementById(containerId);
  if (!container) return;

  const notesSection = document.createElement('div');
  notesSection.id = 'recipe-notes-section';
  notesSection.className = 'card';
  notesSection.innerHTML = `
    <h2>📝 Cooking Notes & Instructions</h2>
    <div class="notes-input-group">
      <label for="recipeNotes">Cooking Notes:</label>
      <textarea id="recipeNotes" placeholder="Add any cooking notes or tips..." rows="4"></textarea>
    </div>
    <div class="notes-input-group">
      <label for="recipeInstructions">Instructions/Steps:</label>
      <div id="instructionsSteps"></div>
      <button onclick="addInstructionStep()" class="secondary-btn">+ Add Step</button>
    </div>
  `;

  container.appendChild(notesSection);
  loadRecipeNotesFromStorage();
}

function addInstructionStep() {
  const stepsContainer = document.getElementById('instructionsSteps');
  const stepCount = stepsContainer.children.length + 1;

  const stepDiv = document.createElement('div');
  stepDiv.className = 'instruction-step';
  stepDiv.innerHTML = `
    <span class="step-number">${stepCount}</span>
    <input type="text" class="step-input" placeholder="Enter step..." data-step="${stepCount}">
    <button onclick="removeInstructionStep(this)" class="remove-btn">×</button>
  `;

  stepsContainer.appendChild(stepDiv);
}

function removeInstructionStep(button) {
  button.parentElement.remove();
  updateStepNumbers();
}

function updateStepNumbers() {
  const steps = document.querySelectorAll('.instruction-step');
  steps.forEach((step, index) => {
    step.querySelector('.step-number').textContent = index + 1;
  });
}

function saveRecipeNotes() {
  const notes = document.getElementById('recipeNotes')?.value || '';
  const steps = Array.from(document.querySelectorAll('.step-input')).map(input => input.value);

  sessionStorage.setItem('recipeNotes', notes);
  sessionStorage.setItem('recipeSteps', JSON.stringify(steps));
}

function loadRecipeNotesFromStorage() {
  const notes = sessionStorage.getItem('recipeNotes');
  const stepsJson = sessionStorage.getItem('recipeSteps');

  if (notes) {
    const notesInput = document.getElementById('recipeNotes');
    if (notesInput) notesInput.value = notes;
  }

  if (stepsJson) {
    const steps = JSON.parse(stepsJson);
    const stepsContainer = document.getElementById('instructionsSteps');
    if (stepsContainer) {
      stepsContainer.innerHTML = '';
      steps.forEach((step, index) => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'instruction-step';
        stepDiv.innerHTML = `
          <span class="step-number">${index + 1}</span>
          <input type="text" class="step-input" placeholder="Enter step..." value="${step}">
          <button onclick="removeInstructionStep(this)" class="remove-btn">×</button>
        `;
        stepsContainer.appendChild(stepDiv);
      });
    }
  }
}

function includeNotesInExport(format = 'text') {
  const notes = sessionStorage.getItem('recipeNotes') || '';
  const stepsJson = sessionStorage.getItem('recipeSteps') || '[]';
  const steps = JSON.parse(stepsJson);

  let notesText = '';
  if (notes) {
    notesText = `\nCooking Notes:\n${notes}\n`;
  }

  let stepsText = '';
  if (steps.length > 0) {
    stepsText = '\nInstructions:\n';
    steps.forEach((step, index) => {
      if (step.trim()) {
        stepsText += `${index + 1}. ${step}\n`;
      }
    });
  }

  return { notesText, stepsText };
}

// ============================================================================
// UTILITY: Initialize all enhancements on page load
// ============================================================================

function initializeRecipeEnhancements() {
  // Make ingredients editable on scaled page
  if (document.getElementById('scaledIngredients')) {
    setTimeout(() => {
      makeIngredientsEditable('scaledIngredients');
      loadEditedIngredients('scaledIngredients');
    }, 500);
  }

  // Add notes section to enter recipe page
  if (document.getElementById('recipeIngredientsList')) {
    setTimeout(() => {
      addRecipeNotesSection('main-content');
    }, 500);
  }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeRecipeEnhancements);
} else {
  initializeRecipeEnhancements();
}