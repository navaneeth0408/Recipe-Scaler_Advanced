import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)

from app.services.ai_substitution_service import ai_substitution_service

print("==== Testing offline fallback substitutions ====")
tests = [
    {"ingredient": "paneer", "quantity": 200, "unit": "g"},
    {"ingredient": "coconut milk", "quantity": 1, "unit": "cup"},
    {"ingredient": "coriander powder", "quantity": 2, "unit": "tsp"},
    {"ingredient": "unknown generic meat", "quantity": 500, "unit": "g"}, # to trigger fallback category
]

for test in tests:
    # use _fallback_suggest to force local substitutions without Groq/OpenAI calls
    subs = ai_substitution_service._fallback_suggest(
        ingredient=test["ingredient"],
        quantity=test["quantity"],
        unit=test["unit"]
    )
    print(f"\nSubstitutes for {test['ingredient']}:")
    for s in subs:
        print(f"  - {s.get('name')} ({s.get('ratio')}) : {s.get('note')}")

