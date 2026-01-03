
import sys
import os
import time

# Ensure aria is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.memory_manager import MemoryManager

def debug_friend_memory():
    print("Initializing MemoryManager...")
    try:
        memory = MemoryManager()
    except Exception as e:
        print(f"[FAIL] Init failed: {e}")
        return

    if not memory.is_available():
        print("[FAIL] Memory not available.")
        return

    # 1. Store a test fact
    test_friend = "Zarathustra"
    fact = f"My best friend's name is {test_friend}."
    print(f"\n[Action] Storing fact: '{fact}'")
    
    success = memory.add_message("debug_session", fact, "user")
    if success:
        print("[PASS] Fact stored.")
    else:
        print("[FAIL] Could not store fact.")
        return

    # 2. Wait for indexing
    print("Waiting for indexing...")
    time.sleep(1)

    # 3. Retrieve
    query = "Who is my best friend?"
    print(f"\n[Action] Querying: '{query}'")
    
    results = memory.search_relevant_context(query)
    
    found = False
    print(f"Found {len(results)} results:")
    for res in results:
        score = res.get('similarity', 0)
        text = res.get('text', '')
        print(f"  - [{score:.4f}] {text}")
        if test_friend in text:
            found = True

    if found:
        print(f"\n[SUCCESS] Retrieved friend name '{test_friend}'.")
    else:
        print(f"\n[FAIL] Did NOT retrieve friend name '{test_friend}'.")
        print("Possible causes: Similarity threshold too high, or embedding mismatch.")

if __name__ == "__main__":
    debug_friend_memory()
