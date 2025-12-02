from search_manager import SearchManager
import os
from dotenv import load_dotenv

# Explicitly load .env for this script since it's standalone
load_dotenv()

def test_tavily():
    print("--- Testing Tavily Search Integration ---")
    
    # Check API Key
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ ERROR: TAVILY_API_KEY not found in environment.")
        return

    print(f"✅ API Key found: {api_key[:5]}...{api_key[-4:]}")

    sm = SearchManager()
    
    # Test Query
    query = "India vs South Africa cricket match score Nov 30 2025"
    print(f"\nSearching for: {query}")
    
    results = sm.search(query)
    
    print("\n--- Search Results ---")
    print(results)
    
    if "Error" in results:
        print("\n❌ Search Failed.")
    elif not results:
        print("\n⚠️ No results returned.")
    else:
        print("\n✅ Search Successful!")

if __name__ == "__main__":
    test_tavily()
