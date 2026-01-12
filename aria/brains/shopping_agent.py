import logging
import webbrowser
import requests
import asyncio
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from aria.search_manager import SearchManager
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

class ShoppingAgent:
    def __init__(self, brain, executor=None):
        self.brain = brain
        self.executor = executor # DesktopExecutor for visual actions
        self.search_manager = SearchManager()
        self.executor = ThreadPoolExecutor(max_workers=5) # Scrape 5 sites at once
        
        # Headers to look like a real browser to avoid 403s
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    async def shop_for(self, product_query: str, on_progress=None):
        """
        Orchestrates the shopping workflow with structured UI updates.
        on_progress: async callback(data: dict)
        """
        async def report(step_id, status, message):
            if on_progress:
                await on_progress({
                    "step_id": step_id,
                    "status": status, # running, completed, etc.
                    "message": message
                })
            logger.info(f"🛒 ShoppingAgent [{step_id}]: {message}")

        # 1. Search
        await report("search", "running", f"Searching for '{product_query}'...")
        
        search_query = f"{product_query} price buy online"
        results = self.search_manager.search(search_query, max_results=10)
        
        if not results:
            await report("search", "failed", "No results found.")
            return "I couldn't find any sites selling that product."
        
        await report("search", "completed", f"Found {len(results)} raw results.")

        # 2. Filter
        await report("filter", "running", "Filtering non-shopping sites...")
        
        urls = [r['url'] for r in results if 'url' in r]
        excluded_domains = [
            "wikipedia.org", "wiktionary.org", "quora.com", "reddit.com", 
            "youtube.com", "pinterest.com", "facebook.com", "instagram.com", 
            "twitter.com", "tiktok.com", "linkedin.com", "cnbc.com", "forbes.com"
        ]
        
        filtered_urls = []
        for url in urls:
            if not any(blocked in url for blocked in excluded_domains):
                filtered_urls.append(url)
                
        unique_urls = list(set(filtered_urls))[:6]
        
        if not unique_urls:
            unique_urls = list(set(urls))[:3]
            await report("filter", "warning", "Aggressive filtering removed all results. Using best guesses.")
        else:
             await report("filter", "completed", f"Selected {len(unique_urls)} stores.")
        
        # 3. Visual Interaction
        await report("visual", "running", "Opening tabs...")
        for url in unique_urls:
             webbrowser.open_new_tab(url)
             await asyncio.sleep(0.5)
        await report("visual", "completed", "Tabs opened.")

        # 4. Scraping
        await report("scrape", "running", "Analyzing page content...")
        
        loop = asyncio.get_running_loop()
        futures = [
            loop.run_in_executor(self.executor, self._scrape_site, url)
            for url in unique_urls
        ]
        
        results = await asyncio.gather(*futures)
        scraped_data = [r for r in results if r]
        
        if not scraped_data:
            await report("scrape", "failed", "Could not extract price data.")
            return "I checked the sites, but couldn't auto-extract pricing."
            
        await report("scrape", "completed", f"Analyzed {len(scraped_data)} pages.")
        
        # 5. Reasoning
        await report("reasoning", "running", "Comparing deals with LLM...")
        
        context_str = ""
        for i, item in enumerate(scraped_data):
            context_str += f"""
            --- Site {i+1} ---
            URL: {item['url']}
            Title: {item['title']}
            Content Snippet: {item['content'][:800]} ...
            ------------------
            """
            
        prompt = f"""
        You are an expert Shopping Assistant.
        The user wants to buy: "{product_query}".
        
        I have scraped {len(scraped_data)} websites.
        Here is the raw data:
        {context_str}
        
        Your Mission:
        1. Identify the EXACT price for the product on each site (if available).
        2. Compare valid offers (Price + Shipping if known + Vendor Reliability).
        3. Select the BEST deal.
        4. Explain your reasoning briefly.
        
        Format your response as a Markdown Report:
        ## 🏆 Recommendation: [Product Name] from [Vendor]
        **Price**: [Price]
        **Reason**: [Why is this the best?]
        
        ## 📊 Comparison
        - **[Vendor 1]**: [Price] - [Notes]
        - **[Vendor 2]**: [Price] - [Notes]
        ...
        
        ## 🔗 Action
        Click the link above to buy.
        """
        
        llm = self.brain.get_llm()
        response = llm.invoke([SystemMessage(content="You are a helpful shopping assistant."), HumanMessage(content=prompt)])
        
        await report("reasoning", "completed", "Recommendation ready.")
        
        # 6. Action (Add to Cart)
        if self.executor:
            # Parse the best deal URL/Title from LLM response (Heuristic for now)
            # OR just default to the first top URL if we are confident.
            # For simplicity, we re-open/focus the BEST visual match or just try to click on the currently focused tab.
            
            await report("action", "running", "Attempting to Add to Cart...")
            
            # Simple heuristic: The LLM usually recommends the first or best one. 
            # We'll just try to find "Add to Cart" on the visible screen.
            
            try:
                # We assume the user is looking at the tabs we opened.
                # We might need to ensure the browser is focused.
                # await self.executor.execute_plan({"actions": [{"action": "focus_window", "params": {"title": "Chrome"}}]}) 
                
                # Try to click common buttons
                buttons = ["Add to Cart", "Add to Bag", "Buy Now", "Purchase"]
                clicked = False
                
                for btn_text in buttons:
                    await report("action", "running", f"Looking for '{btn_text}' button...")
                    plan = {
                        "actions": [{
                            "action": "click_text", 
                            "params": {"text": btn_text}
                        }]
                    }
                    success = await self.executor.execute_plan(plan)
                    if success:
                        await report("action", "completed", f"Clicked '{btn_text}'!")
                        clicked = True
                        break
                
                if not clicked:
                    await report("action", "failed", "Could not find 'Add to Cart' button.")
                    
            except Exception as e:
                logger.warning(f"Auto-Click failed: {e}")
                await report("action", "failed", "Visual automation failed.")

        return response.content

    def _scrape_site(self, url: str):
        """Helper to scrape title and content from a URL."""
        try:
            # Simple fast scrape
            resp = requests.get(url, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Clean up script/style
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                    
                text = soup.get_text(separator=' ', strip=True)
                title = soup.title.string if soup.title else url
                
                return {
                    "url": url,
                    "title": title,
                    "content": text
                }
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
        return None
