import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ai_substitution_service import ai_substitution_service

def test_fuzzy_subs():
    test_cases = [
        ("raw rice", 1, "cup"),
        ("whole wheat flour", 2, "cups"),
        ("coconut milks", 1, "can"),
        ("random spice", 1, "tsp")
    ]
    
    print("Testing Fuzzy Substitutions:")
    for ing, qty, unit in test_cases:
        print(f"\nIngredient: {ing}")
        subs = ai_substitution_service.suggest_substitutions(ing, qty, unit)
        for s in subs:
            print(f" - Suggest: {s['name']} ({s['note']})")

if __name__ == "__main__":
    test_fuzzy_subs()
