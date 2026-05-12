import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_palada():
    print("Testing Palada Payasam extraction...")
    
    # Typical transcript for Palada Payasam
    text = "To make palada payasam, take 1 litre milk and add 1 packet of palada payasam mix. Add half cup sugar if needed."
    
    ingredients = IngredientService.extract_ingredients(text)
    
    print(f"\nSource Text: {text}")
    print("\nExtracted Ingredients:")
    for ing in ingredients:
        print(f"  - {ing['quantity']} {ing['unit']} {ing['name']}")
        
    names = [ing['name'] for ing in ingredients]
    if "milk" in names and "palada payasam mix" in names:
        print("\nBoth milk and palada payasam mix extracted.")
    elif "milk" in names:
        print("\nOnly milk extracted.")
    elif "palada payasam mix" in names:
        print("\nOnly palada payasam mix extracted.")
    else:
        print("\nNeither extracted.")

if __name__ == "__main__":
    test_palada()
