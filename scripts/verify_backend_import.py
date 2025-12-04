import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Importing backend_fastapi...")
    import backend_fastapi
    print("backend_fastapi imported successfully.")
except Exception as e:
    print(f"Failed to import backend_fastapi: {e}")
    import traceback
    traceback.print_exc()
