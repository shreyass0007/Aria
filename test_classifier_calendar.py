
from command_intent_classifier import CommandIntentClassifier
from brain import AriaBrain

def test_classifier():
    brain = AriaBrain()
    classifier = CommandIntentClassifier(brain)
    
    queries = [
        "what do i have to do today ?",
        "what's on my agenda",
        "do i have any plans",
        "am i busy tomorrow"
    ]
    
    print("Testing Classifier...")
    for q in queries:
        result = classifier.classify_intent(q)
        print(f"Query: '{q}' -> Intent: {result['intent']} (Conf: {result['confidence']})")

if __name__ == "__main__":
    test_classifier()
