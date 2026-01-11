
import sys
import ast

filename = "d:\\CODEING\\PROJECTS\\ARIA\\aria\\command_intent_classifier.py"
try:
    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)
    print("Syntax OK")
except Exception as e:
    print(f"Syntax Error: {e}")
