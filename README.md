# Aria – Advanced Desktop AI Assistant

<div align="center">

![Aria Logo](aria_logo.png)

**Premium local-first AI copilot that pairs a Python brain with a polished Electron interface**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Electron](https://img.shields.io/badge/Electron-28.0.0-purple.svg)](https://www.electronjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 🌟 Overview

**Aria** is a next-generation desktop AI assistant that combines the power of modern LLMs with practical system automation. Built with a Python backend and Electron frontend, Aria provides a seamless voice and text interface for managing your calendar, files, system settings, emails, and more—all through natural language.

### Key Features

- 🎯 **Unified Interface** – Electron sidebar, CustomTkinter window, and CLI modes
- 🎨 **Premium UX** – Arc-style glassmorphism, light/dark themes, smooth animations
- 🧠 **Multi-Model AI** – Support for GPT-4o, GPT-4o-mini, Claude 3.5 Sonnet, Claude 3 Opus, and Gemini Pro via LangChain
- 🎙️ **Advanced Voice Control** – Wake word detection, local Faster-Whisper transcription, Google/Edge TTS, and natural speech responses
- 📧 **Email Management** – Gmail integration for sending emails via voice/text commands
- 🗓️ **Calendar Integration** – Google Calendar OAuth for scheduling and event management
- 📝 **Notion Integration** – Search, summarize, and interact with your Notion workspace
- 🗂️ **File Management** – Complete CRUD operations with natural language commands
- 🖥️ **System Control** – Volume, power management, system monitoring, and maintenance
- 📊 **System Monitoring** – Real-time battery, CPU, and RAM status monitoring
- 📋 **Clipboard & Screenshots** – Clipboard operations and screenshot capture
- 🌤️ **Weather Updates** – Real-time weather information with friendly advice
- 💬 **Conversation History** – MongoDB-backed conversation persistence
- 🎵 **Media Control** – Quick access to music libraries and web media
- 🤖 **Intent Classification** – LLM-based natural language command understanding

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Electron Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Renderer   │  │   Preload    │  │    Main Process      │   │
│  │  (HTML/CSS)  │◄─┤     IPC      │◄─┤  (Spawns Backend)    │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST API
┌────────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend Server                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              backend_fastapi.py                          │   │
│  │  /health  /greeting  /message  /models/*  /voice/*       │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                      Aria Core Engine                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    aria_core.py                          │   │
│  │  • Speech Recognition & TTS (Faster-Whisper, Edge-TTS) │   │
│  │  • Command Routing & Intent Classification               │   │
│  │  • Desktop App Control                                   │   │
│  │  • Web Automation                                        │   │
│  └───────┬──────────────────────────────────────────────────┘   │
│          │                                                      │
│  ┌───────▼──────────┬───────────────┬───────────────┬────────┐  │
│  │   AriaBrain      │  Calendar     │   Notion      │ System │  │
│  │   (LangChain)    │  Manager      │   Manager     │ Control│  │
│  └───────┬──────────┴───────────────┴───────────────┴────────┘  │
│          │                                                      │
│  ┌───────▼──────────┬───────────────┬───────────────┬────────┐  │
│  │  File Manager    │   Weather     │ Conversation  │ Email  │  │
│  │  (CRUD Ops)      │   Manager     │   Manager     │Manager │  │
│  └──────────────────┴───────────────┴───────────────┴────────┘  │
│                                                                  │
│  ┌──────────────────┬───────────────┬────────────────────────┐  │
│  │ System Monitor   │  Clipboard    │  Speech Engine         │  │
│  │  (Battery/CPU)   │  Screenshot   │  (Faster-Whisper)      │  │
│  └──────────────────┴───────────────┴────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
┌───────▼────┐  ┌───────▼─────┐  ┌───────▼────┐  ┌───────▼────┐
│   OpenAI   │  │   Google    │  │   Notion   │  │  Anthropic │
│   GPT-4o   │  │  Calendar   │  │    API     │  │   Claude   │
│  Gemini    │  │    Gmail    │  │            │  │            │
└────────────┘  └─────────────┘  └────────────┘  └────────────┘
```

### Core Components

| Component | Description |
|-----------|-------------|
| **`aria_core.py`** | Central orchestrator handling speech I/O, command routing, and system integration |
| **`brain.py`**     | LangChain-powered AI brain supporting multiple models (GPT-4o, Claude, Gemini) for conversations and structured data extraction |
| **`backend_fastapi.py`** | FastAPI REST API server exposing endpoints for Electron frontend |
| **`command_intent_classifier.py`** | LLM-based intent classification for natural language commands |
| **`speech_engine.py`** | Local Faster-Whisper model for offline speech transcription |
| **`calendar_manager.py`** | Google Calendar OAuth and event management |
| **`email_manager.py`** | Gmail API integration for sending emails |
| **`notion_manager.py`** | Notion API integration for page search and summarization |
| **`file_manager.py`** | Complete file CRUD operations with safety checks |
| **`system_control.py`** | Volume control, power management, and system maintenance |
| **`system_monitor.py`** | Real-time battery, CPU, and RAM monitoring |
| **`clipboard_screenshot.py`** | Clipboard operations and screenshot capture functionality |
| **`weather_manager.py`** | OpenWeatherMap integration with conversational advice |
| **`conversation_manager.py`** | MongoDB-backed conversation history persistence |
| **`file_automation.py`** | Automatic file organization by type |

---

## 📋 Prerequisites

| Requirement | Version / Notes |
|-------------|-----------------|
| **Python** | 3.10+ (tested on Windows 11) |
| **Node.js & npm** | Node 18+ (Electron 28 requires ≥18.0.0) |
| **FFmpeg** | Optional, improves audio playback reliability |
| **Microphone & Speakers** | Required for voice mode |
| **OpenAI API Key** | Set `OPEN_AI_API_KEY` in `.env` (required for GPT models) |
| **Anthropic API Key** | Optional, set `ANTHROPIC_API_KEY` for Claude models |
| **Google API Key** | Optional, set `GOOGLE_API_KEY` for Gemini models |
| **Google Calendar** | Optional, requires `credentials.json` for calendar features |
| **Gmail** | Optional, uses same `credentials.json` for email features |
| **Notion API** | Optional, requires `NOTION_API_KEY` and `NOTION_DATABASE_ID` |
| **MongoDB** | Optional, for conversation history (defaults to localhost) |
| **OpenWeatherMap API** | Optional, requires `OPENWEATHER_API_KEY` for weather features |
| **CUDA** | Optional, for GPU acceleration of Faster-Whisper (CPU fallback available) |

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shreyass0007/Aria.git
cd ARIA
```

### 2. Python Environment Setup

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Note for Windows:** If PyAudio installation fails, use:
```powershell
pip install pipwin
pipwin install pyaudio
```

**Note for Faster-Whisper:** The model will download automatically on first use. For GPU acceleration, ensure CUDA is installed.

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Required - At least one AI provider
OPEN_AI_API_KEY=sk-your-openai-api-key-here

# Optional - Additional AI Models
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# Optional - Google Calendar & Gmail
# Download credentials.json from Google Cloud Console
# Enable Calendar API and Gmail API in your project

# Optional - Notion Integration
NOTION_API_KEY=secret-your-notion-api-key
NOTION_DATABASE_ID=your-database-id

# Optional - MongoDB (for conversation history)
MONGODB_URI=mongodb://localhost:27017/

# Optional - Weather API
OPENWEATHER_API_KEY=your-openweather-api-key

# Optional - User Name (for personalized greetings)
USER_NAME=Your Name
```

### 4. Google Services Setup (Optional)

To enable calendar scheduling and email features:
1. Follow the detailed [Google Calendar Setup Guide](GOOGLE_CALENDAR_SETUP.md)
2. Enable both **Calendar API** and **Gmail API** in Google Cloud Console
3. Download `credentials.json` and place it in the project root
4. Run Aria and authenticate in the browser
5. First run will open browser for authentication; `token.pickle` (Calendar) and `token_gmail.pickle` (Gmail) will be saved

### 5. Electron Frontend Setup

```powershell
cd electron
npm install
```

---

## 🎮 Usage

### Electron Desktop App (Recommended)

```powershell
cd electron
npm start
```

**Features:**
- Spawns Python backend automatically
- Sidebar window with chat interface
- Voice controls and settings
- Model selection (GPT-4o, Claude, Gemini)
- Theme persistence
- Use `npm run dev` for DevTools

**Build Installer:**
```powershell
npm run build
# Outputs NSIS installer in electron/dist/
```

### CustomTkinter GUI

```powershell
.venv\Scripts\activate
python gui.py
```

Native Python GUI with the same features as Electron app.

### CLI Wake Word Mode

```powershell
.venv\Scripts\activate
python main.py
```

Minimal interface that listens for wake word "aria" (or "neo") and processes voice commands.

### Backend API Only

```powershell
.venv\Scripts\activate
python backend_fastapi.py
```

Starts FastAPI server at `http://localhost:8000` for API testing or custom frontends.

---

## 📡 API Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `GET` | `/health` | Health check | - |
| `GET` | `/greeting` | Get time-based greeting | - |
| `GET` | `/models/available` | List available AI models | - |
| `GET` | `/models/current` | Get currently selected model | - |
| `POST` | `/models/set` | Set the current AI model | `{"model": "gpt-4o"}` |
| `POST` | `/message` | Process text message | `{"message": "text", "conversation_id": "uuid", "model": "gpt-4o"}` |
| `POST` | `/voice/start` | Start voice listening | - |
| `GET` | `/voice/listen` | Long-poll for transcribed text | - |
| `POST` | `/voice/stop` | Stop voice listening | - |

**Response Format:**
```json
{
  "response": "Aria's response text",
  "conversation_id": "uuid",
  "status": "success"
}
```

**Error Format:**
```json
{
  "status": "error",
  "error": "Error message"
}
```

**Available Models:**
- `gpt-4o` - OpenAI GPT-4o (default)
- `gpt-4o-mini` - OpenAI GPT-4o Mini
- `gpt-3.5-turbo` - OpenAI GPT-3.5 Turbo
- `claude-3-5-sonnet-20241022` - Anthropic Claude 3.5 Sonnet
- `claude-3-opus-20240229` - Anthropic Claude 3 Opus
- `gemini-pro` - Google Gemini Pro

---

## 🎯 Features in Detail

### Voice Control

- **Wake Word Detection**: "aria" or "neo" (configurable)
- **Speech Recognition**: 
  - Google Speech API via `SpeechRecognition` (online)
  - Faster-Whisper local transcription (offline, GPU/CPU)
- **Text-to-Speech**: 
  - Google TTS via `gTTS` with `pygame` playback
  - Edge-TTS for natural voice synthesis
- **Thread-Safe**: Prevents microphone contention with locking
- **Queue-Based TTS**: Non-blocking speech output

### AI Models & Intelligence

- **Multi-Model Support**: Switch between GPT-4o, Claude, and Gemini
- **LangChain Integration**: Structured output parsing and tool calling
- **Intent Classification**: LLM-based natural language understanding
- **Conversation Context**: Maintains conversation history for context-aware responses

### Desktop App Control

- **Fuzzy Matching**: Intelligent app name matching (e.g., "open figma" → Figma)
- **Shortcut Indexing**: Automatically indexes `.lnk` files from:
  - `%ProgramData%\Microsoft\Windows\Start Menu`
  - `%APPDATA%\Microsoft\Windows\Start Menu`
- **Fallback**: Uses `os.startfile` for unmatched apps

### Email Management

- **Gmail Integration**: Send emails via voice/text commands
- **OAuth Authentication**: Secure Google OAuth flow
- **Draft Confirmation**: Review email drafts before sending
- **Natural Language**: "send an email to john@example.com about the meeting"

### File Management

**Supported Operations:**
- Create, read, update, delete files
- Rename, move, copy files and directories
- Search files by name/pattern
- Get file information (size, modified date, etc.)
- Safe location restrictions (Desktop, Downloads, Documents)

**Example Commands:**
- "create a file called notes.txt on desktop"
- "read the file report.pdf"
- "delete the file old_draft.txt"
- "search for files named invoice"

### Calendar Integration

- **Natural Language Parsing**: "schedule standup tomorrow 9am"
- **Event Creation**: Automatic time parsing and calendar insertion
- **Event Retrieval**: "what do I have today?" returns upcoming events
- **OAuth Flow**: One-time authentication, token cached in `token.pickle`

### Notion Integration

- **Page Search**: "search notion for project notes"
- **Page Summarization**: "summarize the notion page about AI"
- **Database Queries**: Search and filter Notion databases
- **Interactive Selection**: Choose from multiple search results

### System Control

**Volume Management:**
- "set volume to 50"
- "increase volume"
- "mute/unmute"

**Power Management:**
- "lock screen"
- "shutdown computer"
- "restart computer"
- "put computer to sleep"

**Maintenance:**
- "empty recycle bin"
- "check recycle bin"

### System Monitoring

- **Battery Status**: Real-time battery percentage, charging status, time remaining
- **CPU Usage**: Current CPU utilization percentage
- **RAM Usage**: Memory usage statistics
- **Friendly Advice**: Contextual suggestions based on system status

### Clipboard & Screenshots

- **Clipboard Operations**: Copy, read, and clear clipboard contents
- **Screenshot Capture**: Automatic or custom-named screenshots
- **Auto-Organization**: Screenshots saved to Desktop/Screenshots folder

### Weather Updates

- Real-time weather from OpenWeatherMap
- Conversational advice based on conditions
- Location-aware (requires API key)

### File Automation

- **Organize Downloads**: Automatically sorts files by type
- **Organize Desktop**: Cleans up desktop files
- **Category Folders**: Images, Documents, Audio, Video, Archives, Code, etc.

### Conversation History

- MongoDB-backed conversation persistence
- Automatic conversation creation
- Message history tracking
- Conversation titles based on first message
- Works without MongoDB (in-memory mode)

---

## 📁 Project Structure

```
ARIA/
├── aria_core.py                 # Core orchestrator
├── backend_fastapi.py           # FastAPI REST API server
├── brain.py                     # LangChain/OpenAI/Claude/Gemini integration
├── calendar_manager.py          # Google Calendar OAuth
├── command_intent_classifier.py # LLM-based intent classification
├── conversation_manager.py      # MongoDB conversation storage
├── email_manager.py             # Gmail API integration
├── file_automation.py           # File organization automation
├── file_manager.py              # File CRUD operations
├── gui.py                       # CustomTkinter GUI
├── main.py                      # CLI wake word listener
├── music_library.py             # Music URL mappings
├── notion_manager.py            # Notion API integration
├── speech_engine.py             # Faster-Whisper local transcription
├── system_control.py            # System control (volume, power)
├── system_monitor.py            # System monitoring (battery, CPU, RAM)
├── clipboard_screenshot.py      # Clipboard & screenshot operations
├── weather_manager.py           # Weather API integration
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
├── credentials.json             # Google OAuth credentials (download)
├── token.pickle                 # Cached Google Calendar token
├── token_gmail.pickle           # Cached Gmail token
│
├── electron/                    # Electron frontend
│   ├── main.js                  # Electron main process
│   ├── preload.js               # Secure IPC bridge
│   ├── package.json             # Node dependencies
│   └── renderer/                # Frontend assets
│       ├── index.html           # Main HTML
│       ├── app.js               # Frontend logic
│       └── styles.css           # Styling
│
├── docs/                        # Documentation
├── ARIA_USER_MANUAL.md          # User manual
├── DOCUMENTATION.md              # Technical documentation
├── FULL_DOCUMENTATION.md         # Complete documentation
├── GOOGLE_CALENDAR_SETUP.md     # Google Calendar setup guide
├── MONGODB_SETUP.md             # MongoDB setup guide
├── NOTION_SETUP.md              # Notion setup guide
├── SYSTEM_CONTROL_GUIDE.md      # System control guide
└── verify_*.py                   # Verification/test scripts
```

---

## ⚙️ Configuration

### Custom Wake Words

Edit `aria_core.py`:
```python
self.wake_word = "your-wake-word"
```

### AI Model Selection

Models can be selected via:
- Electron UI: Model dropdown in settings
- API: `POST /models/set` endpoint
- Default: `gpt-4o`

### Speech Engine Configuration

Edit `aria_core.py`:
```python
# For Faster-Whisper (local)
self.speech_engine = SpeechEngine(model_size="base")  # tiny, base, small, medium, large-v2
```

### Music Library

Edit `music_library.py`:
```python
music = {
    "lofi": "https://your-music-url.com",
    "jazz": "https://another-url.com"
}
```

### Theme Customization

Edit `electron/renderer/styles.css` for color schemes and styling.

### Safe File Locations

Modify `file_manager.py` to add/remove safe file operation locations.

---

## 🔧 Troubleshooting

### Backend Fails to Start from Electron

- Ensure `.venv` path matches `electron/main.js`
- Check Python executable path in `main.js`
- Verify virtual environment is activated
- Check that FastAPI server starts on port 8000

### SpeechRecognition Errors

```powershell
pip install pipwin
pipwin install pyaudio
```

Or download PyAudio wheel matching your Python version from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio).

### Faster-Whisper Issues

- First run downloads the model automatically (may take time)
- For GPU acceleration, ensure CUDA is installed
- Falls back to CPU if GPU unavailable
- Model size affects accuracy vs speed (tiny < base < small < medium < large-v2)

### Calendar/Gmail Auth Not Working

1. Delete `token.pickle` and `token_gmail.pickle`
2. Ensure `credentials.json` exists in project root
3. Verify Calendar API and Gmail API are enabled in Google Cloud Console
4. Relaunch to trigger OAuth flow

### Voice Mode Stuck on "Waiting"

- Adjust `energy_threshold` in `aria_core.py`
- Increase `phrase_time_limit`
- Check microphone permissions
- Reduce background noise
- Try switching to Faster-Whisper for local transcription

### No AI Responses

1. Verify `.env` contains at least one API key (`OPEN_AI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_API_KEY`)
2. Restart application to reload environment
3. Test with `python verify_openai.py`, `python verify_langchain.py`, or `python verify_models.py`
4. Check model availability via `/models/available` endpoint

### MongoDB Connection Issues

- Ensure MongoDB is running: `mongod`
- Check `MONGODB_URI` in `.env`
- Default: `mongodb://localhost:27017/`
- Conversation history is optional; app works without it (in-memory mode)

### Notion Integration Not Working

1. Verify `NOTION_API_KEY` in `.env`
2. Check `NOTION_DATABASE_ID` is correct
3. Ensure Notion integration is enabled in workspace settings
4. Test with `python verify_notion.py`

### Email Not Sending

1. Verify Gmail API is enabled in Google Cloud Console
2. Check `credentials.json` includes Gmail scopes
3. Delete `token_gmail.pickle` and re-authenticate
4. Ensure email draft confirmation is completed in UI

### Build/Packaging Issues

- `npm run build` outputs to `electron/dist/`
- Bundle `.venv` or create installer for distribution
- Check Electron Builder configuration in `package.json`

---

## 🧪 Testing

Run verification scripts to test integrations:

```powershell
# Test OpenAI connection
python verify_openai.py

# Test all available models
python verify_models.py

# Test LangChain
python verify_langchain.py

# Test Notion integration
python verify_notion.py

# Test weather API
python verify_weather.py

# Test system control
python test_system_control.py

# Test system monitoring
python test_system_monitor.py

# Test email integration
python test_email_integration.py
```

---

## 📚 Additional Documentation

- **[ARIA_USER_MANUAL.md](ARIA_USER_MANUAL.md)** – Complete user guide
- **[FULL_DOCUMENTATION.md](FULL_DOCUMENTATION.md)** – Technical deep dive
- **[GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)** – Google Calendar & Gmail setup guide
- **[NOTION_SETUP.md](NOTION_SETUP.md)** – Notion integration guide
- **[MONGODB_SETUP.md](MONGODB_SETUP.md)** – MongoDB setup instructions
- **[SYSTEM_CONTROL_GUIDE.md](SYSTEM_CONTROL_GUIDE.md)** – System control features

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

## 👤 Author

**Shreyas**

- GitHub: [@shreyass0007](https://github.com/shreyass0007)
- Project: [Aria](https://github.com/shreyass0007/Aria)

---

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- Anthropic for Claude API
- Google for Gemini API and Calendar/Gmail APIs
- LangChain for LLM orchestration
- Electron team for the framework
- Faster-Whisper for local speech recognition
- All open-source contributors

---

<div align="center">

**Made with  by Shreyas**

⭐ Star this repo if you find it helpful!

</div>
