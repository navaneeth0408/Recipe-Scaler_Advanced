import json
import sys
import os
from collections import Counter

# Add project root to path
sys.path.append(os.getcwd())

from app.services.ingredient_service import STRICT_FOOD_WHITELIST

DATASET_PATH = r'C:\Users\DELL\.cache\kagglehub\datasets\kaggle\recipe-ingredients-dataset\versions\1\train.json'

def explore():
    with open(DATASET_PATH, 'r') as f:
        data = json.load(f)
        
    all_ingredients = []
    for recipe in data:
        all_ingredients.extend(recipe['ingredients'])
        
    counts = Counter(all_ingredients)
    print(f"Total unique ingredients found in global dataset: {len(counts)}")
    
    whitelist_set = set(i.lower() for i in STRICT_FOOD_WHITELIST)
    
    missing = []
    for ing, freq in counts.most_common():
        if ing.lower() not in whitelist_set:
            missing.append((ing, freq))
                
    print("\nMost frequent missing global ingredients:")
    count = 0
    for ing, freq in missing:
        if len(ing) > 2:
            print(f"{ing}: {freq}")
            count += 1
            if count >= 100:
                break

if __name__ == "__main__":
    explore()
