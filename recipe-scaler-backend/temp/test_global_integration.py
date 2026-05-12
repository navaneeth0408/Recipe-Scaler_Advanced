import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService
from app.services.translation_service import translation_service

def test_global_ingredients_extraction():
    print("Testing global ingredients extraction...")
    test_cases = [
        "2 scallions",
        "1/2 cup kosher salt",
        "1 avocado",
        "2 shallots",
        "1 lb ground beef",
        "1 cup buttermilk",
        "1 tbsp mayonnaise"
    ]
    
    for text in test_cases:
        ingredients = IngredientService.extract_ingredients(text)
        if ingredients:
            print(f"Input: '{text}' -> Extracted: {ingredients[0]}")
        else:
            print(f"FAILED to extract from: '{text}'")

def test_deep_translator_fallback():
    print("\nTesting deep_translator fallback...")
    # These terms might not be in the local glossary, so deep_translator should handle them
    test_cases = [
        ("scallions", "ml", "സവാളയില"), # Now in glossary, but let's see
        ("avocado", "hi", "एवोकाडो"), # Now in glossary
        ("pomegranate", "ml", "മാതളപ്പഴം"), # Not in glossary
        ("dragon fruit", "hi", "ड्रैगन फ्रूट") # Not in glossary
    ]
    
    for name, lang, expected in test_cases:
        try:
            ingredients = [{"name": name, "quantity": 1, "unit": "unit"}]
            translated = translation_service.translate_ingredients(ingredients, lang)
            result = translated[0]['name']
            print(f"Translate '{name}' to {lang} -> Result: {result}")
        except Exception as e:
            print(f"Translation failed for {name} to {lang}: {e}")

if __name__ == "__main__":
    test_global_ingredients_extraction()
    test_deep_translator_fallback()
    print("\nGLOBAL INTEGRATION TESTS FINISHED!")
