from notion_manager import NotionManager
import os
from dotenv import load_dotenv

load_dotenv()

def test_search():
    nm = NotionManager()
    print("Testing Notion Search...")
    
    # Test 1: Global Search (Recent)
    print("\n--- Recent Pages ---")
    recent = nm.get_pages(num_pages=3)
    print(recent)

    # Test 2: Specific Search (if any)
    # We'll try searching for "Task" or "Note" which are common
    print("\n--- Search 'DATA SCIENCE' ---")
    search_res = nm.search_item("DATA SCIENCE")
    if search_res:
        print(f"Found: {search_res.get('id')} - {search_res.get('object')}")
        
        # Test 3: Add to Target
        print("\n--- Add to 'DATA SCIENCE' ---")
        res = nm.create_page("Test Task from Aria", "This is a test.", target_name="DATA SCIENCE")
        print(res)
    else:
        print("No results for 'DATA SCIENCE'")

if __name__ == "__main__":
    test_search()
