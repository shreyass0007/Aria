# Aria User Guide

Welcome to **Aria**, your premium AI desktop assistant. Aria combines the power of advanced AI with deep integration into your computer, allowing you to control apps, manage your schedule, and organize your life using natural voice or text commands.

---

## 🚀 Getting Started

### 1. Launching Aria
- **Desktop App**: Run `npm start` in the `electron` directory.
- **Voice Mode**: Click the microphone icon 🎙️ or say "Aria" if listening is active.

### 2. Configuration
Ensure your `.env` file has the necessary keys:
- `OPEN_AI_API_KEY`: For Aria's brain.
- `NOTION_API_KEY` & `NOTION_DATABASE_ID`: For Notion integration.

---

## 🌟 Core Features & Use Cases

### 1. Notion Integration (New!)
Aria can now manage your entire Notion workspace. You can add tasks, notes, and search for pages.

**Setup:**
See [NOTION_SETUP.md](NOTION_SETUP.md) for instructions on connecting Aria to your workspace.

**Use Cases:**
*   **Quick Capture**: "Add a task to *Grocery List* to buy milk."
    *   *Aria finds the "Grocery List" page and adds the item.*
*   **Journaling**: "Add a note to *Daily Journal* saying I had a great meeting today."
*   **Searching**: "Search Notion for *Project Alpha*."
    *   *Aria lists pages matching that name.*
*   **Overview**: "List my Notion pages."
    *   *Shows recently modified pages.*

### 2. Calendar Scheduling
Manage your Google Calendar effortlessly.

**Use Cases:**
*   **Scheduling**: "Schedule a meeting with John tomorrow at 3 PM."
*   **Reminders**: "Remind me to call mom on Friday at 6 PM."
*   **Checking Schedule**: "What do I have upcoming?" or "What is my schedule for today?"

### 3. Desktop Control
Open applications instantly without touching your mouse.

**Use Cases:**
*   **Apps**: "Open Spotify", "Open VS Code", "Open Calculator".
*   **Files**: Aria indexes your Start Menu shortcuts, so you can open almost anything installed on your PC.

### 4. Web Browsing
Navigate the web hands-free.

**Use Cases:**
*   **Direct Access**: "Open YouTube", "Open Instagram", "Open Gmail".
*   **Smart Search**: "Search Google for latest tech news."
*   **Specific Sites**: "Open github.com".

### 5. Media Control
Control your music playback.

**Use Cases:**
*   **Music**: "Play my playlist" (Requires configuration in `music_library.py`).
*   **YouTube**: "Play lofi hip hop" (Searches/Opens YouTube).

### 6. General Knowledge
Ask Aria anything, just like ChatGPT.

**Use Cases:**
*   **Questions**: "Explain quantum computing in simple terms."
*   **Creative Writing**: "Write a short poem about rain."
*   **Utilities**: "What time is it?", "What is today's date?"

---

## 🎙️ Voice Commands Cheat Sheet

| Category | Command Example |
| :--- | :--- |
| **Wake Word** | "Aria..." |
| **Notion** | "Add to [Page] [Content]", "Search Notion for [Query]" |
| **Calendar** | "Schedule [Event] at [Time]" | "Schedule meeting with John tomorrow at 3 PM" |
| | "What is on my calendar?" | "Check my schedule for today" |
| | "Add to calendar" | "Add dentist appointment next Friday at 10 AM" |
| **Apps** | "Open [App Name]" |
| **Web** | "Open [Website]", "Search for [Query]" |
| **System** | "Exit", "Quit" |

---

## ❓ Troubleshooting

*   **"I encountered an error..."**: This usually means the backend is down. Restart the app (`npm start`).
*   **Notion not finding pages**: Ensure you have shared the specific page with the "Aria" integration in Notion (Click `...` > `Add connections` > `Aria`).
*   **Voice not working**: Check your microphone settings and ensure you are in a quiet environment.
