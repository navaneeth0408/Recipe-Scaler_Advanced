import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_substitution_service import ai_substitution_service

def test_fallback():
    print("Testing fallback substitutions for 1 cup milk:")
    res = ai_substitution_service._fallback_suggest("milk", 1.0, "cup")
    print(json.dumps(res, indent=2))

    print("\nTesting fallback substitutions for 1 clove garlic:")
    res2 = ai_substitution_service._fallback_suggest("garlic", 1.0, "clove")
    print(json.dumps(res2, indent=2))
    
    print("\nTesting fallback substitutions for 2 cup butter:")
    res3 = ai_substitution_service._fallback_suggest("butter", 2.0, "cup")
    print(json.dumps(res3, indent=2))

if __name__ == "__main__":
    test_fallback()
