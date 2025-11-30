"""
Script to merge new sections into ARIA_USER_MANUAL.md
Inserts the new tutorial sections before the Troubleshooting section
"""

# Read the new sections
with open('USER_MANUAL_NEW_SECTIONS.md', 'r', encoding='utf-8') as f:
    new_content = f.read()

# Extract just the sections (remove the header comments)
lines = new_content.split('\n')
start_idx = 0
for i, line in enumerate(lines):
    if line.strip() == '---' and i > 0:
        start_idx = i
        break

end_idx = len(lines)
for i in range(len(lines) - 1, 0, -1):
    if '# END OF NEW SECTIONS' in lines[i]:
        end_idx = i
        break

new_sections = '\n'.join(lines[start_idx:end_idx])

# Read the original user manual
with open('ARIA_USER_MANUAL.md', 'r', encoding='utf-8') as f:
    original = f.read()

# Find the insertion point (before ## 🔧 Troubleshooting)
insertion_marker = '## 🔧 Troubleshooting'
insertion_idx = original.find(insertion_marker)

if insertion_idx == -1:
    print("ERROR: Could not find Troubleshooting section!")
    exit(1)

# Insert the new sections
updated_content = (
    original[:insertion_idx] +
    new_sections + '\n\n' +
    original[insertion_idx:]
)

# Write the updated manual
with open('ARIA_USER_MANUAL.md', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("✅ Successfully merged new sections into ARIA_USER_MANUAL.md")
print(f"📊 Original lines: {len(original.splitlines())}")
print(f"📊 New lines: {len(updated_content.splitlines())}")
print(f"📊 Added: {len(updated_content.splitlines()) - len(original.splitlines())} lines")
