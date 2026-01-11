import json
import uuid
import sys
import os

# Add the current directory to sys.path to ensure we can import aria modules
sys.path.append(os.getcwd())

try:
    from aria.memory_manager import MemoryManager
except ImportError:
    # Fallback if running from root
    try:
        from memory_manager import MemoryManager
    except ImportError:
        print("Error: Could not import MemoryManager. Make sure you are in the project root.")
        sys.exit(1)

def ingest_data(filename="fine_tuning_dataset.jsonl"):
    print(f"Initializing Memory Manager...")
    memory = MemoryManager()
    
    if not memory.is_available():
        print("Error: Memory Manager is not available. Check your API keys and configuration.")
        return

    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.")
        return

    print(f"Reading from {filename}...")
    
    count = 0
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                messages = data.get("messages", [])
                
                user_msg = next((m for m in messages if m["role"] == "user"), None)
                assistant_msg = next((m for m in messages if m["role"] == "assistant"), None)
                
                if user_msg and assistant_msg:
                    # Use a consistent conversation ID for training data
                    conv_id = "training_data_batch_1"
                    
                    # Add user message
                    memory.add_message(conv_id, user_msg["content"], "user")
                    
                    # Add assistant message
                    memory.add_message(conv_id, assistant_msg["content"], "assistant")
                    
                    count += 1
                    if count % 10 == 0:
                        print(f"Ingested {count} examples...", end='\r')
                        
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error processing line: {e}")
                continue
                
    print(f"\n✅ Successfully ingested {count} training examples into local memory.")

if __name__ == "__main__":
    ingest_data()
