import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables.")
    exit(1)

print(f"Anthropic API Key found: {api_key[:5]}...{api_key[-4:]}")

models_to_test = [
    "claude-3-haiku-20240307",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229"
]

print("\nTesting models...")

for model in models_to_test:
    print(f"\nTesting {model}...")
    try:
        llm = ChatAnthropic(
            model=model,
            anthropic_api_key=api_key,
            temperature=0.7
        )
        response = llm.invoke("Hello")
        print(f"SUCCESS: {model}")
    except Exception as e:
        print(f"FAILED: {model} - {str(e)[:100]}...")
