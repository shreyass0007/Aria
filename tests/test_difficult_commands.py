"""
Difficult Command Test Suite for ARIA LLM Training
Tests edge cases, ambiguity, and complex scenarios
"""

from aria.command_intent_classifier import CommandIntentClassifier
from aria.brain import AriaBrain


class DifficultCommandTester:
    """Test ARIA with challenging commands"""
    
    def __init__(self):
        self.brain = AriaBrain()
        self.classifier = CommandIntentClassifier(self.brain)
        
    def test_command(self, command, expected_intent, description):
        """Test a single command and print results"""
        print(f"\n{'='*70}")
        print(f"TEST: {description}")
        print(f"{'='*70}")
        print(f"Command: \"{command}\"")
        print(f"Expected Intent: {expected_intent}")
        
        result = self.classifier.classify_intent(command)
        
        intent = result.get("intent")
        confidence = result.get("confidence", 0)
        parameters = result.get("parameters", {})
        
        status = " PASS" if intent == expected_intent else " FAIL"
        
        print(f"\nResult:")
        print(f"  Intent: {intent}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Parameters: {parameters}")
        print(f"\n{status}")
        
        return intent == expected_intent
    
    def run_all_tests(self):
        """Run all difficult test scenarios"""
        print("\n" + "="*70)
        print("ARIA DIFFICULT COMMAND TEST SUITE")
        print("="*70)
        
        tests = [
            # ============================================================
            # CATEGORY 1: AMBIGUOUS COMMANDS (Critical Distinctions)
            # ============================================================
            {
                "command": "find python files on my desktop",
                "expected": "file_search",
                "description": "File search vs web search - LOCAL file operation"
            },
            {
                "command": "search for python tutorials online",
                "expected": "web_search",
                "description": "File search vs web search - WEB search"
            },
            {
                "command": "look for resume.pdf in downloads",
                "expected": "file_search",
                "description": "Alternative phrasing for file search"
            },
            {
                "command": "google how to write a resume",
                "expected": "web_search",
                "description": "Clear web search with 'google' keyword"
            },
            
            # ============================================================
            # CATEGORY 2: APP vs WEBSITE CONFUSION
            # ============================================================
            {
                "command": "open chrome browser",
                "expected": "app_open",
                "description": "Desktop application (Chrome app)"
            },
            {
                "command": "open youtube",
                "expected": "web_open",
                "description": "Website (YouTube.com)"
            },
            {
                "command": "launch spotify",
                "expected": "app_open",
                "description": "Desktop application (Spotify app)"
            },
            {
                "command": "open instagram",
                "expected": "web_open",
                "description": "Website (Instagram.com)"
            },
            
            # ============================================================
            # CATEGORY 3: COMPLEX PARAMETER EXTRACTION
            # ============================================================
            {
                "command": "create a file named meeting_notes.txt in the download section",
                "expected": "file_create",
                "description": "File creation with location mapping (download section  downloads)"
            },
            {
                "command": "set my system volume to seventy five percent",
                "expected": "volume_set",
                "description": "Volume with number spelled out (needs extraction)"
            },
            {
                "command": "what's the weather like in new york city",
                "expected": "weather_check",
                "description": "Weather with multi-word city name"
            },
            {
                "command": "copy the text hello world and welcome to aria to my clipboard",
                "expected": "clipboard_copy",
                "description": "Clipboard with long text parameter"
            },
            
            # ============================================================
            # CATEGORY 4: TYPOS AND FUZZY MATCHING
            # ============================================================
            {
                "command": "serch for best laptops 2025",
                "expected": "web_search",
                "description": "Typo: 'serch' should match 'search'"
            },
            {
                "command": "opne calculator",
                "expected": "app_open",
                "description": "Typo: 'opne' should match 'open'"
            },
            {
                "command": "shutdwon the computer",
                "expected": "shutdown",
                "description": "Typo: 'shutdwon' should match 'shutdown'"
            },
            
            # ============================================================
            # CATEGORY 5: NATURAL LANGUAGE VARIATIONS
            # ============================================================
            {
                "command": "could you please increase the volume a bit",
                "expected": "volume_up",
                "description": "Polite/natural phrasing"
            },
            {
                "command": "i need to check how much battery i have left",
                "expected": "battery_check",
                "description": "Conversational style"
            },
            {
                "command": "would you mind organizing my downloads folder",
                "expected": "organize_downloads",
                "description": "Question format"
            },
            {
                "command": "let me know what the CPU usage is",
                "expected": "cpu_check",
                "description": "Indirect request"
            },
            
            # ============================================================
            # CATEGORY 6: MULTI-WORD PARAMETERS
            # ============================================================
            {
                "command": "find all pdf files in my documents folder",
                "expected": "file_search",
                "description": "File search with pattern and location"
            },
            {
                "command": "schedule a team meeting tomorrow at 3 pm",
                "expected": "calendar_create",
                "description": "Calendar with event name and time"
            },
            {
                "command": "send an email to john.doe@example.com about the project update",
                "expected": "email_send",
                "description": "Email with recipient and subject"
            },
            
            # ============================================================
            # CATEGORY 7: EDGE CASES
            # ============================================================
            {
                "command": "take a screenshot of my screen right now",
                "expected": "screenshot_take",
                "description": "Screenshot with redundant words"
            },
            {
                "command": "what is the current time",
                "expected": "time_check",
                "description": "Time check with formal phrasing"
            },
            {
                "command": "tell me today's date",
                "expected": "date_check",
                "description": "Date check with casual phrasing"
            },
            {
                "command": "mute the system audio",
                "expected": "volume_mute",
                "description": "Volume mute with explicit 'system audio'"
            },
            
            # ============================================================
            # CATEGORY 8: SIMILAR SOUNDING COMMANDS
            # ============================================================
            {
                "command": "lock my computer",
                "expected": "lock",
                "description": "Lock (not 'clock')"
            },
            {
                "command": "read the clipboard",
                "expected": "clipboard_read",
                "description": "Read clipboard (not 'clipboard_clear')"
            },
            {
                "command": "clear the clipboard",
                "expected": "clipboard_clear",
                "description": "Clear clipboard (not 'clipboard_read')"
            },
            
            # ============================================================
            # CATEGORY 9: CONTEXT-DEPENDENT COMMANDS
            # ============================================================
            {
                "command": "summarize my notion page about project goals",
                "expected": "notion_query",
                "description": "Notion summarization (not notion_create)"
            },
            {
                "command": "add buy milk to my notion grocery list",
                "expected": "notion_create",
                "description": "Notion creation (not notion_query)"
            },
            
            # ============================================================
            # CATEGORY 10: VERY DIFFICULT / TRICKY
            # ============================================================
            {
                "command": "find the file called search_results.txt",
                "expected": "file_search",
                "description": "TRICKY: File has 'search' in name, but this is file_search not web_search"
            },
            {
                "command": "open the application called browser",
                "expected": "app_open",
                "description": "TRICKY: App named 'browser' (not web_open)"
            },
            {
                "command": "create a new file with notes from the download section",
                "expected": "file_create",
                "description": "TRICKY: Complex phrasing with location ambiguity"
            },
            {
                "command": "what's playing right now",
                "expected": "general_chat",
                "description": "TRICKY: 'playing' keyword but not music_play intent"
            },
        ]
        
        # Run all tests
        passed = 0
        failed = 0
        
        for test in tests:
            result = self.test_command(
                test["command"],
                test["expected"],
                test["description"]
            )
            if result:
                passed += 1
            else:
                failed += 1
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {len(tests)}")
        print(f"Passed: {passed} ({passed/len(tests)*100:.1f}%)")
        print(f"Failed: {failed} ({failed/len(tests)*100:.1f}%)")
        
        if failed == 0:
            print("\n ALL TESTS PASSED! LLM training is excellent!")
        elif passed / len(tests) >= 0.95:
            print("\n EXCELLENT: 95%+ accuracy on difficult commands")
        elif passed / len(tests) >= 0.85:
            print("\n GOOD: 85%+ accuracy, some edge cases need work")
        else:
            print("\n NEEDS IMPROVEMENT: Consider adding failed cases to training data")
        
        return passed, failed


def main():
    """Run the difficult command test suite"""
    tester = DifficultCommandTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
