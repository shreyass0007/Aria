import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aria.vision.vision_manager import VisionManager
from aria.brain import AriaBrain

def test_paddle():
    print("[-] Initializing VisionManager...")
    vm = VisionManager()
    
    if vm.use_paddle:
        print("[+] PaddleOCR is ENABLED and initialized.")
    else:
        print("[!] PaddleOCR failed to initialize. Using Tesseract.")
        
    print("[-] Testing OCR (Find 'File')...")
    coords = vm.find_text("File")
    if coords:
        print(f"[+] Found 'File' at {coords}")
    else:
        print("[-] 'File' not found on screen (this might be normal if not visible).")

def test_vision_llm():
    print("\n[-] Testing Llama 3.2 Vision (Local VLM)...")
    brain = AriaBrain()
    vm = VisionManager()
    
    print("[-] Capturing screen...")
    img_b64 = vm.capture_screen_base64()
    
    print("[-] Asking AI to describe screen...")
    response = brain.ask_vision("Describe what you see on this screen in one sentence.", img_b64, model_name="llama3.2-vision")
    
    print(f"\n[AI Response]: {response}")

if __name__ == "__main__":
    print("=== ARIA VISION UPGRADE VERIFICATION ===")
    try:
        test_paddle()
        test_vision_llm()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
    input("\nPress Enter to exit...")
