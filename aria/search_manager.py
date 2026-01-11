import logging
import os
from tavily import TavilyClient

class SearchManager:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            logging.warning("TAVILY_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, max_results: int = 5) -> str:
        """
        Searches Tavily for the query and returns a formatted string of results.
        """
        if not self.client:
            return "Error: TAVILY_API_KEY is missing. Please add it to your environment variables."

        try:
            print(f"DEBUG: Tavily searching: {query}")
            # Use search_depth="advanced" for better results
            response = self.client.search(query, search_depth="advanced", max_results=max_results)
            results = response.get("results", [])
            
            print(f"DEBUG: Tavily results count: {len(results)}")
            
            if not results:
                return []

            # Return raw list of dicts for the processor to handle
            # We filter/clean if necessary
            cleaned_results = []
            for result in results:
                cleaned_results.append({
                    "title": result.get('title', 'No Title'),
                    "content": result.get('content', 'No Content'),
                    "url": result.get('url', '#')
                })
            
            return cleaned_results
        except Exception as e:
            print(f"ERROR: Tavily search exception: {e}")
            logging.error(f"Error performing search: {e}")
            return []
