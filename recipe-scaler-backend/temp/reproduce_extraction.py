import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_extraction():
    text = """
    1 cup raw rice
    water
    1/2 cup poha/flattened rice
    grated coconut
    1tsp sugar
    salt
    oil
    """
    
    print("Testing extraction for text:")
    print(text)
    
    service = IngredientService()
    results = service.extract_ingredients(text)
    
    print("\nExtracted Ingredients:")
    for res in results:
        print(f" - {res['quantity']} {res['unit']} {res['name']}")

if __name__ == "__main__":
    test_extraction()
