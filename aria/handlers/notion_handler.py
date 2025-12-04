from typing import Dict, Any, Optional, List
from .base_handler import BaseHandler
from ..logger import setup_logger

logger = setup_logger(__name__)

class NotionHandler(BaseHandler):
    def __init__(self, tts_manager, notion_manager, brain):
        super().__init__(tts_manager)
        self.notion = notion_manager
        self.brain = brain
        self.pending_notion_pages: Optional[List[Dict]] = None

    def should_handle(self, intent: str) -> bool:
        return intent in ["notion_query", "notion_create"]

    def has_pending_interaction(self) -> bool:
        return self.pending_notion_pages is not None

    def handle_interaction(self, text: str, extra_data: Dict = None) -> Optional[str]:
        """Handles page selection logic."""
        if not self.pending_notion_pages:
            return None
            
        try:
            selection = None
            number_words = {
                "first": 1, "one": 1, "1": 1,
                "second": 2, "two": 2, "2": 2,
                "third": 3, "three": 3, "3": 3,
                "fourth": 4, "four": 4, "4": 4,
                "fifth": 5, "five": 5, "5": 5
            }
            
            for word, num in number_words.items():
                if word in text:
                    selection = num
                    break
            
            if selection and 1 <= selection <= len(self.pending_notion_pages):
                selected_page = self.pending_notion_pages[selection - 1]
                page_id = selected_page["id"]
                page_title = selected_page["title"]
                
                self.pending_notion_pages = None
                
                self.tts_manager.speak(f"Great! Fetching {page_title}...")
                page_data = self.notion.get_page_content(page_id)
                
                if page_data.get("status") == "error":
                    self.tts_manager.speak(page_data.get("error", "Unable to fetch the page."))
                    return "Error fetching page."
                
                content = page_data.get("content", "")
                self.tts_manager.speak(f"Summarizing {page_title}...")
                summary = self.brain.summarize_text(content, max_sentences=5)
                
                word_count = page_data.get("word_count", 0)
                structured_output = f"""## 📄 Notion Page Summary

**Page:** {page_title}  
**Word Count:** {word_count} words

---

### 💡 Summary
{summary}

---
"""
                self.tts_manager.speak(structured_output)
                return structured_output
            else:
                self.tts_manager.speak("I didn't understand your selection. Please say a number like 'one', 'two', or 'three'.")
                return "Invalid selection. Please try again."
                
        except Exception as e:
            logger.error(f"Error processing selection: {e}")
            self.pending_notion_pages = None
            self.tts_manager.speak("Sorry, I had trouble with that. Let's start over.")
            return "Error processing selection."

    def handle(self, text: str, intent: str, parameters: Dict[str, Any]) -> Optional[str]:
        if intent == "notion_query":
            if "summarize" in text or "summary" in text:
                page_info = self.brain.extract_notion_page_id(text)
                search_query = page_info.get("search_query")
                
                if not search_query:
                    search_query = text.replace("summarize", "").replace("summary", "").replace("page", "").replace("about", "").replace("of", "").strip()
                
                if search_query:
                    self.tts_manager.speak(f"Searching Notion for '{search_query}'...")
                    results = self.notion.search_pages_raw(search_query)
                    
                    if not results:
                        self.tts_manager.speak("No pages found.")
                        return "No pages found."
                    
                    if len(results) == 1:
                        page_id = results[0]["id"]
                        page_title = results[0]["title"]
                        self.tts_manager.speak(f"Found {page_title}. Summarizing...")
                        
                        page_data = self.notion.get_page_content(page_id)
                        content = page_data.get("content", "")
                        summary = self.brain.summarize_text(content, max_sentences=5)
                        
                        word_count = page_data.get("word_count", 0)
                        structured_output = f"""## 📄 Notion Page Summary

**Page:** {page_title}  
**Word Count:** {word_count} words

---

### 💡 Summary
{summary}

---
"""
                        self.tts_manager.speak(structured_output)
                        return structured_output
                    else:
                        self.pending_notion_pages = results
                        
                        # Aggregate list into a single message
                        message = f"I found {len(results)} pages. Which one?\n\n"
                        for i, page in enumerate(results):
                            message += f"{i+1}. {page['title']}\n"
                            
                        self.tts_manager.speak(message)
                        return message
                else:
                    self.tts_manager.speak("What page should I summarize?")
            return None

        elif intent == "notion_create":
            self.tts_manager.speak("Analyzing your request...")
            details = self.brain.parse_notion_intent(text)
            
            title = details.get("title")
            content = details.get("content", "")
            target = details.get("target")
            
            if title:
                self.tts_manager.speak(f"Creating page '{title}'...")
                result = self.notion.create_page(title, content, target)
                self.tts_manager.speak(result)
                return result
            else:
                self.tts_manager.speak("I couldn't understand what page to create. Please specify a title.")
                return "Missing title for Notion page."
        
        return None
