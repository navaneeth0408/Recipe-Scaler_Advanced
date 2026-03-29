# 📱 Recipe Scaler - Visual Feature Guide

## Feature 1: 🥘 Ingredient Categorization

### Before (Standard List)
```
□ 2 cups flour
□ 1 cup sugar
□ 1 tsp salt
□ 2 cups milk
□ 3 eggs
□ 1 tbsp vanilla extract
□ 2 tbsp butter
```

### After (Categorized)
```
🥘 MAIN INGREDIENTS
├─ 2 cups flour
├─ 3 eggs
└─ 1 cup sugar

💧 LIQUIDS
├─ 2 cups milk
└─ 1 tbsp vanilla extract

🧂 SPICES & SEASONINGS
└─ 1 tsp salt

✨ GARNISH & TOPPINGS
└─ 2 tbsp butter
```

### Benefits
- 🎯 Easier to follow while cooking
- 📋 Better organization for shopping
- ✅ Prevents ingredient misses
- 🎨 Visual clarity

---

## Feature 2: 🔄 Unit Conversion Toggle

### User Interface
```
┌─────────────────────────────────────┐
│  Unit System:  [Original Units ▼]  │
│  ◉ Original Units                   │
│  ○ Metric (g, ml)                   │
│  ○ Imperial (oz, cups)              │
└─────────────────────────────────────┘
```

### Conversion Example

#### Original (from YouTube)
```
□ 2 cups flour
□ 1/2 cup sugar
□ 250 ml milk
□ 2 oz butter
```

#### Switch to Metric
```
□ 473 ml flour
□ 118 ml sugar
□ 250 ml milk
□ 56 g butter
```

#### Switch to Imperial
```
□ 2 cups flour
□ 1/2 cup sugar
□ 1 cup milk
□ 2 oz butter
```

### Instant Toggling
- No refresh needed
- Switch back anytime
- Original always preserved
- Real-time calculation

---

## Feature 3: ✏️ Editable Scaled Output

### Interactive Ingredients

#### Default View (Hover)
```
╭─────────────────────────────────────╮
│ 2 cups flour  👆 (Click to edit)    │
│ 1.5 cups sugar  👆                  │
│ 1 cup milk  👆                      │
│ 2 oz butter  👆                     │
╰─────────────────────────────────────╯
```

#### Click to Edit
```
╭─────────────────────────────────────╮
│ ┌─────────────────────────────┐    │
│ │ 2 cups flour           [✏️] │    │
│ │                             │    │
│ │ [Save ✓]  [Cancel ✗]       │    │
│ └─────────────────────────────┘    │
│ 1.5 cups sugar  👆                  │
│ 1 cup milk  👆                      │
│ 2 oz butter  👆                     │
╰─────────────────────────────────────╯
```

#### Edit Mode
```
Original: 2 cups flour
Edit to:  3/4 cup flour
          ╰─ Press Enter to save
```

### Use Cases
```
Original recipe:     2 cups flour
You want less:       👉 Edit to 1.5 cups
Saves to session:    ✓ Automatically saved
Includes in export:  ✓ PDF/Text/Print all updated
Survives unit swap:  ✓ Stays 1.5 cups when converting
```

---

## Feature 4: 🔍 Duplicate Ingredient Detection

### Detection & Merging

```
BEFORE MERGE:
├─ 1 cup onion
├─ 1/2 cup onions
├─ 2 tbsp garlic
├─ 1 tbsp garlic cloves
├─ 3 cups oil
└─ 1 cup olive oil

AFTER MERGE:
├─ 1.5 cups onion  ✓ (merged)
├─ 3 tbsp garlic  ✓ (merged)
├─ 3 cups oil
└─ 1 cup olive oil (kept - more specific)
```

### Smart Rules
```
RULE 1: Plurals
  onion + onions = 1 ingredient

RULE 2: Quantity Summation
  1 cup + 1/2 cup = 1.5 cups (same unit)

RULE 3: Name Normalization
  Salt + salt = 1 ingredient
  Garlic + garlic clove = same (substring match)

RULE 4: Unit Mismatch
  3 cups oil + 1 tbsp oil = kept separate (convert first?)
  
RULE 5: Specificity
  Oil + Olive Oil = kept separate (different)
  Onion + Diced Onion = merged (same base)
```

### Shopping Benefits
```
Recipe calls for:
- 2 cups flour
- 2 tbsp flour
- 1 cup flour

Instead of: Buy 5 items of flour
Smart merge: 3.25 cups flour total ✓
```

---

## Feature 5: 📝 Recipe Notes & Instructions

### Input Form (Enter Recipe Page)
```
┌─────────────────────────────────────────────────────┐
│ 📝 COOKING NOTES & INSTRUCTIONS                    │
├─────────────────────────────────────────────────────┤
│ Cooking Notes:                                      │
│ ┌─────────────────────────────────────────────────┐│
│ │ - Preheat oven to 350°F                        ││
│ │ - Use room temperature eggs                    ││
│ │ - Mix dry ingredients separately first         ││
│ └─────────────────────────────────────────────────┘│
│                                                      │
│ Instructions/Steps:                                 │
│ ┌─────────────────────────────────────────────────┐│
│ │ ① Combine dry ingredients in a bowl            ││
│ │ ② Beat eggs and sugar until fluffy             ││
│ │ ③ Fold in dry ingredients slowly               ││
│ │ ④ Pour into baking pan                         ││
│ │ ⊕ Add Step  ✕ Delete                           ││
│ └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

### Display Form (Scaled Recipe Page)
```
┌─────────────────────────────────────────────────────┐
│ 📝 COOKING NOTES                                    │
├─────────────────────────────────────────────────────┤
│ - Preheat oven to 350°F                             │
│ - Use room temperature eggs                         │
│ - Mix dry ingredients separately first              │
├─────────────────────────────────────────────────────┤
│ 👨‍🍳 INSTRUCTIONS                                     │
├─────────────────────────────────────────────────────┤
│ 1. Combine dry ingredients in a bowl                │
│ 2. Beat eggs and sugar until fluffy                 │
│ 3. Fold in dry ingredients slowly                   │
│ 4. Pour into baking pan                             │
└─────────────────────────────────────────────────────┘
```

### Integrated in Exports

#### PDF Export
```
═══════════════════════════════════════════════════════
    CHOCOLATE CHIP COOKIES (SCALED)
═══════════════════════════════════════════════════════

INGREDIENTS:
• 2 cups flour
• 1 cup butter
• 3 eggs
• 2 cups chocolate chips
• 1 tsp vanilla

COOKING NOTES:
- Preheat oven to 350°F
- Room temperature ingredients work best
- Don't overmix the dough

INSTRUCTIONS:
1. Mix flour and salt together
2. Cream butter and sugar
3. Add eggs one at a time
4. Fold in flour mixture
5. Fold in chocolate chips
6. Drop on baking sheet
7. Bake 12-15 minutes
```

#### Text File Export
```
Chocolate Chip Cookies

Ingredients:
- 2 cups flour
- 1 cup butter
- 3 eggs
- 2 cups chocolate chips
- 1 tsp vanilla

Cooking Notes:
- Preheat oven to 350°F
- Room temperature ingredients work best
- Don't overmix the dough

Instructions:
1. Mix flour and salt together
2. Cream butter and sugar
3. Add eggs one at a time
4. Fold in flour mixture
5. Fold in chocolate chips
6. Drop on baking sheet
7. Bake 12-15 minutes
```

---

## 🔄 Feature Interaction Example

### Complete Workflow

#### Step 1: Enter Recipe with YouTube
```
[Enter YouTube Link]
        ↓
[Fetch Ingredients] → Automatically categorized
        ↓
Shows 🥘 Main | 🧂 Spices | 💧 Liquids | 🍗 Proteins | ✨ Garnish
```

#### Step 2: Scale & Add Notes
```
[Set Servings: 4 servings]
        ↓
[Click to add Cooking Notes]
[Click to add Steps 1, 2, 3, 4...]
        ↓
[Click "Scale Recipe"]
```

#### Step 3: Adjust on Scaled Page
```
Ingredients now appear:
- Organized by category
- Clickable to edit quantities
- Unit conversion dropdown available
        ↓
User can:
✓ Edit any quantity
✓ Convert units (Original → Metric ↔ Imperial)
✓ See notes and instructions
✓ Add/edit notes
✓ Edit instruction steps
```

#### Step 4: Export Everything
```
[Click Export dropdown]
    ├─ PDF (formatted with categories, notes, steps)
    ├─ Text (plain text with all info)
    ├─ Email (sends complete recipe)
    └─ Print (includes everything)
        ↓
All exports include:
✓ Recipe name
✓ Categorized ingredients (edited quantities)
✓ Cooking notes
✓ Step-by-step instructions
✓ Source (if YouTube)
```

---

## 📊 Feature Comparison Matrix

```
Feature          │ Input    │ Scaling  │ Export   │ Print    │ Save
─────────────────┼──────────┼──────────┼──────────┼──────────┼──────
Categorization   │ ✓ Auto   │ ✓ Display│ -        │ -        │ -
Unit Conversion  │ -        │ -        │ ✓ Toggle │ ✓ Toggle │ ✓ Last
Editable Output  │ -        │ -        │ ✓ Edited │ ✓ Edited │ ✓ Edited
Duplicate Detect │ -        │ ✓ Auto   │ ✓ Merged │ ✓ Merged │ ✓ Merged
Notes & Steps    │ ✓ Input  │ ✓ Show   │ ✓ Incl.  │ ✓ Incl.  │ ✓ Store
```

---

## 💡 Pro Tips

### For Best Results

#### 1️⃣ **Adding Notes**
- Include cooking time for each step
- Note temperature requirements
- Add prep instructions ("mince fine" vs "slice")
- Include resting times

#### 2️⃣ **Editing Quantities**
- Adjust for availability ("out of milk? use 3/4 cup")
- Personal taste ("less salt for low-sodium diet")
- Portion size ("need 6 servings? scale up here")

#### 3️⃣ **Unit Conversion**
- Convert to units you're comfortable with
- Double-check volume-to-weight conversions
- Keep original handy for comparison

#### 4️⃣ **Saving Recipes**
- Always save with notes for future reference
- Edit notes as you cook ("reduced salt next time")
- Build your personal recipe collection

---

## ⚡ Quick Actions

### Most Common Tasks

```
Task                          Action
─────────────────────────────────────────────────────
Scale recipe 2x                Scale to 2 servings
Half a recipe                  Scale to 0.5 servings
Convert to metric              Dropdown → Metric
Edit 1 ingredient              Click ingredient → Edit
Add cooking note               Click "Cooking Notes" field
Add step                       Click "+ Add Step"
Export as PDF                  Export dropdown → PDF
Print with notes               Print button (includes all)
Save for later                 Save Recipe button
Undo all edits                 Refresh page
```

---

## 🎯 Feature Use Cases

### Use Case 1: YouTube Recipe Scaling
```
Goal: Make pasta for 6 people
Action: 
  1. Enter YouTube link
  2. Ingredients auto-categorized
  3. Set servings to 6
  4. Click Scale
  5. Ingredients auto-scaled
  6. Edit any that need adjustment
  7. Export PDF
  ✓ Done in ~1 minute
```

### Use Case 2: Manual Recipe with Conversions
```
Goal: Convert grandma's recipe to metric
Action:
  1. Enter recipe manually
  2. Add notes ("secret is room temp ingredients")
  3. Add steps from her instructions
  4. Scale as needed
  5. Switch unit system to Metric
  6. Adjust any conversions
  7. Save recipe
  ✓ Preserved for future use
```

### Use Case 3: Shopping List Optimization
```
Goal: Consolidate ingredients before shopping
Action:
  1. Combine 3 recipes
  2. Duplicates auto-merge (onion + onions = 1 item)
  3. Units unified (convert all to cups)
  4. Export text list
  5. Take to store
  ✓ No confusion at store
```

---

## 🔧 Keyboard Shortcuts

```
Action              Key         Where
────────────────────────────────────────────────
Save ingredient     Enter       In edit mode
Cancel edit         Esc         In edit mode
Tab navigation      Tab         Form fields
Jump to notes       Jump        During scaling
Select unit system  Arrow keys  Dropdown
Refresh (undo all)  F5          Anytime
Print preview       Ctrl+P      Before print
Select all          Ctrl+A      In text areas
```

---

## ✅ Checklist for Success

When using Recipe Scaler with new features:

- [ ] Recipe imported/entered
- [ ] Ingredients look organized (categories visible)
- [ ] Servings/scale set correctly
- [ ] Any manual adjustments made
- [ ] Cooking notes added (optional but recommended)
- [ ] Steps added (optional but recommended)
- [ ] Unit system set to your preference
- [ ] Ready to export/print/save

---

*Visual Guide Complete - Ready to Use!* 🎉

