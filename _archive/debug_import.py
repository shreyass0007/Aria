import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")

deps = {
    "pvporcupine": "wake_word",
    "speech_recognition": "speech_input",
    "chromadb": "memory_manager",
    "paddleocr": "vision_ocr"
}

failed = False
for module, feature in deps.items():
    try:
        __import__(module)
        print(f"[OK] {module} imported successfully ({feature})")
    except ImportError as e:
        print(f"[FAIL] {module} not found ({feature}): {e}")
        failed = True
    except Exception as e:
         print(f"[ERROR] Error importing {module}: {e}")
         failed = True

if failed:
    sys.exit(1)
else:
    print("All dependencies verified.")
    sys.exit(0)
