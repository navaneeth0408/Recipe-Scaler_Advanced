import sys
import os
import re

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai_ingredient_service import AIIngredientService
from app.services.scaling_service import ScalingService

def test_vague_extraction_and_scaling():
    service = AIIngredientService()
    
    test_text = """
    4 cups all purpose flour
    Sprinkle of salt
    Salt to taste
    1 handful of coriander
    """
    
    print("--- Extraction Test ---")
    ingredients = service.extract_and_normalize_ingredients(test_text)
    for ing in ingredients:
        print(f"Name: {ing['name']}, Quantity: {ing['quantity']}, Unit: {ing['unit']}")
    
    # Verify salt
    salt_ings = [ing for ing in ingredients if 'salt' in ing['name'].lower()]
    print(f"\nFound {len(salt_ings)} salt items")
    
    print("\n--- Scaling Test (2x) ---")
    original_servings = 1
    target_servings = 2
    
    scaled_ingredients, factor = ScalingService.scale_ingredients(
        ingredients, original_servings, target_servings
    )
    
    for ing in scaled_ingredients:
        print(f"Name: {ing['name']}, Quantity: {ing['quantity']}, Unit: {ing['unit']}")
        
    print(f"\nFactor: {factor}")
    
    # Check if vague quantities are preserved
    print("\n--- Verification Results ---")
    success = True
    for ing in scaled_ingredients:
        name = ing['name'].lower()
        qty = ing['quantity']
        
        if 'salt' in name:
            if not isinstance(qty, str):
                print(f"FAILURE: Salt quantity scaled to {qty} (expected string)")
                success = False
            else:
                print(f"SUCCESS: Salt quantity preserved as '{qty}'")
        
        if 'coriander' in name:
            if not isinstance(qty, str):
                print(f"FAILURE: Coriander quantity scaled to {qty} (expected string)")
                success = False
            else:
                print(f"SUCCESS: Coriander quantity preserved as '{qty}'")
                
        if 'flour' in name:
            if qty != 8:
                print(f"FAILURE: Flour quantity scaled incorrectly to {qty} (expected 8)")
                success = False
            else:
                print(f"SUCCESS: Flour quantity scaled correctly to 8")

    if success:
        print("\nALL TESTS PASSED!")
    else:
        print("\nSOME TESTS FAILED.")

if __name__ == "__main__":
    test_vague_extraction_and_scaling()
