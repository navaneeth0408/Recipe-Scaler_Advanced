import sys
import os
import json

# Add to Python path to import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.ingredient_service import IngredientService
from app.services.scaling_service import ScalingService

print("--- Testing IngredientExtraction ---")
test_text = "Ingredients:\n2 whole 1 cup warm milk\n▶ 1 ½ tsp salt ←\nabout 2-3 cups flour\nSome water"
ingredients = IngredientService.extract_ingredients(test_text)
print(json.dumps(ingredients, indent=2))

print("\n--- Testing Scaling ---")
scaled, factor = ScalingService.scale_ingredients(ingredients, original_servings=2, target_servings=3)
print(f"Scale factor: {factor}")
print(json.dumps(scaled, indent=2))
