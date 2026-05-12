import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.scaling_service import ScalingService

def test_salt_scaling():
    results = []
    # Scenario 1: quantity is string "1", name is "salt"
    ing = {"name": "salt", "quantity": "1", "unit": ""}
    original_servings = 1
    target_servings = 2
    
    scaled = ScalingService.scale_ingredient(ing, original_servings, target_servings)
    results.append(f"Scenario 1 (string '1'): {scaled}")
    
    # Scenario 2: quantity is float 1.0, name is "salt"
    ing2 = {"name": "salt", "quantity": 1.0, "unit": ""}
    scaled2 = ScalingService.scale_ingredient(ing2, original_servings, target_servings)
    results.append(f"Scenario 2 (float 1.0): {scaled2}")
    
    # Scenario 3: quantity is string "sprinkle", name is "salt"
    ing3 = {"name": "salt", "quantity": "sprinkle", "unit": ""}
    scaled3 = ScalingService.scale_ingredient(ing3, original_servings, target_servings)
    results.append(f"Scenario 3 (string 'sprinkle'): {scaled3}")

    # Scenario 4: What if the frontend sends "1 salt" as quantity?
    ing4 = {"name": "salt", "quantity": "1 salt", "unit": ""}
    scaled4 = ScalingService.scale_ingredient(ing4, original_servings, target_servings)
    results.append(f"Scenario 4 (quantity '1 salt'): {scaled4}")

    with open("temp/repro_results.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    test_salt_scaling()
