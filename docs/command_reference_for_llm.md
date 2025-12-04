# ARIA Command Reference for LLM Training

> **Purpose**: This document provides a comprehensive reference of all ARIA voice assistant commands for LLM training and context understanding.

---

## Table of Contents

1. [Power Management](#power-management)
2. [Volume Control](#volume-control)
3. [System Maintenance](#system-maintenance)
4. [Clipboard Operations](#clipboard-operations)
5. [Screenshot Operations](#screenshot-operations)
6. [System Monitoring](#system-monitoring)
7. [File Automation](#file-automation)
8. [File Operations](#file-operations)
9. [Web & Applications](#web--applications)
10. [Media Control](#media-control)
11. [Productivity](#productivity)
12. [Information Services](#information-services)
13. [Email](#email)
14. [General Conversation](#general-conversation)

---

## Power Management

### Shutdown
**Intent**: `shutdown`  
**Description**: Shut down the computer  
**Parameters**: None  
**Natural Language Patterns**:
- "shutdown the computer"
- "turn off the computer"
- "shut down my pc"
- "power off the system"
- "shutdown pc"

### Restart
**Intent**: `restart`  
**Description**: Restart the computer  
**Parameters**: None  
**Natural Language Patterns**:
- "restart the computer"
- "reboot my pc"
- "restart my system"
- "reboot the computer"

### Lock Screen
**Intent**: `lock`  
**Description**: Lock the screen/workstation  
**Parameters**: None  
**Natural Language Patterns**:
- "lock the screen"
- "lock my computer"
- "lock the system"
- "lock workstation"

### Sleep
**Intent**: `sleep`  
**Description**: Put computer to sleep  
**Parameters**: None  
**Natural Language Patterns**:
- "put computer to sleep"
- "sleep mode"
- "put pc to sleep"
- "enter sleep mode"

### Cancel Shutdown
**Intent**: `cancel_shutdown`  
**Description**: Cancel pending shutdown/restart  
**Parameters**: None  
**Natural Language Patterns**:
- "cancel shutdown"
- "abort shutdown"
- "cancel restart"
- "abort restart"

---

## Volume Control

### Volume Up
**Intent**: `volume_up`  
**Description**: Increase system volume  
**Parameters**: None  
**Natural Language Patterns**:
- "increase volume"
- "turn up volume"
- "make it louder"
- "volume up"
- "raise volume"

### Volume Down
**Intent**: `volume_down`  
**Description**: Decrease system volume  
**Parameters**: None  
**Natural Language Patterns**:
- "decrease volume"
- "turn down volume"
- "make it quieter"
- "lower volume"

### Volume Set
**Intent**: `volume_set`  
**Description**: Set volume to specific level  
**Parameters**: 
- `level` (integer, 0-100)

**Natural Language Patterns**:
- "set volume to 50"
- "volume 75"
- "set volume at 30"
- "change volume to 60"

### Mute
**Intent**: `volume_mute`  
**Description**: Mute system audio  
**Parameters**: None  
**Natural Language Patterns**:
- "mute system"
- "mute audio"
- "turn off sound"
- "silence audio"

### Unmute
**Intent**: `volume_unmute`  
**Description**: Unmute system audio  
**Parameters**: None  
**Natural Language Patterns**:
- "unmute system"
- "unmute audio"
- "turn on sound"
- "restore audio"

### Check Volume
**Intent**: `volume_check`  
**Description**: Check current volume level  
**Parameters**: None  
**Natural Language Patterns**:
- "what's the volume"
- "check volume"
- "current volume level"
- "volume status"

---

## System Maintenance

### Empty Recycle Bin
**Intent**: `recycle_bin_empty`  
**Description**: Empty the recycle bin  
**Parameters**: None  
**Natural Language Patterns**:
- "empty recycle bin"
- "clear recycle bin"
- "empty trash"
- "clean recycle bin"

### Check Recycle Bin
**Intent**: `recycle_bin_check`  
**Description**: Check recycle bin status  
**Parameters**: None  
**Natural Language Patterns**:
- "check recycle bin"
- "recycle bin status"
- "what's in recycle bin"
- "how many items in recycle bin"

---

## Clipboard Operations

### Copy to Clipboard
**Intent**: `clipboard_copy`  
**Description**: Copy text to clipboard  
**Parameters**: 
- `text` (string)

**Natural Language Patterns**:
- "copy hello world to clipboard"
- "copy meeting at 3pm to clipboard"
- "clipboard copy this is a test"

**Example**:
```
User: "copy call john tomorrow to clipboard"
Intent: clipboard_copy
Parameters: {text: "call john tomorrow"}
```

### Read Clipboard
**Intent**: `clipboard_read`  
**Description**: Read clipboard contents  
**Parameters**: None  
**Natural Language Patterns**:
- "read clipboard"
- "what's in the clipboard"
- "clipboard contents"
- "show clipboard"

### Clear Clipboard
**Intent**: `clipboard_clear`  
**Description**: Clear clipboard  
**Parameters**: None  
**Natural Language Patterns**:
- "clear clipboard"
- "empty clipboard"
- "delete clipboard"
- "reset clipboard"

---

## Screenshot Operations

### Take Screenshot
**Intent**: `screenshot_take`  
**Description**: Take a screenshot  
**Parameters**: 
- `filename` (string, optional)

**Natural Language Patterns**:
- "take a screenshot"
- "capture screen"
- "screenshot"
- "take screenshot called bug_report"
- "capture screen as project_demo"

**Examples**:
```
User: "take screenshot"
Intent: screenshot_take
Parameters: {}

User: "take screenshot called meeting_notes"
Intent: screenshot_take
Parameters: {filename: "meeting_notes"}
```

---

## System Monitoring

### Battery Check
**Intent**: `battery_check`  
**Description**: Check battery status and percentage  
**Parameters**: None  
**Natural Language Patterns**:
- "check battery"
- "battery status"
- "what's my battery percentage"
- "how much battery left"

### CPU Check
**Intent**: `cpu_check`  
**Description**: Check CPU usage  
**Parameters**: None  
**Natural Language Patterns**:
- "check CPU"
- "CPU usage"
- "how much CPU am I using"
- "processor usage"

### RAM Check
**Intent**: `ram_check`  
**Description**: Check RAM/memory usage  
**Parameters**: None  
**Natural Language Patterns**:
- "check RAM"
- "memory usage"
- "how much RAM am I using"
- "RAM status"

### System Stats
**Intent**: `system_stats`  
**Description**: Get all system statistics  
**Parameters**: None  
**Natural Language Patterns**:
- "system stats"
- "check system status"
- "system information"
- "show system stats"

---

## File Automation

### Organize Downloads
**Intent**: `organize_downloads`  
**Description**: Organize downloads folder  
**Parameters**: None  
**Natural Language Patterns**:
- "organize downloads"
- "organize downloads folder"
- "clean up downloads"
- "sort downloads"

### Organize Desktop
**Intent**: `organize_desktop`  
**Description**: Organize desktop folder  
**Parameters**: None  
**Natural Language Patterns**:
- "organize desktop"
- "clean desktop"
- "sort desktop files"
- "tidy desktop"

---

## File Operations

### Create File
**Intent**: `file_create`  
**Description**: Create a new file  
**Parameters**: 
- `filename` (string, required)
- `location` (string, optional: desktop, downloads, documents, pictures, music)
- `content` (string, optional)

**Natural Language Patterns**:
- "create a file called notes.txt"
- "create file test.txt on desktop"
- "make a file named report.doc in documents"
- "create readme.md in downloads"

**Location Mapping**:
- "download section", "downloads" → `downloads`
- "desktop", "on desktop" → `desktop`
- "documents", "document folder" → `documents`
- "pictures", "photos" → `pictures`

**Examples**:
```
User: "create file hi.txt in download section"
Intent: file_create
Parameters: {filename: "hi.txt", location: "downloads"}

User: "create notes.txt on desktop with content meeting at 3pm"
Intent: file_create
Parameters: {filename: "notes.txt", location: "desktop", content: "meeting at 3pm"}
```

### Read File
**Intent**: `file_read`  
**Description**: Read/view file contents  
**Parameters**: 
- `filename` (string)

**Natural Language Patterns**:
- "read notes.txt"
- "read the file report.pdf"
- "show me contents of todo.txt"
- "what's in the file data.csv"

### File Info
**Intent**: `file_info`  
**Description**: Get file information  
**Parameters**: 
- `filename` (string)

**Natural Language Patterns**:
- "get info on report.pdf"
- "file information for document.docx"
- "show details of image.png"
- "info about video.mp4"

### Append to File
**Intent**: `file_append`  
**Description**: Append content to a file  
**Parameters**: 
- `filename` (string)
- `content` (string)

**Natural Language Patterns**:
- "append to notes.txt Meeting at 3 PM"
- "add to todo.txt buy groceries"
- "append call john to reminders.txt"

### Delete File
**Intent**: `file_delete`  
**Description**: Delete a file or directory  
**Parameters**: 
- `filename` (string)

**Natural Language Patterns**:
- "delete the file old_draft.txt"
- "remove test.txt"
- "delete obsolete_data.csv"

### Rename File
**Intent**: `file_rename`  
**Description**: Rename a file or directory  
**Parameters**: 
- `old_name` (string)
- `new_name` (string)

**Natural Language Patterns**:
- "rename notes.txt to important_notes.txt"
- "rename report.doc to final_report.doc"

### Move File
**Intent**: `file_move`  
**Description**: Move a file to different location  
**Parameters**: 
- `filename` (string)
- `destination` (string)

**Natural Language Patterns**:
- "move screenshot.png to pictures"
- "move report.pdf to documents"
- "transfer image.jpg to pictures folder"

### Copy File
**Intent**: `file_copy`  
**Description**: Copy a file or directory  
**Parameters**: 
- `filename` (string)
- `destination` (string)

**Natural Language Patterns**:
- "copy report.pdf to documents"
- "copy notes.txt to desktop"
- "duplicate image.png to pictures"

### Search Files
**Intent**: `file_search`  
**Description**: Search for files (NOT web search)  
**Parameters**: 
- `pattern` (string)
- `location` (string, optional)

**Natural Language Patterns**:
- "search for aria_logo on downloads"
- "find presentation in documents"
- "search for *.pdf on desktop"
- "find all images in pictures"

**Key Distinction**:
- **File Search**: "find resume on desktop" → `file_search`
- **Web Search**: "search for python tutorials" → `web_search`

---

## Web & Applications

### Open Website
**Intent**: `web_open`  
**Description**: Open a website  
**Parameters**: 
- `url` (string)
- `name` (string, optional)

**Natural Language Patterns**:
- "open YouTube"
- "open Instagram"
- "go to Gmail"
- "open GitHub"
- "go to reddit.com"

**Common Websites**:
- YouTube → https://youtube.com
- Instagram → https://instagram.com
- Gmail → https://gmail.com
- Twitter → https://twitter.com
- LinkedIn → https://linkedin.com
- GitHub → https://github.com

### Open Application
**Intent**: `app_open`  
**Description**: Open a desktop application  
**Parameters**: 
- `app_name` (string)

**Natural Language Patterns**:
- "open Chrome"
- "launch VS Code"
- "open Calculator"
- "start Spotify"
- "open Notion"

**Common Applications**:
- Chrome, Firefox, Edge (browsers)
- VS Code, PyCharm (development)
- Spotify, VLC (media)
- Discord, Slack (communication)
- Calculator, Notepad (utilities)

### Web Search
**Intent**: `web_search`  
**Description**: Search Google/Web for information  
**Parameters**: 
- `query` (string)

**Natural Language Patterns**:
- "search for Python tutorials"
- "Google latest AI news"
- "search best restaurants near me"
- "look up how to fix Python import errors"

---

## Media Control

### Play Music
**Intent**: `music_play`  
**Description**: Play music or specific song  
**Parameters**: 
- `song` (string)

**Natural Language Patterns**:
- "play lofi music"
- "play some taylor swift"
- "play jazz"
- "play relaxing music"

---

## Productivity

### Calendar Query
**Intent**: `calendar_query`  
**Description**: Check schedule/events  
**Parameters**: None  
**Natural Language Patterns**:
- "what do I have today"
- "what's my schedule"
- "show upcoming events"
- "what's on my calendar"

### Calendar Create
**Intent**: `calendar_create`  
**Description**: Create a calendar event  
**Parameters**: 
- `event` (string)
- `time` (string)

**Natural Language Patterns**:
- "schedule a meeting tomorrow at 3 PM"
- "schedule standup on Monday at 9 AM"
- "create event team review next Friday at 2 PM"

### Notion Query
**Intent**: `notion_query`  
**Description**: Search or summarize Notion pages  
**Parameters**: 
- `query` (string)

**Natural Language Patterns**:
- "search notion for project notes"
- "summarize the notion page about AI"
- "find goals in notion"

### Notion Create
**Intent**: `notion_create`  
**Description**: Add item/page to Notion  
**Parameters**: 
- `content` (string)
- `list` (string, optional)

**Natural Language Patterns**:
- "add milk to grocery list in notion"
- "add task to notion todo list"
- "create notion page for new project"

---

## Information Services

### Time Check
**Intent**: `time_check`  
**Description**: Get current time  
**Parameters**: None  
**Natural Language Patterns**:
- "what time is it"
- "tell me the time"
- "current time"
- "what's the time"

### Date Check
**Intent**: `date_check`  
**Description**: Get current date  
**Parameters**: None  
**Natural Language Patterns**:
- "what's today's date"
- "tell me the date"
- "current date"
- "what date is it"

### Weather Check
**Intent**: `weather_check`  
**Description**: Check weather for a specific location  
**Parameters**: 
- `city` (string, optional)

**Natural Language Patterns**:
- "what's the weather in London"
- "check weather in New York"
- "weather in Tokyo"
- "what's the weather" (uses default location)

---

## Email

### Send Email
**Intent**: `email_send`  
**Description**: Send an email  
**Parameters**: 
- `recipient` (string)
- `subject` (string, optional)
- `body` (string, optional)

**Natural Language Patterns**:
- "send an email to john@example.com about meeting"
- "email sarah@company.com the project update"
- "send email to team@startup.com"

---

## General Conversation

### General Chat
**Intent**: `general_chat`  
**Description**: General conversation/questions (fallback)  
**Parameters**: None  
**Natural Language Patterns**:
- "tell me a joke"
- "who are you"
- "explain quantum computing"
- "write a poem about rain"
- "what can you do"
- "help me with something"

**Use Cases**:
- Questions that don't fit specific intents
- General AI assistance
- Casual conversation
- Explanations and information

---

## Intent Classification Decision Tree

```
User Command
    │
    ├─ Contains power words (shutdown, restart, lock, sleep)
    │   └─> Power Management Intents
    │
    ├─ Contains volume words (volume, mute, sound, audio)
    │   └─> Volume Control Intents
    │
    ├─ Contains file words (file, create, read, delete, search for [filename])
    │   └─> File Operation Intents
    │
    ├─ Contains "search for" + generic query
    │   └─> web_search (NOT file_search)
    │
    ├─ Contains "open" + website/URL
    │   └─> web_open
    │
    ├─ Contains "open/launch" + application name
    │   └─> app_open
    │
    ├─ Contains system monitoring words (battery, CPU, RAM, stats)
    │   └─> System Monitoring Intents
    │
    ├─ Contains clipboard/screenshot words
    │   └─> Clipboard/Screenshot Intents
    │
    ├─ Contains calendar/schedule words
    │   └─> Calendar Intents
    │
    ├─ Contains notion words
    │   └─> Notion Intents
    │
    ├─ Contains weather/time/date words
    │   └─> Information Service Intents
    │
    └─ Everything else
        └─> general_chat
```

---

## Common Confusion Points

### File Search vs Web Search
- **File Search**: Local file system search
  - "find resume on desktop"
  - "search for *.pdf in downloads"
  
- **Web Search**: Google/web search
  - "search for python tutorials"
  - "google best restaurants"

### Website vs Application
- **Website**: Online services
  - "open YouTube" (web)
  - "open Gmail" (web)
  
- **Application**: Desktop software
  - "open Chrome" (app)
  - "launch VS Code" (app)

### Location Parameters
Always map to standard locations:
- Downloads: `downloads`
- Desktop: `desktop`
- Documents: `documents`
- Pictures: `pictures`
- Music: `music`
- Videos: `videos`

---

## Training Tips

1. **Context Matters**: Consider the full sentence, not just keywords
2. **Be Specific**: Choose the most specific intent that matches
3. **Extract Parameters**: Pull out all relevant data (filenames, numbers, locations)
4. **Handle Variations**: Recognize different phrasings of the same command
5. **Use Fallback**: When unsure, use `general_chat` intent

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-28  
**Total Intents**: 40  
**Categories**: 14
