import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_substitution_service import ai_substitution_service

def test_fallback():
    out = {}
    
    out["1 cup milk"] = ai_substitution_service._fallback_suggest("milk", 1.0, "cup")
    out["1 clove garlic"] = ai_substitution_service._fallback_suggest("garlic", 1.0, "clove")
    out["2 cup butter"] = ai_substitution_service._fallback_suggest("butter", 2.0, "cup")

    with open(os.path.join(os.path.dirname(__file__), "test_out.json"), "vw", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    test_fallback()
