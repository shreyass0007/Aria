from notion_manager import NotionManager
import json

def test_notion_search():
    nm = NotionManager()
    if not nm.client:
        print("Notion client not initialized (check .env)")
        return

    print("Testing search_pages_raw...")
    # Search for something likely to exist or just empty query for recent
    results = nm.search_pages_raw(limit=3)
    
    print(f"Found {len(results)} pages.")
    for i, page in enumerate(results):
        print(f"Page {i+1}: {page['title']} (ID: {page['id']})")
        
    if results:
        print("\nSUCCESS: search_pages_raw returned results.")
    else:
        print("\nWARNING: No results found (might be empty workspace).")

if __name__ == "__main__":
    test_notion_search()
