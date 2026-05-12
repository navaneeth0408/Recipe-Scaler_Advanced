import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ai_substitution_service import ai_substitution_service

def test_dataset_substitutions():
    print("Testing dataset-driven ingredient substitutions...")
    
    # "applesauce" is in the dataset (I saw it in sampling)
    # "arrowroot" is also there
    test_ingredients = ["applesauce", "arrowroot", "ghee"]
    
    for ing in test_ingredients:
        subs = ai_substitution_service.suggest_substitutions(ing, 1, "unit")
        print(f"\nIngredient: {ing}")
        if subs:
            for s in subs:
                print(f"  - {s['name']} ({s['ratio']}): {s['note']}")
        else:
            print("  - No substitutions found!")

    # Verify applesauce has dataset subs
    applesauce_subs = ai_substitution_service.suggest_substitutions("applesauce", 1, "unit")
    assert len(applesauce_subs) > 0, "Applesauce should have substitutions from the dataset!"
    
    # Verify ghee still uses manual high-confidence subs
    ghee_subs = ai_substitution_service.suggest_substitutions("ghee", 1, "unit")
    assert "butter" in [s['name'] for s in ghee_subs], "Ghee should still have 'butter' as a substitute!"

if __name__ == "__main__":
    test_dataset_substitutions()
    print("\nDATASET SUBSTITUTION TESTS FINISHED!")
