import os
import re

TESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests")

ARIA_MODULES = [
    "app_launcher", "aria_core", "brain", "calendar_manager", "clipboard_screenshot",
    "command_intent_classifier", "command_processor", "config", "conversation_manager",
    "deep_work_manager", "email_manager", "file_automation", "file_manager",
    "greeting_service", "logger", "memory_manager", "music_library", "notion_manager",
    "proactive_manager", "search_manager", "speech_engine", "speech_input",
    "system_control", "system_monitor", "tts_manager", "wake_word_listener",
    "water_manager", "weather_manager"
]

def fix_imports_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original_content = content
    
    # Fix: from module import ... -> from aria.module import ...
    for module in ARIA_MODULES:
        # Regex for 'from module import'
        # We use word boundary \b to avoid matching partial names if any
        pattern = fr"from {module}\b"
        replacement = f"from aria.{module}"
        content = re.sub(pattern, replacement, content)
        
        # Fix: import module -> from aria import module
        # This is trickier because 'import module' might be used as 'module.Something'
        # But usually in tests it's 'import module' then 'module.func()'
        # Or 'import module as m'
        # We'll handle 'import module' at start of line
        pattern_import = fr"^import {module}\b"
        replacement_import = f"from aria import {module}"
        content = re.sub(pattern_import, replacement_import, content, flags=re.MULTILINE)

    # Fix handlers
    content = re.sub(r"from handlers\b", "from aria.handlers", content)
    content = re.sub(r"import handlers\b", "from aria import handlers", content)

    if content != original_content:
        print(f"Fixing imports in {filepath}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

def main():
    print(f"Scanning {TESTS_DIR}...")
    for root, dirs, files in os.walk(TESTS_DIR):
        for file in files:
            if file.endswith(".py"):
                fix_imports_in_file(os.path.join(root, file))
    print("Done.")

if __name__ == "__main__":
    main()
