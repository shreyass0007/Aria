# Test UI Formatting - Code Blocks

## Test Messages for Aria

Send these messages to Aria to test the code block formatting:

### 1. Python Example
"Show me a Python hello world program"

Expected response should include:
```python
print("Hello, World!")
```

### 2. JavaScript Example
"Write a JavaScript function to add two numbers"

Expected response should include:
```javascript
function add(a, b) {
    return a + b;
}
```

### 3. HTML Example
"Give me basic HTML structure"

Expected response should include:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Page Title</title>
</head>
<body>
    <h1>Hello</h1>
</body>
</html>
```

### 4. CSS Example
"Show me CSS for a button"

Expected response should include:
```css
.button {
    background: #4f46e5;
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
}
```

### 5. Inline Code Example
"What is the `useState` hook in React?"

Expected: Should have `useState` styled as inline code

### 6. Mixed Content
"Explain how to use fetch in JavaScript with an example"

Expected: Text explanation with code block example

## What to Verify

✅ **Code blocks display with:**
- Language label in header (e.g., "PYTHON", "JAVASCRIPT")
- Copy button with icon
- Syntax highlighting (colored keywords)
- Glassmorphism container styling
- Proper spacing and padding

✅ **Copy button functionality:**
- Hover effect shows accent color
- Click shows "Copied!" with checkmark
- Actually copies code to clipboard
- Reverts after 2 seconds

✅ **Theme compatibility:**
- Test in all 4 color themes
- Test in light mode and dark mode
- Verify colors adapt appropriately

✅ **Inline code:**
- Displays with accent background
- Monospace font
- Distinct from code blocks
