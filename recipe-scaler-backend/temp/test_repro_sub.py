import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ai_substitution_service import ai_substitution_service

def test_repro():
    print("Testing reproduction of self-substitution...")
    
    ingredient = "almond milk"
    qty = 1
    unit = "cups"
    
    # Simulate the substitution logic
    subs = ai_substitution_service.suggest_substitutions(ingredient, qty, unit)
    
    print(f"\nIngredient: {ingredient}")
    sub_names = [s['name'].lower() for s in subs]
    for s in subs:
        print(f"  - {s['name']} ({s['ratio']}): {s['note']}")
        
    if ingredient.lower() in sub_names:
        print(f"\nISSUE REPRODUCED: '{ingredient}' is in the substitution list.")
    else:
        print(f"\nISSUE NOT REPRODUCED: '{ingredient}' is NOT in the substitution list.")

if __name__ == "__main__":
    test_repro()
