
import os
import sys

file_path = r"d:\CODEING\PROJECTS\ARIA\verify_output.txt"

try:
    # Try utf-16 first as PowerShell > redirects often use it
    with open(file_path, "r", encoding="utf-16") as f:
        print(f.read())
except UnicodeError:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading file: {e}")
except Exception as e:
    print(f"Error: {e}")
