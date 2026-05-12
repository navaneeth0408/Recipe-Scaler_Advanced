import json
import os
from collections import defaultdict

def prepare():
    # Paths (adjust based on where kagglehub Downloads them)
    # On windows it's usually C:\Users\<user>\.cache\kagglehub\...
    user_profile = os.environ.get('USERPROFILE')
    base_path = os.path.join(user_profile, '.cache', 'kagglehub', 'datasets', 'kanakraj', 'multimodal-ingredient-substitution', 'versions', '2')
    
    pairs_path = os.path.join(base_path, 'substitution_pairs.json')
    
    if not os.path.exists(pairs_path):
        print(f"Error: {pairs_path} not found")
        return

    print(f"Loading {pairs_path}...")
    with open(pairs_path, 'r') as f:
        data = json.load(f)

    # Map: ingredient -> list of substitutes
    dataset_subs = defaultdict(list)
    
    print(f"Sampling first entry: {data[0]}")
    
    for entry in data:
        # Some entries might have null values for these keys
        target_raw = entry.get('ingredient')
        sub_raw = entry.get('substitution_original')
        
        target = str(target_raw).lower().strip() if target_raw else ""
        sub = str(sub_raw).lower().strip() if sub_raw else ""
        
        if target and sub and sub not in dataset_subs[target]:
            dataset_subs[target].append(sub)

    # Save to app/data/dataset_substitutions.json
    output_dir = os.path.join('app', 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'dataset_substitutions.json')
    
    print(f"Stats: Processed {len(data)} entries. Found {len(dataset_subs)} unique ingredients.")
    print(f"Exporting to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(dict(dataset_subs), f, indent=2)

if __name__ == "__main__":
    prepare()
