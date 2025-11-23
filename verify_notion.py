from notion_manager import NotionManager
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_notion():
    with open("verify_output.txt", "w") as f:
        f.write("Testing Notion Integration...\n")
        f.write(f"API Key present: {bool(os.getenv('NOTION_API_KEY'))}\n")
        db_id = os.getenv('NOTION_DATABASE_ID')
        f.write(f"DB ID: {db_id}\n")
        
        try:
            nm = NotionManager()
            if nm.client:
                f.write(f"Client type: {type(nm.client)}\n")
                f.write(f"Pages dir: {dir(nm.client.pages)}\n")
            
            f.write("Fetching pages...\n")
            
            # Try retrieving DB info first
            try:
                db_info = nm.client.databases.retrieve(database_id=db_id)
                f.write(f"DB Retrieve Success: {db_info.get('object')}\n")
            except Exception as e:
                f.write(f"DB Retrieve Failed: {e}\n")

            result = nm.get_pages(num_pages=1)
            f.write(f"Result: {result}\n")
        except Exception as e:
            f.write(f"CRITICAL ERROR: {e}\n")

if __name__ == "__main__":
    test_notion()
