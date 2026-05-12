import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_final():
    text = """
    1 cup raw rice
    water
    1/2 cup poha/flattened rice
    grated coconut
    1tsp sugar
    salt
    oil
    """
    
    print("Final Verification - ACTUAL Ingredients List:")
    service = IngredientService()
    results = service.extract_ingredients(text)
    
    # Sort results to make summary consistent
    results.sort(key=lambda x: x['name'])
    
    print("\nEXTRACTED RESULTS:")
    for res in results:
        print(f" - {res['quantity']} {res['unit']} {res['name']}")
    
    # Specific checks
    names = [r['name'] for r in results]
    print("\nSpecific Checks:")
    print(f"Rice correctly extracted: {'rice' in names or 'raw rice' in names}")
    print(f"Poha correctly extracted: {'poha' in names}")
    print(f"No duplicates for poha: {names.count('poha') == 1}")
    print(f"Grate coconut corrected extracted: {'desiccated coconut' in names or 'grated coconut' in names}")
    print(f"Water correctly extracted: {'water' in names}")
    print(f"Noise 'flavour' removed: {'flavour' not in names and 'flavor' not in names}")

if __name__ == "__main__":
    test_final()
