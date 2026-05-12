import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)

from app.services.ingredient_service import IngredientService
from app.services.youtube_service import YouTubeService

print("==== Test 1: Description Parser (previously caught 'the', 'for' as ingredients) ====")
test_lines = [
    "1 for",
    "a the",
    "2 cups flour",
    "1/2 cup sugar",
    "3 eggs",
    "please subscribe"
]

for line in test_lines:
    matches = IngredientService.extract_ingredients(line)
    names = [m.get('name') for m in matches] if matches else []
    print(f"Line '{line}' -> Extracted: {names}")

print("\n==== Test 2: Audio Transcript Parser (previously caught loose words) ====")
test_transcript = "In this video we will use 2 cups of flour and 1 cup of the sugar and 2 for the egg"
matches = YouTubeService.extract_ingredients_from_transcript(test_transcript)
names = [m.get('name') for m in matches] if matches else []
print(f"Transcript -> Extracted: {names}")
