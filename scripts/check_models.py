from aria_core import AriaCore
import os
from dotenv import load_dotenv

load_dotenv()

def check_models():
    print("--- Checking Available Models ---")
    aria = AriaCore()
    models = aria.brain.get_available_models()
    print(f"Available Models Count: {len(models)}")
    for model in models:
        print(f" - {model['id']} ({model['name']})")

    print("\n--- Checking GPT-5 Status ---")
    print(f"GPT-5: {aria.brain.llm_gpt_5}")
    print(f"GPT-5 Mini: {aria.brain.llm_gpt_5_mini}")

if __name__ == "__main__":
    check_models()
