import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_shaan_geo_format():
    print("Testing Shaan Geo 'Food - Quantity' format extraction...")
    
    # Text exactly as seen in Shaan Geo's video descriptions
    text = """
    - INGREDIENTS -
    Beef - 1 kg
    Coriander powder - 1+2 Tablespoon
    Garam Masala 1+1 Teaspoon (OR) Meat Masala - 1 1/4 Tablespoon
    """
    
    ingredients = IngredientService.extract_ingredients(text)
    print(f"Input text:\n{text}")
    print("\nExtracted ingredients:")
    for ing in ingredients:
        print(f"  - {ing['name']}: {ing['quantity']} {ing['unit']}")
    
    # Verify Beef - 1 kg
    beef = next((i for i in ingredients if i['name'] == 'beef'), None)
    assert beef is not None, "Beef not found!"
    assert beef['quantity'] == 1, f"Beef quantity should be 1, got {beef['quantity']}"
    assert beef['unit'] == 'kilograms', f"Beef unit should be kilograms, got {beef['unit']}"
    
    # Verify Meat Masala - 1 1/4 Tablespoon
    meat_masala = next((i for i in ingredients if i['name'] == 'meat masala'), None)
    assert meat_masala is not None, "Meat Masala not found!"
    assert meat_masala['quantity'] == 1.25, f"Meat masala qty should be 1.25, got {meat_masala['quantity']}"
    assert meat_masala['unit'] == 'tbsp', f"Meat masala unit should be tbsp, got {meat_masala['unit']}"

    print("\nSUCCESS: Shaan Geo format extracted perfectly!")

if __name__ == "__main__":
    test_shaan_geo_format()
