"""
Debug Notion search issue
"""

from notion_manager import NotionManager
from brain import AriaBrain
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("DEBUGGING NOTION SEARCH ERROR")
print("="*60)

# Initialize
notion = NotionManager()
brain = AriaBrain()

# Test the exact flow that's failing
text = "summarize notion page The Pursuit of Happiness"

print(f"\n1. Testing LLM extraction...")
print(f"   Command: {text}")

page_info = brain.extract_notion_page_id(text)
print(f"   Result: {page_info}")

if page_info.get("search_query"):
    search_query = page_info["search_query"]
    print(f"\n2. Searching Notion for: '{search_query}'")
    
    try:
        # This is the exact code from aria_core.py
        search_results = notion.client.search(
            query=search_query,
            filter={"property": "object", "value": "page"},
            page_size=5
        ).get("results", [])
        
        print(f"   ✅ Search successful!")
        print(f"   Found {len(search_results)} results")
        
        for i, page in enumerate(search_results, 1):
            props = page.get("properties", {})
            title = "Untitled"
            for prop_name, prop_val in props.items():
                if prop_val.get("type") == "title":
                    title_list = prop_val.get("title", [])
                    if title_list:
                        title = title_list[0].get("text", {}).get("content", "Untitled")
                    break
            print(f"   {i}. {title}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
