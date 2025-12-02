from search_manager import SearchManager

def test_search():
    print("Testing SearchManager...")
    sm = SearchManager()
    
    query = "current price of bitcoin"
    print(f"Searching for: {query}")
    
    results = sm.search(query)
    
    if results:
        print("\nSUCCESS: Results found!")
        print("-" * 40)
        print(results[:500] + "...") # Print first 500 chars
        print("-" * 40)
    else:
        print("\nFAILURE: No results found.")

if __name__ == "__main__":
    test_search()
