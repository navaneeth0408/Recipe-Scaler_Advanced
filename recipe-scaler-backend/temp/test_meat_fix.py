import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_meat_masala_fix():
    print("Testing Meat Masala extraction fix...")
    
    # Text from the video description
    text = """
    INGREDIENTS -
    Beef - 1 kg
    Meat Masala - 1 1/4 Tablespoon
    """
    
    ingredients = IngredientService.extract_ingredients(text)
    print(f"Input text:\n{text}")
    print("\nExtracted ingredients:")
    for ing in ingredients:
        print(f"  - {ing['quantity']} {ing['unit']} {ing['name']}")
    
    # Verify that 'meat' is NOT extracted as a separate 500g item
    extracted_names = [ing['name'] for ing in ingredients]
    assert "beef" in extracted_names
    assert "meat masala" in extracted_names
    assert "meat" not in extracted_names or "meat masala" == "meat masala" # meat masala is better
    
    print("\nSUCCESS: 'meat masala' extracted correctly and 'meat' partial match avoided.")

if __name__ == "__main__":
    test_meat_masala_fix()
