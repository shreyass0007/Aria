import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain import AriaBrain
from command_intent_classifier import CommandIntentClassifier

def test_classifier():
    print("Initializing Brain...")
    brain = AriaBrain()
    if not brain.is_available():
        print("ERROR: Brain not available (check API key). Cannot test.")
        return

    classifier = CommandIntentClassifier(brain)
    
    test_cases = [
        ("Open YouTube", "web_open"),
        ("Play some jazz music", "music_play"),
        ("Search for python tutorials", "web_search"),
        ("Find resume.pdf on desktop", "file_search"),
        ("Schedule a meeting tomorrow at 10am", "calendar_create"),
        ("What is on my calendar?", "calendar_query"),
        ("Summarize my notion page about goals", "notion_query"),
        ("Add milk to grocery list in Notion", "notion_create"),
        ("Turn up the volume", "volume_up"),
        ("Shut down the computer", "shutdown"),
        ("Tell me a joke", "general_chat"),
        ("Who are you?", "general_chat"),
        ("Open Calculator", "app_open"),
        ("What time is it?", "time_check")
    ]
    
    print("\nRunning Classification Tests...")
    print("=" * 60)
    
    passed = 0
    for text, expected_intent in test_cases:
        print(f"\nInput: '{text}'")
        result = classifier.classify_intent(text)
        intent = result["intent"]
        confidence = result["confidence"]
        params = result["parameters"]
        
        print(f"  -> Intent: {intent} (Expected: {expected_intent})")
        print(f"  -> Confidence: {confidence}")
        print(f"  -> Params: {params}")
        
        if intent == expected_intent:
            print("  [PASS]")
            passed += 1
        else:
            print(f"  [FAIL] Expected {expected_intent}, got {intent}")
            
    print("=" * 60)
    print(f"Passed {passed}/{len(test_cases)} tests.")

if __name__ == "__main__":
    test_classifier()
