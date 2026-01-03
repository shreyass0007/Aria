
import sys
import os
import time

# Ensure aria is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.memory_manager import MemoryManager

def check_ltm_retrieval():
    print("Initializing MemoryManager...")
    try:
        memory_manager = MemoryManager()
    except Exception as e:
        print(f"[ERROR] Failed to init MemoryManager: {e}")
        return

    if not memory_manager.is_available():
        print("[ERROR] MemoryManager is not available (check logs).")
        return

    print(f"\nStats: {memory_manager.get_stats()}")
    
    # Test Queries
    queries = [
        "What is my name?",
        "What did we talk about?",
        "Hello",
        "secret code"
    ]
    
    print("\n--- Testing Retrieval ---")
    for q in queries:
        print(f"\nQuery: '{q}'")
        start = time.time()
        results = memory_manager.search_relevant_context(q)
        duration = time.time() - start
        
        print(f"Time: {duration:.4f}s")
        print(f"Found {len(results)} relevant memories:")
        for i, res in enumerate(results):
            # Print similarity score and preview
            print(f"  [{i+1}] (Score: {res.get('similarity', 0)}) {res.get('text', '')[:100]}...")
            
if __name__ == "__main__":
    check_ltm_retrieval()
