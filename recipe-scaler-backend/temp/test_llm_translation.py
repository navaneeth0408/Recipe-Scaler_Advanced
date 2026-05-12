import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)

from app.services.translation_service import translation_service

def test_translation():
    print("Testing general translation (en to ml)")
    text = "Mix the flour and butter."
    tr1 = translation_service.translate_text(text, "en", "ml", context="general")
    print(f"Result: {tr1}\n")

    print("Testing ingredient translation (en to ml)")
    ing = "2 cups all-purpose flour"
    tr2 = translation_service.translate_text(ing, "en", "ml", context="ingredient")
    print(f"Result: {tr2}\n")

if __name__ == "__main__":
    test_translation()
