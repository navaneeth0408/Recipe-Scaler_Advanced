import time
import sys
import importlib

def benchmark_import(module_name):
    start = time.time()
    try:
        if module_name in sys.modules:
            del sys.modules[module_name]
        importlib.import_module(module_name)
        duration = time.time() - start
        print(f"Import {module_name}: {duration:.4f}s")
        return duration
    except Exception as e:
        print(f"Failed to import {module_name}: {e}")
        return None

if __name__ == "__main__":
    print("Benchmarking current import times...")
    # These are the main entry points that load services
    benchmark_import('app.services.ai_ingredient_service')
    benchmark_import('app.services.speech_service')
    benchmark_import('app.routes.ai')
    
    # Check the actual heavy libraries too
    benchmark_import('transformers')
    benchmark_import('spacy')
    benchmark_import('faster_whisper')
