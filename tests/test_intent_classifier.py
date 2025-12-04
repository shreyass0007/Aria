"""
Test script to verify command intent classification
Tests various natural language variations for system commands
"""

from command_intent_classifier import CommandIntentClassifier
from brain import AriaBrain


def test_command_variations():
    """Test the classifier with various command phrasings."""
    
    print("=" * 70)
    print("TESTING COMMAND INTENT CLASSIFIER")
    print("=" * 70)
    
    # Initialize
    brain = AriaBrain()
    if not brain.is_available():
        print("ERROR: Brain/LLM not available. Check your API key.")
        return
    
    classifier = CommandIntentClassifier(brain)
    
    # Define test cases
    test_cases = {
        "Shutdown Commands": [
            "shutdown the computer",
            "turn off the pc",
            "power off my system",
            "turn off computer",
        ],
        "Restart Commands": [
            "restart the computer",
            "reboot system",
            "restart my pc",
        ],
        "Volume Commands": [
            "increase volume",
            "make it louder",
            "turn it up",
            "decrease volume",
            "make it quieter",
            "set volume to 50",
            "volume 75",
            "mute the sound",
            "unmute",
        ],
        "Lock Commands": [
            "lock my screen",
            "lock the computer",
        ],
        "Recycle Bin Commands": [
            "empty the trash",
            "empty recycle bin",
            "check recycle bin size",
        ],
        "Non-System Commands": [
            "what's the weather?",
            "tell me a joke",
            "open youtube",
        ]
    }
    
    # Run tests
    for category, commands in test_cases.items():
        print(f"\n{'─' * 70}")
        print(f"📋 {category}")
        print(f"{'─' * 70}")
        
        for cmd in commands:
            result = classifier.classify_intent(cmd)
            
            # Color coding based on confidence
            confidence = result['confidence']
            if confidence >= 0.8:
                status = "✅ HIGH"
            elif confidence >= 0.7:
                status = "⚠️  GOOD"
            else:
                status = "❌ LOW "
            
            print(f"\n  Command: \"{cmd}\"")
            print(f"   └─ Intent:     {result['intent']:<20} {status} ({confidence:.2f})")
            if result['parameters']:
                print(f"   └─ Parameters: {result['parameters']}")
    
    print(f"\n{'=' * 70}")
    print("✅ Testing Complete!")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    test_command_variations()
