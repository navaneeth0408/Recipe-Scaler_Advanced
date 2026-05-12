import sys
import os
import re

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService

def test_complex_extraction():
    text = """
    𝗜𝗡𝗚𝗥𝗘𝗗𝗜𝗘𝗡𝗧𝗦
    4  nos ( whole egg )
    80 g ( powdered sugar / white sugar ) 1/3cup
    80 g ( cake flour or all purpose flour )1/2cup
    optional ( flavor )
    """
    
    print("Testing complex extraction for text:")
    # print(text)
    
    # Check if a non-unicode version works better
    import unicodedata
    normalized_text = unicodedata.normalize('NFKD', text)
    print("\nNormalized Text (Plain ASCII-ish):")
    # print(normalized_text)
    
    service = IngredientService()
    results = service.extract_ingredients(text)
    
    print("\nExtracted Ingredients (from original):")
    for res in results:
        print(f" - {res['quantity']} {res['unit']} {res['name']}")
        
    results_norm = service.extract_ingredients(normalized_text)
    print("\nExtracted Ingredients (from normalized):")
    for res in results_norm:
        print(f" - {res['quantity']} {res['unit']} {res['name']}")

if __name__ == "__main__":
    test_complex_extraction()
