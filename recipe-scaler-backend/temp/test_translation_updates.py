import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.translation_service import translation_service

def test_translations():
    print("Testing Malayalam translations...")
    
    test_cases = [
        ("jaggery", "ശർക്കര"),
        ("lemon", "നാരങ്ങ"),
        ("cloves", "ഗ്രാമ്പൂ"),
        ("cardamom", "ഏലക്ക"),
        ("ginger garlic paste", "ഇഞ്ചി വെളുത്തുള്ളി പേസ്റ്റ്"),
        ("lemon juice", "നാരങ്ങാനീര്")
    ]
    
    all_passed = True
    for text, expected in test_cases:
        translated = translation_service.translate_text(text, "en", "ml", context="ingredient")
        print(f"'{text}' -> '{translated}' (Expected: '{expected}')")
        if translated != expected:
            print(f"  FAILED: Expected {expected}, got {translated}")
            all_passed = False
            
    if all_passed:
        print("\nAll translation tests PASSED!")
    else:
        print("\nSome translation tests FAILED.")

if __name__ == "__main__":
    test_translations()
