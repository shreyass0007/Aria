import chromadb
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

def inspect_chroma():
    print("=== Inspecting ChromaDB Data ===")
    
    db_path = os.getenv("CHROMADB_PATH", "./vector_db")
    if not os.path.exists(db_path):
        print(f"Error: Database path '{db_path}' does not exist.")
        return

    try:
        client = chromadb.PersistentClient(path=db_path)
        
        # List all collections
        collections = client.list_collections()
        print(f"\nFound {len(collections)} collections:")
        for col in collections:
            print(f"- {col.name}")
            
        # Inspect specific collection
        collection_name = "aria_conversations_v2"
        try:
            collection = client.get_collection(collection_name)
            count = collection.count()
            print(f"\nCollection: '{collection_name}'")
            print(f"Total Documents: {count}")
            
            if count > 0:
                # Get all data
                result = collection.get()
                
                # Create DataFrame for better visualization
                data = []
                for i in range(len(result['ids'])):
                    item = {
                        'ID': result['ids'][i],
                        'Document': result['documents'][i],
                        'Metadata': result['metadatas'][i]
                    }
                    data.append(item)
                
                df = pd.DataFrame(data)
                
                # Adjust display settings
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', 1000)
                pd.set_option('display.max_colwidth', 50)
                
                print("\n--- Data Preview (Last 20 items) ---")
                print(df.tail(20))
                
                print("\n--- Full Data Dump (ID | Document | Metadata) ---")
                for index, row in df.iterrows():
                    print(f"ID: {row['ID']}")
                    print(f"Doc: {row['Document']}")
                    print(f"Meta: {row['Metadata']}")
                    print("-" * 50)
                    
            else:
                print("Collection is empty.")
                
        except Exception as e:
            print(f"Error accessing collection '{collection_name}': {e}")

    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")

if __name__ == "__main__":
    inspect_chroma()
