import os
import sys
from dotenv import load_dotenv
import openai
import chromadb
from datetime import datetime

# Load environment variables
load_dotenv()

def test_memory_manager():
    print("=== Testing Memory Manager ===")
    
    # 1. Check API Key
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key:
        print("[FAIL] OPEN_AI_API_KEY not found in .env")
        return
    print(f"[PASS] OPEN_AI_API_KEY found: {api_key[:5]}...")
    
    # 2. Initialize ChromaDB
    try:
        db_path = os.getenv("CHROMADB_PATH", "./vector_db")
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(
            name="aria_conversations_v2",
            metadata={"hnsw:space": "cosine", "description": "Long-term conversation memory for Aria"}
        )
        print(f"[PASS] ChromaDB initialized at {db_path}")
        print(f"[INFO] Current message count: {collection.count()}")
    except Exception as e:
        print(f"[FAIL] ChromaDB initialization failed: {e}")
        return

    # 3. Test Embedding
    print("\n--- Testing Embedding ---")
    try:
        openai.api_key = api_key
        test_text = "This is a test memory."
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=test_text
        )
        embedding = response.data[0].embedding
        print(f"[PASS] Generated embedding (length: {len(embedding)})")
    except Exception as e:
        print(f"[FAIL] Embedding generation failed: {e}")
        return

    # 4. Test Storage
    print("\n--- Testing Storage ---")
    try:
        test_id = f"test_{datetime.utcnow().timestamp()}"
        collection.add(
            ids=[test_id],
            embeddings=[embedding],
            documents=[test_text],
            metadatas=[{"conversation_id": "test_conv", "role": "user", "timestamp": datetime.utcnow().isoformat()}]
        )
        print(f"[PASS] Stored test message with ID: {test_id}")
    except Exception as e:
        print(f"[FAIL] Storage failed: {e}")
        return

    # 5. Test Retrieval
    print("\n--- Testing Retrieval ---")
    try:
        query_text = "test memory"
        query_response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        query_embedding = query_response.data[0].embedding
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=1
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            retrieved_doc = results['documents'][0][0]
            distance = results['distances'][0][0]
            similarity = 1 - distance
            print(f"[PASS] Retrieved: '{retrieved_doc}' (Similarity: {similarity:.3f})")
        else:
            print("[FAIL] No results found")
            
    except Exception as e:
        print(f"[FAIL] Retrieval failed: {e}")

if __name__ == "__main__":
    test_memory_manager()
