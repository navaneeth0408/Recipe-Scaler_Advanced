import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_palada_only():
    print("Testing 'Palada' alone...")
    text = "Palada"
    ingredients = IngredientService.extract_ingredients(text)
    print(f"Extracted: {ingredients}")

if __name__ == "__main__":
    test_palada_only()
