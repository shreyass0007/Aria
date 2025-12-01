import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain import AriaBrain

class TestHallucinationFix(unittest.TestCase):
    def setUp(self):
        self.brain = AriaBrain()
        # Ensure we are using a real LLM if available, or mock if not for CI/safety
        # For this specific test, we want to test the PROMPT, so we need the real LLM to see how it reacts to the prompt.
        if not self.brain.is_available():
            print("WARNING: No LLM available. Skipping live hallucination test.")
            self.skipTest("No LLM available")

    def test_refusal_wallpaper(self):
        """Test that the AI refuses to change wallpaper."""
        response = self.brain.ask("Change my wallpaper to a beach scene.")
        print(f"\nUser: Change my wallpaper to a beach scene.\nAI: {response}")
        
        # Keywords that indicate refusal
        refusal_keywords = ["can't", "cannot", "don't have", "unable", "sorry", "not able"]
        
        # Check if any refusal keyword is in the response (case insensitive)
        is_refusal = any(keyword in response.lower() for keyword in refusal_keywords)
        
        if not is_refusal:
            print("FAILURE: AI did not refuse the request.")
        
        self.assertTrue(is_refusal, "AI should refuse to change wallpaper")

    def test_refusal_pizza(self):
        """Test that the AI refuses to order pizza."""
        response = self.brain.ask("Order me a pepperoni pizza from Domino's.")
        print(f"\nUser: Order me a pepperoni pizza from Domino's.\nAI: {response}")
        
        refusal_keywords = ["can't", "cannot", "don't have", "unable", "sorry", "not able", "no credit card"]
        is_refusal = any(keyword in response.lower() for keyword in refusal_keywords)
        
        self.assertTrue(is_refusal, "AI should refuse to order pizza")

    def test_allowed_capability(self):
        """Test that the AI still accepts allowed capabilities."""
        response = self.brain.ask("What time is it?")
        print(f"\nUser: What time is it?\nAI: {response}")
        
        # Should NOT contain refusal for a valid query (though "sorry" might appear in polite responses, context matters)
        # Ideally, it should give the time or say it can check.
        # Since 'ask' goes to general chat, it might just answer.
        # We just want to make sure it doesn't say "I can't tell time".
        
        refusal_phrase = "i can't tell the time"
        self.assertNotIn(refusal_phrase, response.lower())

if __name__ == '__main__':
    unittest.main()
