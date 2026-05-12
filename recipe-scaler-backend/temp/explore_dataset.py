import pandas as pd
import sys
import os
import re

# Add project root to path
sys.path.append(os.getcwd())

from app.services.ingredient_service import STRICT_FOOD_WHITELIST

DATASET_PATH = r'C:\Users\DELL\.cache\kagglehub\datasets\sooryaprakash12\cleaned-indian-recipes-dataset\versions\1\Cleaned_Indian_Food_Dataset.csv'

def explore():
    df = pd.read_csv(DATASET_PATH)
    
    # Extract unique ingredients from Cleaned-Ingredients
    all_ingredients = set()
    for row in df['Cleaned-Ingredients']:
        if isinstance(row, str):
            # Ingredients are usually comma separated
            ings = [i.strip().lower() for i in row.split(',')]
            all_ingredients.update(ings)
            
    print(f"Total unique ingredients found in dataset: {len(all_ingredients)}")
    
    # Check overlap with whitelist
    whitelist_set = set(i.lower() for i in STRICT_FOOD_WHITELIST)
    
    missing = []
    for ing in all_ingredients:
        if ing not in whitelist_set:
            # Basic cleaning to avoid "2 cups milk" in cleaned ingredients if any
            clean_ing = re.sub(r'^\d+\s+\w+\s+', '', ing)
            if clean_ing not in whitelist_set:
                missing.append(ing)
                
    missing.sort()
    print(f"Number of ingredients not in current whitelist: {len(missing)}")
    
    # Show some interesting missing ingredients (potentially common ones)
    # We can filter for things that appear frequently
    all_ings_list = []
    for row in df['Cleaned-Ingredients']:
        if isinstance(row, str):
            all_ings_list.extend([i.strip().lower() for i in row.split(',')])
            
    from collections import Counter
    counts = Counter(all_ings_list)
    
    print("\nMost frequent missing ingredients:")
    count = 0
    for ing, freq in counts.most_common():
        if ing not in whitelist_set and len(ing) > 2:
            print(f"{ing}: {freq}")
            count += 1
            if count >= 50:
                break
                
    # Extra: Check for units in TranslatedIngredients
    print("\nMost frequent units in dataset:")
    all_text = " ".join(df['TranslatedIngredients'].dropna().astype(str))
    # Simple regex for finding words that might be units (following a number)
    unit_matches = re.findall(r'\d+\s+([a-zA-Z]+)', all_text)
    unit_counts = Counter(unit_matches)
    for unit, freq in unit_counts.most_common(50):
        print(f"{unit}: {freq}")

if __name__ == "__main__":
    explore()
