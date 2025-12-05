from aria.command_intent_classifier import CommandIntentClassifier
from unittest.mock import MagicMock

def test_classifier():
    # Mock Brain to avoid actual LLM calls (or we can let it fail if we want to see LLM behavior, 
    # but here we want to see if our fast path logic works)
    mock_brain = MagicMock()
    mock_brain.is_available.return_value = True
    
    # Mock LLM response to simulate failure if we want, but for now let's just see what happens
    # We'll mock the LLM to return "general_chat" to simulate the user's issue
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = '{"intent": "general_chat", "confidence": 0.5, "parameters": {}}'
    mock_brain.get_llm.return_value = mock_llm

    classifier = CommandIntentClassifier(mock_brain)
    
    test_phrases = [
        "set volume to 50",
        "change volume to 30",
        "volume 80",
        "vset volume 20"
    ]
    
    print("Testing classifier with mocked LLM failure...")
    for phrase in test_phrases:
        result = classifier.classify_intent(phrase)
        print(f"Phrase: '{phrase}' -> Intent: {result['intent']}")

if __name__ == "__main__":
    test_classifier()
