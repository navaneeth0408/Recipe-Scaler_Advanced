import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)

from app.services.translation_service import translation_service, Language

print("==== Test 1: Translation service glossary translations ====")
ingredients_to_test = [
    {"name": "coriander"},
    {"name": "mustard seeds"},
    {"name": "ginger"},
    {"name": "coconut milk"},
    {"name": "red chilli"},
    {"name": "green chilli"}
]

translated = translation_service.translate_ingredients(ingredients_to_test, target_lang=Language.MALAYALAM.value)

for original, trans in zip(ingredients_to_test, translated):
    print(f"{original['name']} -> {trans['name']}")

print("\n==== Test 2: Full recipe translation (simulated) ====")
recipe = {
    "name": "Chicken Curry",
    "description": "Tasty chicken curry",
    "ingredients": [
        {"name": "chicken", "quantity": 500, "unit": "g"},
        {"name": "garlic", "quantity": 4, "unit": "cloves"}
    ]
}
trans_recipe = translation_service.translate_recipe(recipe, Language.MALAYALAM.value)
for ing in trans_recipe['ingredients']:
    print(f"{ing.get('quantity')} {ing.get('unit')} {ing.get('name')}")
