import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ai_substitution_service import ai_substitution_service

def test_substitutions():
    print("Testing ingredient substitutions...")
    
    test_cases = [
        ("ghee", 3, "tbsp"),
        ("lemon", 1, "unit"),
        ("meat masala", 1, "tsp"),
        ("nonexistent ingredient", 1, "unit") # Should get a generic fallback
    ]
    
    for name, qty, unit in test_cases:
        # We use _fallback_suggest directly to test our new logic without calling external APIs
        subs = ai_substitution_service._fallback_suggest(name, qty, unit)
        print(f"\nIngredient: {name}")
        for s in subs:
            print(f"  - {s['name']} ({s['ratio']}): {s['note']}")
            
    # Specific verification for Meat Masala
    meat_masala_subs = ai_substitution_service._fallback_suggest("meat masala", 1, "tsp")
    names = [s['name'] for s in meat_masala_subs]
    assert "garam masala + 1 tsp chilli powder" in names or "another compatible spice or spice blend" in names
    assert "tofu" not in names[0], "Meat masala should NOT be substituted with tofu!"

if __name__ == "__main__":
    test_substitutions()
    print("\nSUBSTITUTION TESTS FINISHED!")
