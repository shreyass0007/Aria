
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("[FAIL] No ANTHROPIC_API_KEY found in environment.")
    exit(1)

print(f"[OK] Found Anthropic API Key: {api_key[:5]}...{api_key[-4:]}")

models_to_test = [
    "claude-3-haiku-20240307",
    "claude-3-5-sonnet-20240620",
    "claude-3-opus-20240229"
]

print("\nTesting Model Access:")
print("-" * 30)

for model in models_to_test:
    print(f"Testing {model}...", end=" ", flush=True)
    try:
        llm = ChatAnthropic(model=model, anthropic_api_key=api_key, max_tokens=10)
        llm.invoke("Hello")
        print("[OK]")
    except Exception as e:
        print("[FAIL]")
        # print(f"   Error: {e}") # Print error details if needed

print("-" * 30)
