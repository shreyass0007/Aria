from search_manager import SearchManager
import datetime

def test_search():
    sm = SearchManager()
    
    # Query 1: Raw user query
    query1 = "yesterday cricket match score ind vs southafrica"
    print(f"--- Query 1: {query1} ---")
    results1 = sm.search(query1)
    print(results1)
    print("\n")

    # Query 2: Date-specific query (calculating yesterday's date)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    date_str = yesterday.strftime("%B %d %Y")
    query2 = f"India vs South Africa cricket match score {date_str}"
    print(f"--- Query 2: {query2} ---")
    results2 = sm.search(query2)
    print(results2)

if __name__ == "__main__":
    test_search()
