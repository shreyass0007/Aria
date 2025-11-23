"""
Test script for Notion Page Summarization feature.
This tests the end-to-end functionality without running the full app.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_notion_summarization():
    """Test the Notion summarization workflow"""
    print("=" * 60)
    print("Testing Notion Page Summarization Feature")
    print("=" * 60)
    
    # Import components
    from notion_manager import NotionManager
    from brain import AriaBrain
    
    # Initialize
    print("\n1. Initializing components...")
    notion = NotionManager()
    brain = AriaBrain()
    
    # Check if initialized
    if not notion.client:
        print("❌ ERROR: Notion client not initialized. Check your NOTION_API_KEY.")
        return False
    
    if not brain.llm:
        print("❌ ERROR: LLM not initialized. Check your OPEN_AI_API_KEY.")
        return False
    
    print("✓ Components initialized successfully")
    
    # Test 1: Search for a page
    print("\n2. Testing page search...")
    search_query = input("Enter a Notion page title to search for (or press Enter to skip): ").strip()
    
    if search_query:
        try:
            results = notion.client.search(
                query=search_query,
                filter={"property": "object", "value": "page"},
                page_size=3
            ).get("results", [])
            
            if results:
                print(f"✓ Found {len(results)} page(s):")
                for i, page in enumerate(results, 1):
                    # Extract title
                    title = "Untitled"
                    props = page.get("properties", {})
                    for prop_name, prop_val in props.items():
                        if prop_val.get("type") == "title":
                            title_list = prop_val.get("title", [])
                            if title_list:
                                title = title_list[0].get("text", {}).get("content", "Untitled")
                            break
                    
                    page_id = page["id"]
                    print(f"  {i}. {title}")
                    print(f"     ID: {page_id}")
                
                # Use the first result for testing
                test_page_id = results[0]["id"]
            else:
                print(f"❌ No pages found matching '{search_query}'")
                test_page_id = input("Enter a page ID manually to continue testing: ").strip()
                if not test_page_id:
                    return False
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return False
    else:
        # Manual page ID input
        test_page_id = input("Enter a Notion page ID to test with: ").strip()
        if not test_page_id:
            print("❌ No page ID provided. Aborting test.")
            return False
    
    # Test 2: Fetch page content
    print(f"\n3. Testing page content extraction...")
    print(f"   Page ID: {test_page_id}")
    
    try:
        page_data = notion.get_page_content(test_page_id)
        
        if page_data.get("status") == "error":
            print(f"❌ Error: {page_data.get('error')}")
            return False
        
        print(f"✓ Page fetched successfully:")
        print(f"  Title: {page_data.get('title')}")
        print(f"  Word Count: {page_data.get('word_count')}")
        print(f"  Content Preview: {page_data.get('content', '')[:200]}...")
        
    except Exception as e:
        print(f"❌ Error fetching page: {e}")
        return False
    
    # Test 3: Summarize content
    print(f"\n4. Testing LLM summarization...")
    
    try:
        content = page_data.get("content", "")
        if len(content) < 50:
            print("⚠️  Content is too short for meaningful summarization")
            print(f"   Content: {content}")
        else:
            summary = brain.summarize_text(content, max_sentences=5)
            print(f"✓ Summary generated:")
            print(f"\n{summary}\n")
    except Exception as e:
        print(f"❌ Error summarizing: {e}")
        return False
    
    # Test 4: Test page ID extraction
    print(f"\n5. Testing page ID extraction from natural language...")
    
    test_commands = [
        "summarize my notion page about project planning",
        "summarize notion page https://notion.so/test-abc123def456789",
        "summarize the meeting notes page"
    ]
    
    for cmd in test_commands:
        try:
            result = brain.extract_notion_page_id(cmd)
            print(f"  Command: '{cmd}'")
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_notion_summarization()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
