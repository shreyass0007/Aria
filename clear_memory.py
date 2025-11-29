from memory_manager import MemoryManager
import sys

def clear_rag_memory():
    print("Initializing Memory Manager...")
    mgr = MemoryManager()
    
    if not mgr.is_available():
        print("Memory Manager is not available. Check configuration.")
        return
    
    print("Clearing Long-Term Memory (Vector DB)...")
    success = mgr.clear_memory()
    
    if success:
        print("✅ Memory successfully cleared!")
    else:
        print("❌ Failed to clear memory.")

if __name__ == "__main__":
    # Ask for confirmation
    response = input("Are you sure you want to clear ALL long-term memory? (y/n): ")
    if response.lower() == 'y':
        clear_rag_memory()
    else:
        print("Operation cancelled.")
