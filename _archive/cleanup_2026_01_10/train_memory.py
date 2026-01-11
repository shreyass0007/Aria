import os
import sys
from memory_manager import MemoryManager
from brain import AriaBrain
import uuid

def train_memory():
    print("="*50)
    print("ARIA MEMORY TRAINER")
    print("="*50)
    print("This tool allows you to 'teach' Aria by adding correct examples to its long-term memory.")
    print("When you ask a similar question in the future, Aria will recall this example.")
    print("-" * 50)

    memory = MemoryManager()
    if not memory.is_available():
        print("Error: Memory Manager is not available. Check your API keys.")
        return

    while True:
        print("\nOptions:")
        print("1. Add a new training example")
        print("2. Search existing memory")
        print("3. Clear all memory (WARNING)")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            user_query = input("\nEnter the User Command (e.g., 'open project X'): ").strip()
            if not user_query:
                continue
                
            assistant_response = input("Enter the Correct Response/Action (e.g., 'Opening Project X located at D:/Projects/X'): ").strip()
            if not assistant_response:
                continue
            
            # Create a synthetic conversation entry
            conv_id = "training_data"
            
            # Add user part
            print("Adding user query...")
            memory.add_message(conv_id, user_query, "user")
            
            # Add assistant part
            print("Adding assistant response...")
            memory.add_message(conv_id, assistant_response, "assistant")
            
            print("\n✅ Training example added successfully!")
            
        elif choice == "2":
            query = input("\nEnter search query: ").strip()
            results = memory.search_relevant_context(query, top_k=3)
            
            print(f"\nFound {len(results)} matches:")
            for i, res in enumerate(results):
                print(f"\n[{i+1}] Similarity: {res['similarity']}")
                print(f"Role: {res['role']}")
                print(f"Text: {res['text']}")
                
        elif choice == "3":
            confirm = input("Are you sure you want to delete ALL memory? (yes/no): ").strip().lower()
            if confirm == "yes":
                memory.clear_memory()
                print("Memory cleared.")
            else:
                print("Cancelled.")
                
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    train_memory()
