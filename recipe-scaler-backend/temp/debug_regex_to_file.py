import re

vague_terms = r"sprinkle|pinch|handful|dash|drop|salt to taste|to taste"
regex = rf"^\s*(\d+(?:\.\d+)?(?:\s+\d+/\d+)?|{vague_terms})\s*(kg|g|gm|grams|ml|l|cups?|cup|tablespoons?|tablespoon|tbsp|tbs|teaspoons?|teaspoon|tsp)?\s*(.*)$"

lines = [
    "4 cups all purpose flour",
    "Sprinkle of salt",
    "Salt to taste",
    "1 handful of coriander"
]

results = []
for line in lines:
    match = re.match(regex, line, re.IGNORECASE)
    if match:
        results.append(f"Line: '{line}'")
        results.append(f"  Qty: '{match.group(1)}'")
        results.append(f"  Unit: '{match.group(2)}'")
        results.append(f"  Name: '{match.group(3)}'")
    else:
        results.append(f"Line: '{line}' NO MATCH")

with open("temp/debug_results.txt", "w") as f:
    f.write("\n".join(results))
