from search_manager import SearchManager

def test():
    sm = SearchManager()
    query = "November 30 2025 match score ind vs south afria cricket"
    print(f"Searching for: {query}")
    results = sm.search(query)
    print(f"Results length: {len(results)}")
    print("--- RAW RESULTS START ---")
    print(results)
    print("--- RAW RESULTS END ---")

if __name__ == "__main__":
    test()
