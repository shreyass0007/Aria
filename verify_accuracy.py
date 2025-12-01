import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain import AriaBrain
from command_intent_classifier import CommandIntentClassifier

class TestAccuracyEnhancement(unittest.TestCase):
    def setUp(self):
        self.brain = AriaBrain()
        self.classifier = CommandIntentClassifier(self.brain)
        
        if not self.brain.is_available():
            print("WARNING: No LLM available. Skipping live accuracy test.")
            self.skipTest("No LLM available")

    def test_refusal_wallpaper(self):
        """Test refusal for wallpaper change (General Chat)."""
        response = self.brain.ask("Change my wallpaper to a beach scene.")
        print(f"\n[Wallpaper] User: Change my wallpaper to a beach scene.\nAI: {response}")
        
        refusal_keywords = ["can't", "cannot", "don't have", "unable", "sorry", "not able", "settings"]
        is_refusal = any(keyword in response.lower() for keyword in refusal_keywords)
        self.assertTrue(is_refusal, "AI should refuse to change wallpaper")

    def test_refusal_pizza(self):
        """Test refusal for ordering food (General Chat)."""
        response = self.brain.ask("Order me a pepperoni pizza.")
        print(f"\n[Pizza] User: Order me a pepperoni pizza.\nAI: {response}")
        
        refusal_keywords = ["can't", "cannot", "don't have", "unable", "sorry", "not able", "no credit card"]
        is_refusal = any(keyword in response.lower() for keyword in refusal_keywords)
        self.assertTrue(is_refusal, "AI should refuse to order pizza")

    def test_refusal_screen_vision(self):
        """Test refusal for seeing screen without screenshot."""
        response = self.brain.ask("Can you see what's on my screen right now?")
        print(f"\n[Vision] User: Can you see what's on my screen right now?\nAI: {response}")
        
        refusal_keywords = ["can't", "cannot", "don't have", "unable", "sorry", "screenshot", "no eyes"]
        is_refusal = any(keyword in response.lower() for keyword in refusal_keywords)
        self.assertTrue(is_refusal, "AI should refuse to see screen without screenshot")

    def test_intent_classification_wallpaper(self):
        """Test that 'change wallpaper' goes to general_chat, NOT some random intent."""
        result = self.classifier.classify_intent("Change my wallpaper")
        print(f"\n[Intent] 'Change my wallpaper' -> {result['intent']}")
        self.assertEqual(result['intent'], "general_chat")

    def test_intent_classification_install(self):
        """Test that 'install python' goes to general_chat."""
        result = self.classifier.classify_intent("Install Python for me")
        print(f"\n[Intent] 'Install Python for me' -> {result['intent']}")
        self.assertEqual(result['intent'], "general_chat")

    def test_intent_classification_valid(self):
        """Test that a valid command is still classified correctly."""
        result = self.classifier.classify_intent("Open YouTube")
        print(f"\n[Intent] 'Open YouTube' -> {result['intent']}")
        self.assertEqual(result['intent'], "web_open")

if __name__ == '__main__':
    unittest.main()
