"""
Quick demo of structured output formatting
"""

# Simulate the structured output that Aria will now display

print("\n" + "="*60)
print("DEMO: New Structured Output Format")
print("="*60 + "\n")

# Example 1: Page Selection
print("EXAMPLE 1: When multiple pages are found")
print("-" * 60)

structured_options = """
🔍 Found 3 pages matching 'meeting notes'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SELECT A PAGE:

1. 📝 Meeting Notes - January 2025
2. 📝 Meeting Notes - February 2025
3. 🗓️ Meeting Notes Archive

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 Reply with the number (1-3)
"""

print(structured_options)
print("\n" + "-" * 60 + "\n")

# Example 2: Summary Output
print("EXAMPLE 2: Summary display")
print("-" * 60)

page_title = "The Pursuit of Happiness"
word_count = 543
summary = """The text challenges the common notion that life is solely about chasing happiness, suggesting instead that true fulfillment comes from experiencing the full spectrum of emotions and life's realities. It argues that happiness is not a singular goal but a byproduct of becoming the best version of oneself through embracing both joy and suffering. The author emphasizes the importance of focusing on personal growth and the inputs one can control, such as effort and mindset, rather than external goals like wealth or success."""

structured_output = f"""
📄 NOTION PAGE SUMMARY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Page: {page_title}
📊 Word Count: {word_count} words
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Summary:
{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print(structured_output)
print("\n" + "-" * 60 + "\n")

print("✅ This is how Aria will now display all Notion outputs!")
print("\nTo see this in action:")
print("1. Make sure your backend is running")
print("2. Type: summarize notion page [your page name]")
print("3. Enjoy the structured output!")
