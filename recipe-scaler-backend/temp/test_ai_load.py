import sys
import os
import time

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.ai_ingredient_service import ai_ingredient_service
from app.services.speech_service import SpeechService

def test_lazy_loading():
    print("Verifying lazy loading functionality...")
    
    # 1. AI Ingredient Service (transformers/spacy)
    print("\nTesting Ingredient classifier lazy load...")
    start = time.time()
    classifier = ai_ingredient_service.extractor.classifier
    duration = time.time() - start
    print(f"First load duration: {duration:.4f}s")
    
    if classifier:
        print("Success: Transformer model loaded on demand!")
    else:
        print("Bypassed: Transformers not available or SKIP_AI_MODELS=true")

    # 2. Speech Service (faster-whisper)
    print("\nTesting Whisper model lazy load...")
    start = time.time()
    try:
        model = SpeechService.get_model("base")
        duration = time.time() - start
        print(f"First load duration: {duration:.4f}s")
        print("Success: Whisper model loaded on demand!")
    except Exception as e:
        print(f"Whisper load failed or skipped: {e}")

if __name__ == "__main__":
    test_lazy_loading()
    print("\nLAZY LOADING VERIFICATION FINISHED!")
