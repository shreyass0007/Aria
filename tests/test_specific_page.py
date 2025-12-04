"""
Quick test for a specific Notion page - saves output to file
"""

from notion_manager import NotionManager
from brain import AriaBrain
from dotenv import load_dotenv
import sys

load_dotenv()

# Redirect output to file
output_file = open("test_output.txt", "w", encoding="utf-8")
sys.stdout = output_file

# The page URL provided by user
page_url = "https://www.notion.so/The-Pursuit-of-Happiness-2940dccd118d80748626ed79a9ec0e3b?source=copy_link"

print("=" * 70)
print("Testing Notion Summarization on: The Pursuit of Happiness")
print("=" * 70)

# Initialize
notion = NotionManager()
brain = AriaBrain()

# Extract page ID from URL
import re
match = re.search(r'([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', page_url)
if match:
    page_id = match.group(1).replace('-', '')
    print(f"\nExtracted Page ID: {page_id}")
else:
    print("\nERROR: Could not extract page ID from URL")
    output_file.close()
    exit(1)

# Fetch page content
print(f"\nFetching page content...")
page_data = notion.get_page_content(page_id)

if page_data.get("status") == "error":
    print(f"\nERROR: {page_data.get('error')}")
    print("\nMake sure the page is shared with your Notion integration!")
    output_file.close()
    exit(1)

print(f"\nPage retrieved successfully!")
print(f"Title: {page_data.get('title')}")
print(f"Word Count: {page_data.get('word_count')}")

content = page_data.get('content', '')
print(f"\n{'='*70}")
print("FULL CONTENT:")
print(f"{'='*70}")
print(content)
print(f"{'='*70}")

# Generate summary
print(f"\nGenerating AI summary...")
summary = brain.summarize_text(content, max_sentences=5)

print(f"\n{'='*70}")
print("AI SUMMARY:")
print(f"{'='*70}")
print(summary)
print(f"{'='*70}")

print(f"\nSTATS:")
print(f"  Original: {page_data.get('word_count')} words")
print(f"  Summary: {len(summary.split())} words")
print(f"  Compression: {100 - (len(summary.split()) / page_data.get('word_count', 1) * 100):.1f}%")

print("\nTest completed successfully!")

output_file.close()

# Print to console
print("Output saved to test_output.txt", file=sys.__stdout__)
