import os
import re

TESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests")

def remove_non_ascii(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace non-ascii characters with nothing or a placeholder
    # We'll keep basic latin1 if possible, but simplest is to strip anything > 127
    # But wait, some strings might be important.
    # Emojis are usually in high unicode range.
    
    # Regex to find non-ascii
    # [^\x00-\x7F] matches any character that is not in the ASCII range
    
    new_content = re.sub(r'[^\x00-\x7F]+', '', content)
    
    if content != new_content:
        print(f"Cleaning {filepath}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

def main():
    print(f"Scanning {TESTS_DIR}...")
    for root, dirs, files in os.walk(TESTS_DIR):
        for file in files:
            if file.endswith(".py"):
                remove_non_ascii(os.path.join(root, file))
    print("Done.")

if __name__ == "__main__":
    main()
