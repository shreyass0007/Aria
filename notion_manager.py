import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

class NotionManager:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        self.client = None
        
        if self.api_key:
            try:
                self.client = Client(auth=self.api_key)
            except Exception as e:
                print(f"Error initializing Notion client: {e}")
        else:
            print("Warning: NOTION_API_KEY not found in environment variables.")

    def search_item(self, query: str, filter_type: str = None):
        """
        Searches for a page or database in Notion.
        filter_type: 'page' or 'database' (optional)
        """
        if not self.client:
            return None

        try:
            params = {
                "query": query,
                "page_size": 1,
            }
            if filter_type:
                params["filter"] = {"value": filter_type, "property": "object"}

            # Use client.search if available, else fallback to request
            if hasattr(self.client, 'search'):
                results = self.client.search(**params).get("results")
            else:
                # Fallback to direct request
                response = self.client.request(
                    path="search",
                    method="POST",
                    body=params
                )
                results = response.get("results")

            if results:
                return results[0]
            return None
        except Exception as e:
            print(f"Search error: {e}")
            return None

    def create_page(self, title, content=None, target_name=None):
        """
        Creates a page (task) in Notion.
        If target_name is provided, searches for that database/page to add to.
        Otherwise, falls back to NOTION_DATABASE_ID.
        """
        if not self.client:
            return "Notion client not initialized. Check API key."
        
        parent_id = self.database_id
        parent_type = "database_id"

        # 1. Search for target if provided
        if target_name:
            print(f"Searching for target: {target_name}")
            target = self.search_item(target_name)
            if target:
                parent_id = target["id"]
                # Check if it's a database or a page
                if target["object"] == "database":
                    parent_type = "database_id"
                else:
                    parent_type = "page_id"
                print(f"Found target: {target.get('title', target.get('properties', {}).get('title', {}))} ({parent_id})")
            else:
                return f"Could not find a page or database named '{target_name}'."
        
        if not parent_id:
            return "No target specified and no default Database ID configured."

        try:
            properties = {}
            # Properties format depends on parent type
            if parent_type == "database_id":
                properties["Name"] = {"title": [{"text": {"content": title}}]}
            else:
                # Adding to a page as a sub-page
                properties["title"] = [{"text": {"content": title}}]

            children = []
            if content:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                })

            self.client.pages.create(
                parent={parent_type: parent_id},
                properties=properties,
                children=children
            )
            target_display = target_name if target_name else "Notion"
            return f"Successfully added '{title}' to {target_display}."
        except Exception as e:
            return f"Failed to create page in Notion: {e}"

    def get_pages(self, num_pages=5, query=None):
        """
        Retrieves recent pages. If query is provided, searches.
        Otherwise lists recently modified.
        """
        if not self.client:
            return "Notion client not initialized."

        try:
            if query:
                # Search mode
                results = self.client.search(query=query, page_size=num_pages).get("results")
                intro = f"Here are results for '{query}':\n"
            else:
                # Recent pages mode (global search with empty query returns recently modified)
                results = self.client.search(page_size=num_pages).get("results")
                intro = "Here are your recent Notion pages:\n"

            if not results:
                return "No pages found."

            pages_text = intro
            for page in results:
                # Extract title safely
                title = "Untitled"
                icon = ""
                
                # Try to get icon
                if page.get("icon") and page["icon"]["type"] == "emoji":
                    icon = page["icon"]["emoji"] + " "
                
                # Try to get title from properties (if database item) or title (if page)
                props = page.get("properties", {})
                
                # Strategy 1: Check for 'Name' or 'title' property
                for prop_name, prop_val in props.items():
                    if prop_val["type"] == "title":
                        title_list = prop_val.get("title", [])
                        if title_list:
                            title = title_list[0].get("text", {}).get("content", "Untitled")
                        break
                
                # Strategy 2: Check for 'title' key directly (some objects)
                # Note: Search results usually have properties.
                
                pages_text += f"- {icon}{title} ({page['object']})\n"
            
            return pages_text
        except Exception as e:
            return f"Error fetching pages: {e}"

    def get_page_content(self, page_id: str) -> dict:
        """
        Fetches the full content of a Notion page.
        Returns a dict with title, content, and status.
        """
        if not self.client:
            return {
                "status": "error",
                "error": "Notion client not initialized."
            }

        try:
            # Clean page ID (remove dashes if present)
            page_id = page_id.replace("-", "")
            
            # Retrieve page metadata
            page = self.client.pages.retrieve(page_id=page_id)
            
            # Extract title
            title = "Untitled"
            props = page.get("properties", {})
            for prop_name, prop_val in props.items():
                if prop_val.get("type") == "title":
                    title_list = prop_val.get("title", [])
                    if title_list:
                        title = title_list[0].get("text", {}).get("content", "Untitled")
                    break
            
            # Fetch all child blocks (the actual content)
            blocks_response = self.client.blocks.children.list(block_id=page_id)
            blocks = blocks_response.get("results", [])
            
            # Extract text from blocks
            content_parts = []
            for block in blocks:
                block_type = block.get("type")
                block_data = block.get(block_type, {})
                
                # Extract rich text from various block types
                if "rich_text" in block_data:
                    rich_text_array = block_data["rich_text"]
                    text = "".join([rt.get("plain_text", "") for rt in rich_text_array])
                    if text.strip():
                        content_parts.append(text)
                
                # Handle special block types
                elif block_type == "child_page":
                    # Skip child pages (we only want this page's content)
                    continue
                elif block_type == "code":
                    rich_text_array = block_data.get("rich_text", [])
                    code_text = "".join([rt.get("plain_text", "") for rt in rich_text_array])
                    if code_text.strip():
                        content_parts.append(f"[Code Block]: {code_text}")
            
            # Combine all content
            full_content = "\n\n".join(content_parts)
            
            if not full_content.strip():
                full_content = "(This page appears to be empty or contains only nested content)"
            
            return {
                "status": "success",
                "title": title,
                "content": full_content,
                "word_count": len(full_content.split())
            }
            
        except Exception as e:
            error_msg = str(e)
            if "Could not find" in error_msg or "not found" in error_msg.lower():
                return {
                    "status": "error",
                    "error": f"Page not found. Make sure the page ID is correct and the page is shared with your integration."
                }
            else:
                return {
                    "status": "error",
                    "error": f"Error fetching page content: {error_msg}"
                }
