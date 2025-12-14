import chromadb
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

def inspect_chroma():
    output_file = r"C:\Users\shrey\.gemini\antigravity\brain\0adf49df-e45a-4fc1-802a-c43cfb4da0a0\chroma_data.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== Inspecting ChromaDB Data ===\n\n")
        
        db_path = os.getenv("CHROMADB_PATH", "./vector_db")
        if not os.path.exists(db_path):
            f.write(f"Error: Database path '{db_path}' does not exist.\n")
            return

        try:
            client = chromadb.PersistentClient(path=db_path)
            
            # List all collections
            collections = client.list_collections()
            f.write(f"Found {len(collections)} collections:\n")
            for col in collections:
                f.write(f"- {col.name}\n")
                
            # Inspect specific collection
            collection_name = "aria_conversations_v2"
            try:
                collection = client.get_collection(collection_name)
                count = collection.count()
                f.write(f"\nCollection: '{collection_name}'\n")
                f.write(f"Total Documents: {count}\n")
                
                if count > 0:
                    # Get all data
                    result = collection.get()
                    
                    f.write("\n--- Full Data Dump ---\n")
                    for i in range(len(result['ids'])):
                        f.write(f"ID: {result['ids'][i]}\n")
                        f.write(f"Document: {result['documents'][i]}\n")
                        f.write(f"Metadata: {result['metadatas'][i]}\n")
                        f.write("-" * 50 + "\n")
                        
                else:
                    f.write("Collection is empty.\n")
                    
            except Exception as e:
                f.write(f"Error accessing collection '{collection_name}': {e}\n")

        except Exception as e:
            f.write(f"Error connecting to ChromaDB: {e}\n")
            
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    inspect_chroma()
