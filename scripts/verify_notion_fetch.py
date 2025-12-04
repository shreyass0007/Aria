"""
Quick verification test for Notion page fetching
"""

from notion_manager import NotionManager
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("VERIFYING NOTION PAGE FETCHING")
print("="*60)

# Initialize
print("\n1. Initializing Notion Manager...")
notion = NotionManager()

if not notion.client:
    print("❌ ERROR: Notion client not initialized")
    print("   Check your NOTION_API_KEY in .env file")
    exit(1)

print("✅ Notion client initialized")

# Test with the known page ID
page_id = "2940dccd118d80748626ed79a9ec0e3b"

print(f"\n2. Fetching page: {page_id}")
print("   (The Pursuit of Happiness)")

result = notion.get_page_content(page_id)

if result.get("status") == "error":
    print(f"\n❌ ERROR: {result.get('error')}")
    print("\nPossible issues:")
    print("  • Page not shared with your Notion integration")
    print("  • Invalid page ID")
    print("  • API key doesn't have access")
else:
    print(f"\n✅ SUCCESS! Page fetched correctly")
    print(f"\n📊 RESULTS:")
    print(f"   Title: {result.get('title')}")
    print(f"   Word Count: {result.get('word_count')} words")
    print(f"   Content Preview: {result.get('content', '')[:100]}...")
    print(f"\n✅ Notion fetching is working perfectly!")

print("\n" + "="*60)
