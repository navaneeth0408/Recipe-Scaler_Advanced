import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_normalization():
    print("Testing ingredient normalization...")
    
    # Test case 1: Multiple variations appearing in single text
    text = "1 tsp turmeric powder and 1 tsp turmeric"
    ingredients = IngredientService.extract_ingredients(text)
    print(f"Input: '{text}'")
    for ing in ingredients:
        print(f"  Extracted: {ing}")
    
    # Check if they merged (they should if they normalize to same name)
    # Wait, the current logic only keeps one in unique_map during Step 2.
    # It doesn't sum quantities yet if they are found in different parts of text?
    # Let's check.
    
    # Test case 2: Clove garlic vs Garlic
    text = "2 cloves garlic and 1 garlic"
    ingredients = IngredientService.extract_ingredients(text)
    print(f"\nInput: '{text}'")
    for ing in ingredients:
        print(f"  Extracted: {ing}")
        
    # Test case 3: Maida vs Flour
    text = "1 cup maida and 1 cup flour"
    ingredients = IngredientService.extract_ingredients(text)
    print(f"\nInput: '{text}'")
    for ing in ingredients:
        print(f"  Extracted: {ing}")

if __name__ == "__main__":
    test_normalization()
    print("\nNORMALIZATION TESTS FINISHED!")
