
import json
import collections

# Load the dataset
dataset_path = "fine_tuning_dataset.jsonl"
print(f"Loading dataset from {dataset_path}...")

try:
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = [json.loads(line) for line in f]
except Exception as e:
    print(f"FATAL: Failed to load dataset: {e}")
    exit(1)

print(f"Loaded {len(dataset)} examples.")

# Check for formatting issues
format_errors = collections.defaultdict(int)

for ex in dataset:
    if not isinstance(ex, dict):
        format_errors["data_type"] += 1
        continue
        
    messages = ex.get("messages", None)
    if not messages:
        format_errors["missing_messages_list"] += 1
        continue
        
    for message in messages:
        if "role" not in message or "content" not in message:
            format_errors["message_missing_key"] += 1
        
        if message.get("role") not in ("system", "user", "assistant", "function"):
            format_errors["unknown_role"] += 1
            
        content = message.get("content", None)
        if not content or not isinstance(content, str):
            format_errors["missing_content"] += 1

if format_errors:
    print("\n❌ Found formatting errors:")
    for k, v in format_errors.items():
        print(f"{k}: {v}")
    exit(1)
else:
    print("\n✅ No formatting errors found.")

# Check for invalid JSON in assistant responses (since we are training it to output JSON)
json_errors = 0
for i, ex in enumerate(dataset):
    messages = ex["messages"]
    assistant_msg = next((m for m in reversed(messages) if m["role"] == "assistant"), None)
    
    if assistant_msg:
        content = assistant_msg.get("content", "")
        try:
            json.loads(content)
        except json.JSONDecodeError:
            json_errors += 1
            print(f"Warning: Assistant output in example {i+1} is not valid JSON.")

if json_errors > 0:
    print(f"\n⚠️ Found {json_errors} examples with invalid JSON in assistant response.")
else:
    print("\n✅ All assistant responses are valid JSON.")
