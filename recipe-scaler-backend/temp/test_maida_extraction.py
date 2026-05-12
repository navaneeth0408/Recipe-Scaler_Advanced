import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService
from app.services.translation_service import translation_service

def test_maida_extraction():
    print("Testing maida extraction...")
    text = "Ingredients:\n2 cups maida\n1 kg maida\n1/2 cup sugar\n"
    ingredients = IngredientService.extract_ingredients(text)
    
    found_maida_count = 0
    for ing in ingredients:
        print(f"Extracted: {ing}")
        if ing['name'] == 'maida':
            found_maida_count += 1
            
    assert found_maida_count >= 1, "Failed to extract maida!"
    print("SUCCESS: Maida extracted correctly.\n")

def test_maida_translation():
    print("Testing maida translation...")
    ingredients = [
        {"name": "maida", "quantity": 2, "unit": "cups"}
    ]
    
    # Malayalam
    translated_ml = translation_service.translate_ingredients(ingredients, "ml")
    print(f"Translated (ML): {translated_ml}")
    assert translated_ml[0]['name'] == 'മൈദ', f"Failed to translate maida to Malayalam! Got: {translated_ml[0]['name']}"
    
    # Hindi
    translated_hi = translation_service.translate_ingredients(ingredients, "hi")
    print(f"Translated (HI): {translated_hi}")
    assert translated_hi[0]['name'] == 'मैदा', f"Failed to translate maida to Hindi! Got: {translated_hi[0]['name']}"
    
    print("SUCCESS: Maida translated correctly.\n")

if __name__ == "__main__":
    try:
        test_maida_extraction()
        test_maida_translation()
        print("ALL TESTS PASSED!")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
