import sys
import os
sys.path.append(os.getcwd())

print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    print("Attempting to import aria.aria_core...")
    import aria.aria_core
    print("Success!")
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()
