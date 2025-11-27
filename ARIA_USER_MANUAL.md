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
16. [Settings & Customization](#%EF%B8%8F-settings--customization)
17. [Troubleshooting](#-troubleshooting)
18. [Tips & Tricks](#-tips--tricks)
19. [FAQ](#-faq)

---

## 🌟 Introduction

### What is Aria?

Aria is a premium, local-first AI assistant that combines the power of advanced language models (GPT-4o) with deep system integration. Unlike cloud-only assistants, Aria gives you:

- **🎙️ Voice Control** - Wake-word activation and natural speech processing
- **🖥️ System Integration** - Control apps, files, and system settings
- **🧠 AI Intelligence** - Powered by OpenAI's GPT-4o for natural conversations
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

1. **The UI will open** - You'll see a modern chat interface
2. **Aria will greet you** - With a time-based greeting
3. **Backend starts** - The Python backend initializes automatically
4. **You're ready!** - Start typing or click the microphone icon

---

## 🎯 Basic Features - Your First Steps

### Tutorial 1: Your First Command

**Let's start simple:**

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
- **[USER_GUIDE.md](USER_GUIDE.md)** - Quick user guide
- **[SYSTEM_CONTROL_GUIDE.md](SYSTEM_CONTROL_GUIDE.md)** - System control details
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
