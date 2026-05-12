import sys
import os
import json

# Add to Python path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ingredient_service import IngredientService
from app.services.ai_ingredient_service import ai_ingredient_service

test_text = """
Palada Payasam Mix – 300 gm or 200 gm
Milk – 1 litre or 750ml
Sugar – ½ tablespoon
Salt – 1 pinch
Ghee – 1 tablespoon
Water – 1.5 cup
"""

results_rule = IngredientService.extract_ingredients(test_text)
print("RULE_RESULTS_START")
for res in results_rule:
    print(f"ING: {res['name']} | QTY: {res['quantity']} | UNIT: {res['unit']}")
print("RULE_RESULTS_END")

# For AI service, it might try to call external API, which might fail.
# Let's see what it does.
try:
    results_ai = ai_ingredient_service.extract_and_normalize_ingredients(test_text)
    print("AI_RESULTS_START")
    for res in results_ai:
        print(f"ING: {res['name']} | QTY: {res['quantity']} | UNIT: {res['unit']}")
    print("AI_RESULTS_END")
except Exception as e:
    print(f"AI_SERVICE_ERROR: {str(e)}")
