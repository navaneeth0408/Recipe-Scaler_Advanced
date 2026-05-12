import sys
import os
import json

# Add backend path to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)

from app.services.ingredient_service import IngredientService

def test_extraction():
    test_cases = [
        ("2 table spoons instant yeast", ["yeast"], "tbsp"),
        ("red bell pepper, scotch bonnet bell pepper and green bell pepper", ["red bell pepper", "scotch bonnet bell pepper", "green bell pepper"], "whole"),
        ("3 carrots", ["carrot"], "whole"),
        ("1/2 teaspoon curry powder", ["curry powder"], "tsp"),
        ("1 seasoning cube", ["seasoning cube"], "whole"),
        ("1 cooking spoon vegetable oil", ["vegetable oil"], "cooking spoon"),
        ("2 Chicken breasts", ["chicken breasts"], "whole"),
        ("4 sausage pieces", ["sausage"], "whole"),
        ("3 bacon slices", ["bacon"], "whole"),
        ("sprinkle of salt", ["salt"], "")
    ]
    
    results = []
    all_passed = True
    
    for text, expected_names, expected_unit in test_cases:
        matches = IngredientService.extract_ingredients(text)
        extracted_names = [m['name'] for m in matches]
        extracted_units = [m['unit'] for m in matches]
        extracted_qtys = [m['quantity'] for m in matches]
        
        passed_names = all(name in extracted_names for name in expected_names)
        passed_unit = expected_unit in extracted_units if passed_names else False
        
        case_passed = passed_names and passed_unit
        if not case_passed:
            all_passed = False
            
        results.append({
            "text": text,
            "expected_names": expected_names,
            "expected_unit": expected_unit,
            "extracted_names": extracted_names,
            "extracted_units": extracted_units,
            "extracted_qtys": extracted_qtys,
            "passed": case_passed
        })
        
    final_output = {
        "success": all_passed,
        "results": results
    }
    
    with open("temp/verification_results.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)
        
    print(f"Verification completed. Success: {all_passed}")

if __name__ == "__main__":
    test_extraction()
