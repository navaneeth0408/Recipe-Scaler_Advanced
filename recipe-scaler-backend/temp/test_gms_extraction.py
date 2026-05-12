import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_gms_extraction():
    print(f"UNIT_MAP keys: {list(IngredientService.UNIT_MAP.keys())[:20]}...")
    print(f"Is 'gms' in UNIT_MAP? {'gms' in IngredientService.UNIT_MAP}")
    
    text = "300 gms Chicken breast boneless"
    print(f"\nTesting extraction for: {text}")
    results = IngredientService.extract_ingredients(text)
    
    if results:
        for res in results:
            print(f"Extracted: Name='{res['name']}', Qty={res['quantity']}, Unit='{res['unit']}'")
    else:
        print("FAILED: No ingredients extracted.")

if __name__ == "__main__":
    test_gms_extraction()
