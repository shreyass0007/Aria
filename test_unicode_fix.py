"""
Test Unicode safety in console output
"""
import sys
import io

# Simulate a console that can't handle emojis (like Windows cp1252)
class RestrictedConsole(io.TextIOWrapper):
    def write(self, s):
        try:
            # Try to encode to ascii, which will fail for emojis
            s.encode('ascii')
            super().write(s)
        except UnicodeEncodeError:
            raise UnicodeEncodeError('charmap', s, 0, 1, 'character maps to <undefined>')

# Test the safe print logic
def safe_print(text):
    try:
        # Simulate the error
        if any(ord(c) > 127 for c in text):
            raise UnicodeEncodeError('charmap', text, 0, 1, 'character maps to <undefined>')
        print(f"Aria said: {text}")
    except UnicodeEncodeError:
        # This is the fix we implemented
        print(f"Aria said: {text.encode('ascii', 'replace').decode()}")

print("1. Testing normal text...")
safe_print("Hello World")

print("\n2. Testing text with emojis...")
safe_print("🔍 Found 5 pages matching 'happiness'")

print("\n3. Testing structured output...")
structured_output = """
📄 NOTION PAGE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Page: The Pursuit of Happiness
"""
safe_print(structured_output)

print("\n✅ Test completed!")
