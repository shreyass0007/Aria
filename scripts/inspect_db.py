
import os
import sys

# Ensure we can import from project root if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import chromadb
    print("[PASS] chromadb imported successfully.")
except ImportError as e:
    print(f"[FAIL] Could not import chromadb: {e}")
    sys.exit(1)

try:
    from aria.memory_manager import MemoryManager
    print("[PASS] MemoryManager imported.")
except ImportError as e:
    print(f"[FAIL] Could not import MemoryManager: {e}")

def inspect_db():
    db_path = "./vector_db"
    if not os.path.exists(db_path):
        print(f"[WARN] Database path '{db_path}' does not exist.")
        return

    print(f"Connecting to ChromaDB at {db_path}...")
    try:
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        print(f"Collections found: {[c.name for c in collections]}")
        
        for col in collections:
            print(f"\n--- Collection: {col.name} ---")
            print(f"Count: {col.count()}")
            if col.count() > 0:
                print("Peeking at last 5 items:")
                peek = col.peek(limit=5)
                # Pretty print peek results
                docs = peek.get('documents', [])
                metas = peek.get('metadatas', [])
                for i, doc in enumerate(docs):
                    print(f"  [{i}] Doc: {doc[:100]}...")
                    print(f"      Meta: {metas[i]}")
            else:
                print("  (Empty)")

    except Exception as e:
        print(f"[ERROR] Inspecting DB failed: {e}")

if __name__ == "__main__":
    inspect_db()
