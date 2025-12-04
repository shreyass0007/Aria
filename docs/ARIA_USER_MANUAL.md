# 📘 Aria - Complete User Manual
### *Your Personal AI Desktop Assistant - Tutorial Guide*

> **Welcome!** This comprehensive guide will walk you through every feature of Aria, your advanced AI assistant. Whether you're new to Aria or looking to master advanced features, this tutorial-style manual has you covered.

---

## 📑 Table of Contents

1. [Introduction](#-introduction)
2. [Getting Started](#-getting-started)
3. [Basic Features](#-basic-features---your-first-steps)
4. [Voice Control](#%EF%B8%8F-voice-control---hands-free-operation)
5. [Desktop Control](#-desktop-control)
6. [Web Browsing](#-web-browsing--search)
7. [File Management](#-file-management)
8. [System Control](#-system-control)
9. [Clipboard & Screenshots](#-clipboard--screenshots)
10. [System Monitoring](#-system-monitoring)
11. [Weather Information](#%EF%B8%8F-weather-information)
12. [Calendar Management](#-calendar-management)
13. [Notion Integration](#-notion-integration)
14. [File Automation](#-file-automation)
15. [Conversation Features](#-conversation-features)
16. [RAG Memory System](#-rag-memory-system)
17. [Proactive Actions & Automation](#-proactive-actions--automation)
18. [Background Services](#-background-services)
19. [Settings & Customization](#%EF%B8%8F-settings--customization)
20. [Troubleshooting](#-troubleshooting)
21. [Tips & Tricks](#-tips--tricks)
22. [FAQ](#-faq)

---

## 🌟 Introduction

### What is Aria?

Aria is a premium, local-first AI assistant that combines the power of advanced language models (GPT-4o) with deep system integration. Unlike cloud-only assistants, Aria gives you:

- **🎙️ Voice Control** - Wake-word activation and natural speech processing
- **🖥️ System Integration** - Control apps, files, and system settings
- **🧠 AI Intelligence** - Powered by OpenAI's GPT-4o for natural conversations
- **🧠 RAG Memory** - Remembers context from ALL past conversations via semantic search
- **🤖 Proactive Actions** - Calendar monitoring with smart automation and app launching
- **📡 Background Services** - Health monitoring and intelligent event reminders
- **📅 Productivity** - Calendar scheduling, Notion notes, file organization
- **🎨 Beautiful UI** - Modern Electron interface with light/dark themes
- **🔒 Privacy-First** - Runs locally with your own API keys

### Who is Aria For?

- **Power Users** who want voice-controlled productivity
- **Developers** who need a coding companion
- **Busy Professionals** managing calendars and notes
- **Anyone** who wants a smarter desktop experience

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:

| Requirement | Details |
|------------|---------|
| **Operating System** | Windows 10/11 (tested) |
| **Python** | Version 3.10+ |
| **Node.js** | Version 18+ |
| **Microphone** | For voice input |
| **Speakers** | For audio responses |
| **OpenAI API Key** | Required for AI features |

### Installation

#### Step 1: Set Up Python Environment

```powershell
# Navigate to the Aria folder
cd D:\CODEING\PROJECTS\ARIA

# Create a virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```env
OPEN_AI_API_KEY=sk-your-openai-api-key-here
OPENWEATHER_API_KEY=your-weather-api-key-here (optional)
NOTION_API_KEY=your-notion-key-here (optional)
NOTION_DATABASE_ID=your-database-id-here (optional)
USER_NAME=Your Name (optional)
```

> **💡 Tip:** Get your OpenAI API key from [platform.openai.com](https://platform.openai.com)

#### Step 3: Install Electron Dependencies

```powershell
cd electron
npm install
```

#### Step 4: Launch Aria!

**Option A: Electron UI (Recommended)**
```powershell
cd electron
npm start
```

**Option B: CustomTkinter UI**
```powershell
.venv\Scripts\activate
python gui.py
```

**Option C: Command Line**
```powershell
.venv\Scripts\activate
python main.py
```

### First Launch

When you first launch Aria:
1. **Type in the input box**: `What time is it?`
2. **Press Enter** or click the send button
3. **Aria responds**: With the current time and speaks it aloud

**What just happened?**
- Aria processed your text command
- Checked the system time
- Responded in both text (UI) and voice (TTS)

### Tutorial 2: Wake Word Activation

**Try voice control:**

1. **Click the microphone icon** 🎙️ in the UI
2. **Say**: "Aria" (the wake word)
3. **Aria responds**: With a personalized greeting
4. **Now say a command**: "What's today's date?"

**Wake Word Tips:**
- Speak clearly in a quiet environment
- Wait for Aria's response before the next command
- You can change the wake word (see Customization section)

### Tutorial 3: Simple Conversations

**Aria can chat naturally:**

```
You: "Tell me a joke"
Aria: [Responds with a joke]

You: "Explain quantum computing in simple terms"
Aria: [Provides a clear explanation]

You: "Write a short poem about rain"
Aria: [Creates a poem]
```

**Pro Tip:** Aria remembers context within a conversation!

---

## 🎙️ Voice Control - Hands-Free Operation

### Understanding Voice Mode

Aria has **two voice modes**:

1. **Wake Word Mode** - Always listening for "Aria"
2. **Command Mode** - After wake word, listens for your command

### Voice Command Structure

**Pattern 1: Direct Commands**
```
"Aria, open Chrome"
"Aria, what's the weather?"
"Aria, set volume to 50"
```

**Pattern 2: Natural Language**
```
"Aria, can you tell me what time is it?"
"Aria, I need to schedule a meeting tomorrow at 3 PM"
"Aria, organize my downloads folder please"
```

### Voice Settings

**Adjusting Speech Recognition:**

The app auto-adjusts to ambient noise, but you can tweak:
- Speak 2-3 feet from the microphone
- Reduce background noise
- Speak at a normal pace (not too fast/slow)

**Text-to-Speech (TTS) Control:**

By default, Aria speaks all responses. To disable:
- This feature can be toggled in settings (future feature)

---

## 🖥️ Desktop Control

### Opening Applications

Aria can open any installed application on your Windows PC.

#### Tutorial 4: Launch Apps by Voice

**Basic Examples:**
```
"Aria, open Chrome"
"Aria, launch VS Code"
"Aria, open Calculator"
"Aria, start Spotify"
"Aria, open Notion"
```

**How it works:**
1. Aria indexes your Start Menu shortcuts
2. Uses fuzzy matching to find apps
3. Handles variations (e.g., "chrome" finds "Google Chrome")

**Smart Matching:**
```
❌ "open browser" - Too generic
✅ "open chrome" - Specific app name
✅ "open google chrome" - Full name works
✅ "open figma" - Partial match works
```

#### Tutorial 5: Opening Multiple Things

**Chain commands naturally:**
```
You: "Aria, open VS Code and Chrome"
Aria: [Opens VS Code first, then Chrome]
```

### What Apps Can Aria Open?

- **Browsers**: Chrome, Firefox, Edge, Brave
- **Development**: VS Code, PyCharm, Git, Terminal
- **Productivity**: Notion, Obsidian, Excel, Word
- **Communication**: Discord, Slack, Teams, Zoom
- **Media**: Spotify, VLC, Photos
- **Any app** in your Start Menu!

---

## 🌐 Web Browsing & Search

### Opening Websites

#### Tutorial 6: Quick Website Access

**Popular Sites (Pre-configured):**
```
"Aria, open YouTube"
"Aria, open Instagram"
"Aria, open Gmail"
"Aria, open Twitter"
"Aria, open LinkedIn"
"Aria, open GitHub"
```

**Custom Sites:**
```
"Aria, open reddit.com"
"Aria, open stackoverflow.com"
"Aria, open bbc.co.uk"
```

### Google Search

#### Tutorial 7: Search the Web

**Simple Searches:**
```
"Aria, search for Python tutorials"
"Aria, Google latest AI news"
"Aria, search best restaurants near me"
```

**Complex Queries:**
```
"Aria, search for how to fix Python import errors"
"Aria, Google best laptops under $1000 2025"
```

**What happens:**
- Aria opens Google in your default browser
- Search results appear automatically
- You can continue browsing normally

### YouTube & Media

**Play Music/Videos:**
```
"Aria, play lofi music"
"Aria, play Python tutorial"
"Aria, search YouTube for cooking recipes"
```

---

## 📁 File Management

Aria includes a powerful file manager with CRUD operations.

### File Search

#### Tutorial 8: Finding Files

**Basic Search:**
```
"Aria, search for aria_logo on downloads"
"Aria, find presentation in documents"
"Aria, search for *.pdf on desktop"
```

**How it works:**
- Searches specified location (downloads, desktop, documents)
- Supports wildcards (* for any characters)
- Returns file location and info

**Location Keywords:**
- `desktop` - Your Desktop folder
- `downloads` - Downloads folder
- `documents` - Documents folder
- `pictures` - Pictures folder
- `music` - Music folder

### File Creation

#### Tutorial 9: Create a File

**Simple Creation:**
```
"Aria, create a file called notes.txt"
→ Creates notes.txt on Desktop

"Aria, create todo.txt with content 'Buy groceries'"
→ Creates file with initial content
```

### File Reading

**Read File Contents:**
```
"Aria, read notes.txt"
→ Reads and speaks the file content

"Aria, read todo.txt from desktop"
→ Reads specific file
```

**Limits:**
- Files over 1MB are skipped (too large)
- Shows first 50 lines by default
- UTF-8 text files only

### File Information

**Get File Details:**
```
"Aria, get info on report.pdf"
→ Shows: Location, Size, Modified Date

OUTPUT:
report.pdf
Location: C:\Users\YourName\Desktop
Size: 2.45 MB
Modified: 2025-11-22 14:30:15
```

### File Operations

**More Commands:**
```
"Aria, append to notes.txt 'Meeting at 3 PM'"
→ Adds content to end of file

"Aria, rename notes.txt to important_notes.txt"
→ Renames the file

"Aria, copy report.pdf to documents"
→ Copies file to new location

"Aria, move screenshot.png to pictures"
→ Moves file
```

> **⚠️ Safety Note:** Deletion requires manual confirmation for safety

---

## 🎛️ System Control

### Volume Control

#### Tutorial 10: Manage System Volume

**Check Volume:**
```
"Aria, what's the volume?"
"Aria, check volume"
→ "System volume is at 60%"
```

**Set Specific Level:**
```
"Aria, set volume to 50"
"Aria, volume 75"
→ "Volume set to 50%"
```

**Increase/Decrease:**
```
"Aria, increase volume"
"Aria, turn up volume"
"Aria, louder"
→ "Volume increased to 70%"

"Aria, decrease volume"
"Aria, quieter"
→ "Volume decreased to 40%"
```

**Mute/Unmute:**
```
"Aria, mute system"
→ "System muted"

"Aria, unmute"
→ "System unmuted"
```

### Power Management

#### Tutorial 11: Power Controls

> **⚠️ Important:** Shutdown/Restart have 10-second safety timers!

**Lock Screen:**
```
"Aria, lock the system"
"Aria, lock computer"
→ Locks immediately
```

**Sleep Mode:**
```
"Aria, put computer to sleep"
"Aria, sleep system"
→ Enters sleep mode
```

**Shutdown:**
```
"Aria, shutdown computer"
→ "Shutting down in 10 seconds. Say 'cancel shutdown' to abort."

[Wait 10 seconds OR cancel]
"Aria, cancel shutdown"
→ "Shutdown cancelled"
```

**Restart:**
```
"Aria, restart computer"
→ "Restarting in 10 seconds. Say 'cancel restart' to abort."
```

### System Maintenance

#### Tutorial 12: Recycle Bin Management

**Check Recycle Bin:**
```
"Aria, check recycle bin"
→ "Recycle bin contains 23 items (145.67 MB)"
```

**Empty Recycle Bin:**
```
"Aria, empty recycle bin"
→ "Recycle bin contains 23 items (145.67 MB). Emptying it now..."
→ "Recycle bin emptied successfully"
```

### Clipboard & Screenshot Management

#### Tutorial 13: Clipboard Operations

**Copy Text to Clipboard:**
```
"Aria, copy hello world to clipboard"
→ "Copied to clipboard: hello world"

"Aria, copy my email address is aria@example.com"
→ Copies the specified text

"Aria, copy meeting at 3 PM tomorrow"
→ Quick text capture
```

**Read Clipboard:**
```
"Aria, read clipboard"
"Aria, what's in the clipboard?"
→ "Clipboard contains: [your copied text]"
```

**Clear Clipboard:**
```
"Aria, clear clipboard"
→ "Clipboard cleared successfully"
```

**Use Cases:**
- Quick note capture without opening apps
- Voice-to-text for other applications (copy then paste)
- Temporary storage for information

#### Tutorial 14: Take Screenshots

**Basic Screenshot:**
```
"Aria, take a screenshot"
→ "Screenshot saved to C:\Users\YourName\Desktop\Screenshots\screenshot_20251123_193500.png"
```

**Custom Filename:**
```
"Aria, take screenshot called project_demo"
→ "Screenshot saved to C:\Users\YourName\Desktop\Screenshots\project_demo.png"

"Aria, take screenshot called bug_report"
→ Custom naming for organization
```

**Screenshot Features:**
- Captures entire screen
- Auto-saves to Desktop/Screenshots folder
- Automatic timestamp naming (YYYYMMDD_HHMMSS)
- Or use custom names for easy identification
- PNG format for best quality

**Best Practices:**
```
✅ "take screenshot called meeting_notes"  
✅ "screenshot project_dashboard"
✅ "capture screen as error_message"

❌ Don't include file extensions (.png)
   Aria adds it automatically
```

**Screenshot Location:**
All screenshots are saved to:
```
C:\Users\[YourName]\Desktop\Screenshots\
```

The folder is created automatically if it doesn't exist.

### System Monitoring

#### Tutorial 15: Battery Status

**Check Battery:**
```
"Aria, check battery"
"Aria, what's my battery percentage?"
"Aria, battery status"
```

**Example Response:**
```
🔋 Battery: 85%
⚡ Charging
⏱️ Time to full charge: 45 minutes
```

**On Desktop** (no battery):
```
→ "No battery detected. This appears to be a desktop computer."
```

#### Tutorial 16: CPU Monitoring

**Check CPU Usage:**
```
"Aria, check CPU"
"Aria, CPU usage"
"Aria, how much CPU am I using?"
```

**Example Response:**
```
💻 CPU Usage: 23%
📊 Status: Low usage
⚡ Frequency: 3.40 GHz
```

**Status Levels:**
- Low usage: < 30%
- Moderate usage: 30-70%
- High usage: > 70%

#### Tutorial 17: RAM Monitoring

**Check RAM Usage:**
```
"Aria, check RAM"
"Aria, memory usage"
"Aria, how much RAM am I using?"
```

**Example Response:**
```
🧠 RAM Usage: 8.5 GB / 16 GB (53%)
📊 Status: Moderate
✅ Available: 7.5 GB
```

#### Tutorial 18: All System Stats

**Get Complete Overview:**
```
"Aria, system stats"
"Aria, check system status"
"Aria, system information"
```

**Example Response:**
```
📊 SYSTEM STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔋 Battery: 85% (⚡ Charging)
💻 CPU: 23%
🧠 RAM: 8.5 GB / 16 GB (53%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Use Cases:**
- Monitor system health during intensive tasks
- Check battery before unplugging laptop
- Identify high CPU/RAM usage
- Quick system overview

---

## ☁️ Weather Information

### Getting Weather Updates

#### Tutorial 13: Check the Weather

**Default Location (Pimpri, India):**
```
"Aria, what's the weather?"
"Aria, check weather"
→ Provides current weather for default location
```

**Specific City:**
```
"Aria, what's the weather in London?"
"Aria, check weather in New York"
"Aria, weather in Tokyo"
```

**Weather Response Format:**
```
📍 Weather in London
🌡️ Temperature: 15°C (Feels like 13°C)
☁️ Conditions: Partly cloudy
💨 Wind: 12 km/h
💧 Humidity: 65%

💡 It's a bit cloudy today. Maybe grab a light jacket just in case!
```

### Weather Advice

Aria provides context-aware advice:
- ☔ **Rain** - "Don't forget your umbrella!"
- ☀️ **Sunny** - "Apply sunscreen!"
- ❄️ **Snow** - "Bundle up and drive carefully!"
- 🌫️ **Fog** - "Poor visibility, drive slowly!"

**Setup (Optional):**
Get a free API key from [OpenWeatherMap](https://openweathermap.org/) and add to `.env`:
```env
OPENWEATHER_API_KEY=your-key-here
```

---

## 📅 Calendar Management

### Google Calendar Integration

#### Setup Google Calendar

1. **Enable Google Calendar API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Calendar API

2. **Get Credentials**
   - Create OAuth 2.0 credentials (Desktop App)
   - Download as `credentials.json`
   - Place in Aria's root folder

3. **First Authorization**
   - Run Aria
   - Browser window opens
   - Grant calendar permissions
   - `token.pickle` is saved for future use

#### Tutorial 14: Schedule Events

**Simple Scheduling:**
```
"Aria, schedule a meeting tomorrow at 3 PM"
→ Aria: "Checking calendar..."
→ Creates "Meeting" event tomorrow at 3 PM

"Aria, schedule standup on Monday at 9 AM"
→ Creates recurring standup meeting
```

**Detailed Events:**
```
"Aria, schedule team review next Friday at 2 PM for 2 hours"
→ Creates 2-hour event

"Aria, schedule doctor appointment on December 1st at 10 AM"
→ Specific date scheduling
```

#### Check Your Schedule

**View Upcoming Events:**
```
"Aria, what do I have today?"
"Aria, what's my schedule?"
"Aria, show upcoming events"
→ Lists next 5 calendar events
```

**Example Output:**
```
📅 UPCOMING EVENTS:
━━━━━━━━━━━━━━━━━━━━
1. Team Standup
   🕐 Nov 23, 2025 at 9:00 AM

2. Client Meeting  
   🕐 Nov 23, 2025 at 2:00 PM
   
3. Code Review
   🕐 Nov 24, 2025 at 11:00 AM
━━━━━━━━━━━━━━━━━━━━
```

---

## 📝 Notion Integration

### Setup Notion

#### Getting Notion API Access

1. **Create Integration**
   - Go to [Notion Integrations](https://www.notion.so/my-integrations)
   - Click "New Integration"
   - Name it "Aria"
   - Copy the API key

2. **Add to .env:**
```env
NOTION_API_KEY=secret_your-key-here
```

3. **Share Pages with Aria**
   - Open any Notion page
   - Click "..." → "Add connections"
   - Select "Aria"

> See [NOTION_SETUP.md](NOTION_SETUP.md) for detailed instructions

### Using Notion

#### Tutorial 15: Search Notion Pages

**List Pages:**
```
"Aria, list my Notion pages"
→ Shows recently modified pages
```

**Search:**
```
"Aria, search Notion for Project Alpha"
→ Finds pages matching "Project Alpha"
```

#### Add Content to Notion

**Quick Capture:**
```
"Aria, add to Grocery List buy milk and bread"
→ Finds "Grocery List" page and adds content

"Aria, add a note to Daily Journal had a great meeting today"
→ Appends to journal page
```

**Create New Pages:**
```
"Aria, create a Notion page called Meeting Notes"
→ Creates new page in your workspace
```

#### Summarize Notion Pages

**Get Page Summary:**
```
"Aria, summarize Project Alpha from Notion"
→ Aria: "Searching Notion..."
→ [Shows matching pages]
→ You: "First one"
→ Aria: "Fetching Project Alpha..."
→ [Displays summary]
```

**Example Summary:**
```
📄 NOTION PAGE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Page: Project Alpha
📊 Word Count: 523 words
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Summary:
Project Alpha is focused on developing a new AI-powered feature...
[Condensed summary of page content]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🗂️ File Automation

### Smart Folder Organization

Aria can automatically organize messy folders by file type.

#### Tutorial 16: Organize Downloads

**Organize Downloads:**
```
"Aria, organize my downloads"
"Aria, clean up downloads folder"
```

**What happens:**
1. Aria scans your Downloads folder
2. Creates category subfolders:
   - 📄 Documents (PDF, DOCX, TXT, etc.)
   - 🖼️ Images (JPG, PNG, GIF, etc.)
   - 🎵 Audio (MP3, WAV, FLAC, etc.)
   - 🎬 Videos (MP4, AVI, MKV, etc.)
   - 📦 Archives (ZIP, RAR, 7Z, etc.)
   - 💾 Other (Everything else)
3. Moves files into appropriate folders

**Organize Desktop:**
```
"Aria, organize my desktop"
"Aria, clean up desktop"
→ Same organization for Desktop folder
```

**Result:**
```
✨ Downloads organized!
━━━━━━━━━━━━━━━━━━━━
📄 Documents: 15 files
🖼️ Images: 42 files
🎵 Audio: 8 files
🎬 Videos: 3 files
📦 Archives: 6 files
━━━━━━━━━━━━━━━━━━━━
Total: 74 files organized
```

### Smart Archiving (Advanced)

Future feature for automatically archiving old files!

---

## 💬 Conversation Features

### Context Awareness

Aria remembers your conversation context:

```
You: "What's the capital of France?"
Aria: "The capital of France is Paris."

You: "What's the population?"
Aria: "Paris has a population of approximately 2.1 million..."
[Aria knows you mean Paris!]
```

### Multi-turn Dialogues

```
You: "Tell me about Python"
Aria: [Explains Python programming]

You: "How do I install it?"
Aria: [Provides installation steps]

You: "Show me a hello world example"
Aria: [Shows code example]
```

### Markdown Formatting

Aria's responses support rich formatting:

- **Bold text** for emphasis
- *Italic text* for subtle points
- `Code blocks` for technical terms
- Lists and bullet points
- Headers and sections

### Time-Based Greetings

Aria greets you based on the time of day:

**Morning (5 AM - 12 PM):**
```
"Good morning! Ready to make today productive?"
"Rise and shine! What's on the agenda?"
```

**Afternoon (12 PM - 5 PM):**
```
"Good afternoon! How can I help?"
"Hope your day is going well!"
```

**Evening (5 PM - 9 PM):**
```
"Good evening! Time to wind down?"
"Evening! What can I do for you?"
```

**Night (9 PM - 5 AM):**

**Default:** "Aria"

**Change it:**
```
"Aria, change wake word to Neo"
→ "Wake word changed to Neo"

[Now use:]
"Neo, what time is it?"
```

**Popular Alternatives:**
- Jarvis
- Computer
- Hey Assistant
- Your choice!

### Theme Switching

**UI Themes:**
- Light Mode 🌞
- Dark Mode 🌙

**Switch in the GUI:**
1. Click the theme toggle button (top-right)
2. Theme preference is saved locally

### TTS (Text-to-Speech) Settings

Currently enabled by default. Future updates will add:
- Voice selection
- Speech rate control
- Volume adjustment
- Enable/disable toggle

### Customizing Music Library

Edit `music_library.py`:

```python
music = {
    "lofi": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    "chill": "https://open.spotify.com/playlist/...",
    "workout": "https://youtu.be/...",
    # Add your favorites!
}
```

Now say:
```
"Aria, play lofi"
→ Opens your custom lofi link
```

---

---

## 🧠 RAG Memory System

### What is RAG Memory?

RAG (Retrieval-Augmented Generation) Memory allows Aria to remember and search through **ALL** your past conversations, not just the current one. It's like giving Aria a perfect long-term memory!

**How It Works:**
- Every message you send is converted into a "semantic embedding" (meaning-based fingerprint)
- These embeddings are stored in a vector database (ChromaDB)
- When you ask something, Aria searches for relevant past conversations
- The most relevant context is automatically injected into the current response

### Tutorial: Experiencing RAG in Action

**Scenario 1: Restaurant Recommendations**

```
Week 1:
You: "Aria, I loved that Italian place - Mario's Bistro on 5th Street"
Aria: "Glad you enjoyed it! I'll remember that."

Week 3 (different conversation):
You: "Aria, what was that restaurant I mentioned?"
Aria: "You mentioned loving Mario's Bistro on 5th Street! 
       Would you like directions or want to make a reservation?"
```

**What Just Happened?**
- Aria searched across ALL conversations (not just current one)
- Found semantically similar content about restaurants
- Retrieved the specific restaurant name from weeks ago
- Provided contextual response with that information

### Tutorial: Asking About Past Conversations

**Work-Related:**
```
You: "What was that project deadline we discussed last month?"
Aria: [Searches past conversations for deadline mentions]
→ Returns relevant context from previous discussions
```

**Personal Notes:**
```
You: "Did I mention my doctor's appointment date?"
Aria: [Finds past mention in conversation history]
→ "Yes, you scheduled it for December 15th at 2 PM"
```

**Study Topics:**
```
You: "What did we discuss about quantum physics?"
Aria: [Retrieves relevant past conversations]
→ Summarizes previous discussions on the topic
```

### When RAG Memory is Most Helpful

✅ **Great Use Cases:**
- Recalling recommendations (restaurants, books, movies, products)
- Finding past decisions or commitments
- Retrieving information you shared weeks/months ago
- Understanding long-term context and preferences
- Continuing topics from previous conversations
- Remembering personal details you've mentioned

❌ **Not Needed For:**
- Current conversation context (handled by conversation history)
- Real-time facts (Aria doesn't store external web information)
- Web searches (use search commands instead)
- File contents (Aria remembers file operations, not file data)

### Privacy & Data

**What's Stored:**
- Your messages (user) and Aria's responses (assistant)
- Semantic embeddings (mathematical representations of meaning)
- Conversation IDs and timestamps
- Message metadata

**What's NOT Stored:**
- External web content
- Actual file contents (only file operations)
- API keys or sensitive credentials
- Passwords or authentication tokens

**Storage Location:**
All RAG data is stored locally on your computer in:
```
D:\CODEING\PROJECTS\ARIA\vector_db\
```

This folder contains the ChromaDB database. You can delete it anytime to clear all memory.

### Configuration Options

The RAG system uses these settings (configured in `memory_manager.py`):

| Setting | Default Value | Description |
|---------|---------------|-------------|
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model used |
| `SIMILARITY_THRESHOLD` | `0.4` | Minimum similarity score (0.0-1.0) |
| `MAX_LONG_TERM_RESULTS` | `5` | Number of past memories to inject |

**To Adjust Settings:**

Edit your `.env` file:
```env
EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.4
MAX_LONG_TERM_RESULTS=5
```

**Understanding Similarity Threshold:**
- Lower (e.g., 0.3) = More permissive, retrieves loosely related memories
- Higher (e.g., 0.6) = More strict, only very similar matches
- Default 0.4 = Good balance for most use cases

### Managing Your Memory

**View Memory Statistics:**
Currently stored in `memory_manager.py`. You can check:
- Total messages stored
- Embedding model used
- Current configuration

**Clear All Memories:**
```powershell
python clear_memory.py
```

This resets the vector database completely.

**⚠️ Note:** Clearing memory is permanent! Your conversation history in MongoDB remains intact.

---

## 🤖 Proactive Actions & Automation

### What are Proactive Actions?

Proactive Actions make Aria act **before** you ask! When certain events appear in your calendar, Aria automatically:
- Launches relevant applications
- Enables Do Not Disturb mode
- Sends you timely reminders
- Minimizes distracting apps

**It's like having a proactive assistant who knows your schedule and prepares everything for you!**

### Tutorial 22: Calendar-Triggered Actions

**Scenario: Zoom Meeting Auto-Launch**

**Step 1: Create a calendar event**
```
Event Title: "Zoom Standup @ 10 AM"
Date: Tomorrow
Time: 10:00 AM
```

**Step 2: What happens automatically**
```
At 9:55 AM (5 minutes before):
- Aria speaks: "You have a Zoom meeting in 5 minutes. Opening Zoom."
- Zoom application launches automatically
- You're ready when the meeting starts!
```

**How It Works:**
1. Proactive Manager checks your Google Calendar every 60 seconds
2. Detects the keyword "zoom" in the event title
3. Triggers the action 5 minutes before event starts
4. Launches Zoom application
5. Marks event as "reminded" so it never reminds twice

### Supported Keywords & Automatic Actions

| Keyword in Event Title | What Aria Does |
|------------------------|----------------|
| `zoom` | Opens Zoom application + reminder |
| `teams` | Opens Microsoft Teams + reminder |
| `meet` or `google meet` | Opens browser to meet.google.com |
| `discord` | Opens Discord application |
| `coding` or `dev` | Opens VS Code |
| `focus time` | **Activates Deep Work Mode** |
| `gym` or `workout` | Announces workout time |

### Tutorial 23: Deep Work Mode

**Scenario: Protecting Your Focus Time**

**Step 1: Create a Focus Time event**
```
Event Title: "Focus Time - Write Report"
Date: Today
Time: 2:00 PM - 4:00 PM
```

**Step 2: At 2:00 PM (event starts) - Automatic Actions**
```
Aria announces:
"Focus Time detected. Activating Deep Work mode."

What happens:
✅ Windows Do Not Disturb (DND) enabled
✅ Distracting apps minimized (Discord, Spotify, etc.)
✅ Notifications silenced
✅ Full focus environment created
```

**Step 3: At 4:00 PM (event ends) - Automatic Deactivation**
```
Aria announces:
"Focus Time ended. Deactivating Deep Work mode."

What happens:
✅ DND disabled
✅ Normal operation resumes
✅ Apps can be reopened
```

**What Gets Minimized During Deep Work:**
- Social media apps (Discord, Slack personal channels)
- Chat applications (except work-related ones)
- Email clients (to prevent distractions)
- Entertainment apps (Spotify, YouTube)
- Everything except Aria and your specified work tools

### Real-World Usage Scenarios

**Morning Standup:**
```
Calendar Event: "Daily Standup (Teams) @ 9 AM"
Result at 8:55 AM:
- Aria announces: "Daily standup in 5 minutes. Opening Teams."
- Microsoft Teams launches
- You're ready to join
```

**Client Presentations:**
```
Calendar Event: "Client Demo via Zoom @ 3 PM"
Result at 2:55 PM:
- Aria: "Client Demo starting soon. Opening Zoom."
- Zoom launches
- You have time to test audio/video
```

**Coding Sessions:**
```
Calendar Event: "Dev Time - Feature Implementation @ 10 AM"
Result at 9:55 AM:
- Aria: "Coding session starting soon. Opening VS Code."
- VS Code launches
- Project ready to go
```

**Workout Reminders:**
```
Calendar Event: "Gym Session @ 6 PM"
Result at 5:55 PM:
- Aria: "Time for the gym! Get moving."
- Motivational reminder
```

### Customizing Proactive Actions

**To Add More Keywords** (Advanced Users):

Edit `proactive_manager.py`:

```python
def _trigger_action_for_event(self, event):
    summary = event.get('summary', '').lower()
    
    # Add your custom trigger:
    if "standup" in summary:
        self._speak(f"Standup meeting in 5 minutes. Opening Teams.")
        self.app_launcher.open_desktop_app("teams")
```

**Tips for Event Naming:**
- Use clear keywords: "Zoom Call" not just "Call"
- Be specific: "Focus Time" not just "Work"
- Consistent naming helps: Always use "Teams" for Teams meetings

### Configuration

**Proactive monitoring runs automatically in the background.**

**Default Settings:**
- Check Interval: Every 60 seconds
- Reminder Timing: 5 minutes before events
- Deep Work Trigger: "focus time" in event title (case-insensitive)

**To Disable Proactive Actions** (if needed):

Edit `aria_core.py` and comment out:
```python
# self.proactive_manager.start_monitoring()
```

Then restart Aria.

---

## 📡 Background Services

### Understanding Background Services

Background Services run silently while you use Aria, constantly monitoring your system and calendar to keep you informed and prepared.

**Two Main Services:**
1. **Health Monitor** - Watches battery level and CPU usage
2. **Calendar Scheduler** - Sends intelligent event reminders

These services work 24/7 to ensure you never miss important events or system alerts!

### Tutorial 24: Health Monitoring

**Battery Alerts**

Aria automatically notifies you when your battery needs attention:

**Low Battery Alert:**
```
[Battery drops to 18%]
Aria speaks + UI notification:
"⚠️ Low battery detected: 18%. Please plug in your charger."
```

**When It Triggers:**
- Battery level drops below 20%
- Device is NOT currently charging
- Prevents unexpected shutdowns during work

**High Battery (Optional):**
Some users like to know when fully charged to preserve battery health (feature can be added).

**CPU Alerts**

When your system is under heavy load:

```
[CPU usage hits 94%]
Aria speaks + UI notification:
"⚠️ High CPU usage detected: 94%. Some applications may be slowing down your system."
```

**When It Triggers:**
- CPU usage exceeds 90%
- Sustained for more than a few seconds
- Helps identify performance issues

**Monitoring Frequency:**
- Health checks run every 60 seconds
- Lightweight, minimal system impact
- Alerts spoken via TTS + shown in UI

### Tutorial 25: Calendar Event Reminders

Aria provides two levels of event reminders with AI-generated messages.

**30-Minute Early Reminders (Friendly Heads-Up)**

For events 5-30 minutes away:

```
[Event in 15 minutes]
Aria speaks:
"Excuse me, just a heads up that your meeting starts in 15 minutes."
```

**Example Variations** (LLM-generated):
- "Hey, friendly reminder - your client call is in 20 minutes."
- "Heads up! Team standup starts in 10 minutes."
- "Just so you know, your presentation begins in 25 minutes."

**5-Minute Urgent Reminders**

For imminent events (0-5 minutes away):

```
[Event in 3 minutes]
Aria speaks urgently:
"Hurry up, your meeting starts in 3 minutes!"
```

**Example Variations** (LLM-generated):
- "Quick! Your call starts in 2 minutes!"
- "You need to join now - meeting in 1 minute!"
- "Last call - your event is starting in 4 minutes!"

**Why LLM-Generated Messages?**
- Natural variety (never repetitive)
- Context-aware based on event details
- Appropriate urgency level
- Feels more human and less robotic

### Tutorial 26: UI Notification Queue

**How the System Works:**

```
1. Background service detects event (battery low, meeting soon, etc.)
   ↓
2. Notification added to queue
   ↓
3. Frontend polls /notifications endpoint
   ↓
4. Notification appears in Aria UI
   ↓
5. Queue clears after retrieval
```

**Types of Notifications You'll See:**

**System Alerts:**
```
⚡ Battery: 15% - Please charge
🔥 CPU: 92% - High usage detected
```

**Calendar Reminders:**
```
📅 Team Standup in 10 minutes
⏰ Client Call in 5 minutes - Join now!
```

**Proactive Actions:**
```
🚀 Opening Zoom for your meeting
🎯 Deep Work mode activated
```

**Viewing Notifications:**

Notifications appear automatically in the Aria UI. No manual action needed!

**For Developers** (API Access):
```bash
GET http://localhost:5000/notifications
```

Response:
```json
{
  "status": "success",
  "notifications": [
    {
      "type": "assistant_message",
      "content": "Hurry up, your meeting starts in 5 minutes!",
      "timestamp": "2025-11-30T15:55:00"
    },
    {
      "type": "assistant_message",
      "content": "Low battery: 18%. Please plug in.",
      "timestamp": "2025-11-30T15:50:30"
    }
  ]
}
```

### Configuration & Customization

**Health Monitor Settings:**

Default thresholds:
- Battery alert: Below 20%
- CPU alert: Above 90%
- Check frequency: Every 60 seconds

**Calendar Scheduler Settings:**

Default timing:
- Check frequency: Every 15 minutes (900 seconds)
- Early reminder window: 5-30 minutes before event
- Urgent reminder window: 0-5 minutes before event

**To Modify Settings** (Advanced):

Edit `backend_fastapi.py`:

```python
# Health monitor check interval (line ~794)
await asyncio.sleep(60)  # Change to your preference

# Calendar check interval (line ~755)
await asyncio.sleep(900)  # 900s = 15min, try 300s = 5min
```

**To Disable Background Services** (Not Recommended):

Comment out in `backend_fastapi.py`:
```python
# asyncio.create_task(background_scheduler())
# asyncio.create_task(background_health_monitor())
```

**⚠️ Note:** Disabling these reduces Aria's proactive capabilities significantly.

### Benefits of Background Services

**Never Miss Important Events:**
- Automatic, timely reminders
- Even when Aria UI is minimized
- Works across all your calendars

**System Health Awareness:**
- Prevents unexpected shutdowns
- Early warning for performance issues
- Battery preservation

**Hands-Free Operation:**
- No manual checking needed
- Proactive rather than reactive
- Focus on your work, Aria handles the rest

---


## 🔧 Troubleshooting

### Common Issues & Solutions

#### Issue 1: "Backend fails to start"

**Symptoms:** Electron shows "Connecting..." forever

**Solutions:**
```powershell
# 1. Check if Python backend is running
.venv\Scripts\activate
python backend_api.py

# 2. Verify .venv path in electron/main.js
# Make sure it matches your actual venv location

# 3. Check for port conflicts
# Backend runs on port 5000 by default
```

#### Issue 2: "Voice not working"

**Solutions:**
1. **Check microphone permissions:**
   - Windows Settings → Privacy → Microphone
   - Allow desktop apps to access microphone

2. **Test microphone:**
```python
python
>>> import speech_recognition as sr
>>> sr.Microphone.list_microphone_names()
# Should show your microphones
```

3. **Reduce background noise:**
   - Speak in a quieter environment
   - Adjust `energy_threshold` in aria_core.py (advanced)

4. **Install PyAudio properly:**
```powershell
pip install pipwin
pipwin install pyaudio
```

#### Issue 3: "No AI responses"

**Check:**
1. **.env file exists** with valid `OPEN_AI_API_KEY`
2. **Restart after adding .env**
3. **Test API key:**
```powershell
python verify_openai.py
```

#### Issue 4: "Calendar auth not working"

**Solutions:**
1. **Delete old token:**
```powershell
del token.pickle
```

2. **Verify credentials.json exists** in root folder
3. **Re-run Aria** → Browser opens for auth
4. **Grant permissions** in the browser window

#### Issue 5: "Notion integration not working"

**Check:**
1. **API key in .env:**
```env
NOTION_API_KEY=secret_...
```

2. **Pages shared with Aria integration:**
   - Open Notion page → "..." → "Add connections" → "Aria"

3. **Test connection:**
```powershell
python verify_notion.py
```

#### Issue 6: "App won't open [AppName]"

**Solutions:**
1. **Check exact app name:**
   - Open Start Menu and see the actual name
   - Use that name in command

2. **Try variations:**
```
"open vs code"
"open visual studio code"
"open code"
```

3. **Re-index apps:**
   - Restart Aria to rebuild app index

---

## 💡 Tips & Tricks

### Productivity Hacks

**1. Morning Routine:**
```
"Aria, what's the weather?"
"Aria, what's my schedule today?"
"Aria, organize my desktop"
```

**2. Quick Scheduling:**
```
"Aria, schedule lunch with John tomorrow at 12"
[Instantly added to calendar]
```

**3. Research Mode:**
```
"Aria, search for [topic]"
[Opens Google search]
"Aria, summarize this article"
[Processes and summarizes]
```

**4. File Organization:**
```
End of day:
"Aria, organize downloads"
"Aria, organize desktop"
[Clean workspace for tomorrow!]
```

### Voice Command Pro Tips

**✅ DO:**
- Speak clearly and naturally
- Use specific app/file names
- Say "Aria" before each command
- Wait for response before next command

**❌ DON'T:**
- Rush or mumble
- Use overly complex sentences
- Chain too many commands at once
- Interrupt Aria while responding

### Hidden Features

**1. Identity Question:**
```
"Aria, who are you?"
→ Aria introduces herself
```

**2. Fuzzy Matching:**
```
"Aria, opn chrom"  [typo!]
→ Still works! Opens Chrome
```

**3. Natural Language Processing:**
```
"Aria, I need to do some math"
→ Opens Calculator automatically
```

**4. Context in File Ops:**
```
"Create notes.txt"
"Add 'buy milk' to it"
"Read it back to me"
[Aria remembers which file!]
```

---

## ❓ FAQ

### General Questions

**Q: Is Aria free?**
A: Aria is free and open-source! You only pay for:
- OpenAI API usage (very affordable)
- Optional: OpenWeather API (free tier available)

**Q: Does Aria work offline?**
A: Partially. Basic commands work, but AI features require internet for:
- OpenAI API calls
- Google Calendar sync
- Notion integration
- Web searches

**Q: Can I use a different AI model?**
A: Yes! Edit `brain.py` to use:
- Google Gemini (already supported)
- Local models (Llama, Mistral) - requires setup
- Other OpenAI models (GPT-3.5, etc.)

**Q: Is my data private?**
A: Yes! 
- Runs 100% locally on your PC
- Uses your own API keys
- No data sent to third parties
- Open source - verify yourself!

### Feature Questions

**Q: Can Aria draft emails?**
A: Not yet, but it's planned for Phase 5!

**Q: Will Aria work on Mac/Linux?**
A: Currently Windows only. Mac/Linux support coming soon!

**Q: Can I add custom commands?**
A: Yes! Edit `aria_core.py` to add custom logic.

**Q: Does Aria have a mobile app?**
A: No, Aria is desktop-only currently.

**Q: Can multiple users use Aria?**
A: Yes, but each user needs their own API keys.

### Technical Questions

**Q: Which Python version?**
A: Python 3.10+ recommended (tested on 3.10, 3.11)

**Q: How much RAM does Aria use?**
A: ~200-300 MB for backend, ~150MB for Electron UI

**Q: Can I auto-start Aria on boot?**
A: Yes! 
1. Right-click Aria shortcut
2. Copy to: `shell:startup`

**Q: How to update Aria?**
```powershell
git pull origin main
pip install -r requirements.txt --upgrade
cd electron && npm install
```

**Q: Can I build an installer?**
```powershell
cd electron
npm run build
# Creates installer in dist/
```

### Troubleshooting FAQs

**Q: "Aria is really slow to respond"**
A: Check your internet connection - OpenAI API requires it.

**Q: "Aria keeps mishearing me"**
A: Adjust microphone sensitivity or reduce ambient noise.

**Q: "Calendar events in wrong timezone"**
A: Edit `calendar_manager.py` to change timezone from `Asia/Kolkata`.

**Q: "Electron window is too small/large"**
A: Edit window size in `electron/main.js`:
```javascript
width: 400,  // Your preferred width
height: 800, // Your preferred height
```

---

## 📚 Additional Resources

### Documentation Files

- **[README.md](README.md)** - Project overview and quick start
- **[FULL_DOCUMENTATION.md](FULL_DOCUMENTATION.md)** - Technical architecture
- **[SYSTEM_CONTROL_GUIDE.md](SYSTEM_CONTROL_GUIDE.md)** - System control details
- **[GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)** - Google Calendar setup guide
- **[NOTION_SETUP.md](NOTION_SETUP.md)** - Notion integration setup
- **[MONGODB_SETUP.md](MONGODB_SETUP.md)** - Database setup (advanced)

### Quick Reference Card

```
┌─────────────────────────────────────────────┐
│         ARIA COMMAND QUICK REFERENCE         │
├─────────────────────────────────────────────┤
│ BASIC                                        │
│  "What time is it?"                          │
│  "What's today's date?"                      │
│  "Who are you?"                              │
├─────────────────────────────────────────────┤
│ SYSTEM CONTROL                               │
│  "Set volume to 50"                          │
│  "Lock system"                               │
│  "Empty recycle bin"                         │
├─────────────────────────────────────────────┤
│ APPS & WEB                                   │
│  "Open [app name]"                           │
│  "Open [website].com"                        │
│  "Search for [query]"                        │
├─────────────────────────────────────────────┤
│ FILES                                        │
│  "Search for [file] in [location]"           │
│  "Create file [name]"                        │
│  "Read [filename]"                           │
│  "Organize downloads"                        │
├─────────────────────────────────────────────┤
│ PRODUCTIVITY                                 │
│  "What's the weather in [city]?"             │
│  "Schedule [event] at [time]"                │
│  "What's my schedule?"                       │
│  "Add to Notion [content]"                   │
└─────────────────────────────────────────────┘
```

---

## 🎓 Tutorial Videos (Concept)

*If this were a YouTube tutorial series, here's what it would look like:*

### Video 1: "Getting Started with Aria" (10 mins)
- Installation walkthrough
- First launch experience
- Your first 5 commands

### Video 2: "Voice Control Mastery" (15 mins)
- Wake word setup
- Voice command best practices
- Troubleshooting voice issues

### Video 3: "Desktop Automation" (12 mins)
- Opening apps and websites
- File management basics
- System control features

### Video 4: "Productivity Powerhouse" (20 mins)
- Calendar integration setup
- Notion workflow
- File automation

### Video 5: "Advanced Customization" (18 mins)
- Creating custom commands
- Integrating new APIs
- Building plugins

---

## 🏁 Conclusion

Congratulations! You now know how to use every feature of Aria. 

### Your Next Steps:

1. ✅ **Complete the setup** if you haven't already
2. ✅ **Try the first 5 tutorials** to get comfortable
3. ✅ **Set up integrations** (Calendar, Notion, Weather)
4. ✅ **Customize** wake word and music library
5. ✅ **Master voice commands** for hands-free productivity

### Get Help & Contribute

- **Issues?** Check the Troubleshooting section
- **Questions?** Read the FAQ
- **Want more?** Check the GitHub repo for updates
- **Contribute?** Fork and submit pull requests!

### Share Your Experience

We'd love to hear how Aria helps you! Share your workflows, custom commands, and feedback.

---

**Made with ❤️ by Shreyas**

*Version 1.0 | Last Updated: November 23, 2025*

---

> 💡 **Pro Tip:** Bookmark this manual and refer back as you explore new features. The more you use Aria, the more powerful it becomes!

**Happy commanding! 🚀**
