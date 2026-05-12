import sys
import os
import re

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ingredient_service import IngredientService, STRICT_FOOD_WHITELIST

def debug_extraction():
    text = """
    1 cup raw rice
    water
    1/2 cup poha/flattened rice
    grated coconut
    1tsp sugar
    salt
    oil
    """
    
    print("Debug extraction for text:")
    
    qty_pattern = (
        r'('
        r'\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+'
        r'|a|an|one|two|three|four|five|six|seven|eight|nine|ten'
        r'|half|½'
        r'|sprinkle|pinch|handful'
        r')'
    )
    units = "|".join(IngredientService.UNIT_MAP.keys())
    unit_pattern = rf'(?:\b({units})\b)?'
    descriptor_pattern = r'(?:(?:\w+(?:-\w+)?)\s+){0,3}'

    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]
    
    for sent in sentences:
        print(f"\nSentence: '{sent}'")
        sent_lower = sent.lower()
        
        for food in STRICT_FOOD_WHITELIST:
            if re.search(rf'\b{re.escape(food)}(?:s|es)?\b', sent_lower):
                print(f"  Found food keyword: '{food}'")
                
                regex_qty_first = rf'\b{qty_pattern}\b\s*{unit_pattern}\s*(?:of\s+)?{descriptor_pattern}{re.escape(food)}(?:s|es)?\b'
                match = re.search(regex_qty_first, sent_lower)
                if match:
                    print(f"    Regex MATCH (qty first): {match.groups()}")
                else:
                    print(f"    Regex FAIL (qty first): {regex_qty_first}")
                    
                regex_food_first = rf'\b{re.escape(food)}(?:s|es)?\b\s*[-:–]\s*{qty_pattern}\b\s*{unit_pattern}'
                match = re.search(regex_food_first, sent_lower)
                if match:
                    print(f"    Regex MATCH (food first): {match.groups()}")

if __name__ == "__main__":
    debug_extraction()
