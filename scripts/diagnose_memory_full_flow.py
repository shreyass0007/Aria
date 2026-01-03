
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.memory_manager import MemoryManager
from aria.brain import AriaBrain

def diagnose_full_flow():
    print("--- Memory Diagnosis ---")
    
    # 1. Retrieval
    print("\n1. Testing Retrieval...")
    mem = MemoryManager()
    if not mem.is_available():
        print("[FAIL] Memory unavailable.")
        return

    query = "Who is my best friend?"
    # Force threshold Check
    print(f"Current Threshold: {mem.similarity_threshold}")
    
    results = mem.search_relevant_context(query)
    print(f"Results Found: {len(results)}")
    
    context_found = False
    context_data = []
    
    for res in results:
        print(f"  - [{res.get('similarity'):.4f}] {res.get('text')}")
        context_data.append(res)
        if "friend" in res.get('text', '').lower():
            context_found = True
            
    if not context_found:
        print("[FAIL] Relevant memory NOT found in retrieval step.")
        print("Suggestion: Try lowering threshold further or checking embedding consistency.")
        # We continue to test LLM with a FAKE memory to see if Injection works
        print("\n[DEBUG] Injecting FAKE memory to test LLM...")
        context_data = [{"text": "My best friend's name is SUPERMAN_TEST.", "timestamp": "2024-01-01"}]
    else:
        print("[PASS] Relevant memory found.")

    # 2. LLM Generation
    print("\n2. Testing LLM Response (Stream)...")
    brain = AriaBrain()
    
    print("Asking Brain: 'Who is my best friend?' with context.")
    stream = brain.stream_ask(
        query,
        model_name="gpt-4o-mini",
        conversation_history=[],
        long_term_context=context_data
    )
    
    full_response = ""
    for token in stream:
        full_response += token
        
    print(f"\nAI Response: {full_response}")
    
    if "SUPERMAN_TEST" in full_response or "Zarathustra" in full_response:
        print("[PASS] AI used the memory context.")
    else:
        print("[FAIL] AI IGNORED the memory context.")

if __name__ == "__main__":
    diagnose_full_flow()
