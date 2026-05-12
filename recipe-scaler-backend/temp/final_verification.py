import re
from typing import List, Dict, Optional, Union

# --- MOCKING / EXTRACTING LOGIC TO TEST ---

def mock_parse_ingredient_line(line: str) -> Optional[Dict]:
    # UPDATED bullet cleaning regex from ai_ingredient_service.py fix
    cleaned = re.sub(r'^[\-\*••]\s*|^\d+[\.\)]\s*', '', line)
    
    # Updated regex from ai_ingredient_service.py
    vague_terms = r"sprinkle|pinch|handful|dash|drop|salt to taste|to taste"
    units_pattern = r"kg|g|gm|grams|ml|l|cups?|cup|tablespoons?|tablespoon|tbsp|tbs|teaspoons?|teaspoon|tsp|handfuls?|pinches?|pinches|dashes|drops?"
    quantity_match = re.match(
        rf"^\s*(\d+(?:\.\d+)?(?:\s+\d+/\d+)?|{vague_terms})\s*"
        rf"({units_pattern})?\s*(.*)$",
        cleaned,
        re.IGNORECASE
    )

    if quantity_match:
        quantity = quantity_match.group(1)
        unit = (quantity_match.group(2) or '').strip().lower()
        ingredient_name = quantity_match.group(3).strip().lower()
    else:
        quantity = None
        unit = None
        ingredient_name = cleaned.lower()
    
    return {
        "name": ingredient_name,
        "quantity": quantity,
        "unit": unit
    }

def mock_scale_ingredient(ingredient: Dict, original_servings: float, target_servings: float) -> Dict:
    scale_factor = target_servings / original_servings
    raw_qty = ingredient.get('quantity', 0)
    unit = (ingredient.get('unit') or '').lower().strip()
    
    vague_units = ['pinch', 'handful', 'sprinkle', 'dash', 'drop', 'to taste']
    
    is_vague = False
    if any(v in unit for v in vague_units):
        is_vague = True
        new_quantity = raw_qty
    elif isinstance(raw_qty, str):
        if not raw_qty.strip():
            qty = 1.0
        elif re.search(r'\d', raw_qty):
            # Simplified parser for tests
            try:
                qty = float(raw_qty)
            except:
                qty = 1.0
        else:
            is_vague = True
            new_quantity = raw_qty
    else:
        qty = float(raw_qty) if raw_qty is not None else 0.0

    if not is_vague:
        new_quantity = qty * scale_factor

    return {
        "name": ingredient['name'],
        "quantity": new_quantity,
        "unit": ingredient['unit']
    }

# --- TESTS ---

def test():
    test_lines = [
        "4 cups all purpose flour",
        "Sprinkle of salt",
        "Salt to taste",
        "1 handful of coriander"
    ]
    
    results = []
    results.append("--- Extraction & Scaling Test ---")
    
    extracted = []
    for line in test_lines:
        res = mock_parse_ingredient_line(line)
        extracted.append(res)
        results.append(f"Line: '{line.strip()}' -> Extracted: {res}")

    results.append("\n--- Scaling Test (2x) ---")
    for ing in extracted:
        scaled = mock_scale_ingredient(ing, 1, 2)
        results.append(f"Original: {ing} -> Scaled: {scaled}")
        
    with open("temp/final_verification_results.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    test()
