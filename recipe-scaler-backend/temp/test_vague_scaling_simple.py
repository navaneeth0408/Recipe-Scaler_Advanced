import re
from typing import List, Dict, Optional, Union

# --- MOCKING / EXTRACTING LOGIC TO TEST ---

def mock_parse_ingredient_line(line: str) -> Optional[Dict]:
    # Remove leading bullets, numbers, etc.
    cleaned = re.sub(r'^[\d\.\)\-\*•]+\s*', '', line)
    
    # Updated regex from ai_ingredient_service.py
    vague_terms = r"sprinkle|pinch|handful|dash|drop|salt to taste|to taste"
    quantity_match = re.match(
        rf"^\s*(\d+(?:\.\d+)?(?:\s+\d+/\d+)?|{vague_terms})\s*"
        r"(kg|g|gm|grams|ml|l|cups?|cup|tablespoons?|tablespoon|tbsp|tbs|teaspoons?|teaspoon|tsp)?\s*(.*)$",
        cleaned,
        re.IGNORECASE
    )

    if quantity_match:
        quantity = quantity_match.group(1).lower()
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
    
    is_vague = False
    if isinstance(raw_qty, str):
        if not raw_qty.strip():
            qty = 1.0
        elif re.search(r'\d', raw_qty):
            # Simplified parser for tests
            qty = float(raw_qty) if '/' not in raw_qty else 0.5 
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
    
    print("--- Extraction Test ---")
    extracted = []
    for line in test_lines:
        res = mock_parse_ingredient_line(line)
        extracted.append(res)
        print(f"Line: '{line.strip()}' -> Extracted: {res}")

    print("\n--- Scaling Test (2x) ---")
    for ing in extracted:
        scaled = mock_scale_ingredient(ing, 1, 2)
        print(f"Original: {ing} -> Scaled: {scaled}")
        
        # Assertions
        name = ing['name'].lower()
        if 'salt' in name:
            if not isinstance(scaled['quantity'], str):
                print(f"FAILURE: {name} quantity is not a string after scaling")
            else:
                print(f"SUCCESS: {name} preserved as '{scaled['quantity']}'")
        
        if 'flour' in name:
            if scaled['quantity'] != 8:
                print(f"FAILURE: Flour not scaled to 8 (got {scaled['quantity']})")
            else:
                print(f"SUCCESS: Flour scaled to 8")

if __name__ == "__main__":
    test()
