# Aria – Voice & GUI AI Assistant

Aria is a Windows-friendly personal assistant that combines a modern CustomTkinter GUI, wake-word voice controls, and OpenAI-powered intelligent responses. It can open desktop apps, launch websites, search Google, manage your Google Calendar, and play custom music links — all while keeping a lightweight footprint that anyone can run locally.

## Highlights
- **Two ways to interact**: Wake-word driven CLI loop (`main.py`) or a floating chat-style GUI (`gui.py`) with voice toggle.
- **Desktop automation**: Indexes your Start Menu shortcuts so `open spotify` can launch the installed desktop app before falling back to web links.
- **Smart browsing shortcuts**: Built-in phrases for Instagram, YouTube, GitHub, LinkedIn, WhatsApp, and more, plus generic URL handling.
- **Calendar management**: Create and view calendar events using natural language commands with Google Calendar integration.
- **Music launcher**: Point `music_library.py` to your own playlist URLs and ask Aria to play them (fuzzy matching included).
- **AI-powered responses**: Connect an `OPEN_AI_API_KEY` to let AriaBrain answer arbitrary questions via OpenAI's GPT-4o model using LangChain.
- **Intelligent scheduling**: Natural language calendar event creation with automatic time parsing (e.g., "schedule a meeting tomorrow at 3pm").
- **Voice + TTS pipeline**: Uses SpeechRecognition + PyAudio for microphone input and gTTS + pygame for spoken feedback.

## Project Structure
| Path | Description |
|------|-------------|
| `main.py` | Wake-word CLI loop (voice-only) |
| `gui.py` | CustomTkinter chat UI with text + voice controls |
| `aria_core.py` | Core assistant logic (speech, intents, app/indexing, web helpers) |
| `brain.py` | OpenAI integration via LangChain (`langchain-openai`) |
| `calendar_manager.py` | Google Calendar API integration for event management |
| `music_library.py` | User-editable dict of song name → URL mappings |
| `requirements.txt` | Python dependencies |

## Requirements
- Python 3.10+ (tested on Windows 10/11)
- Working microphone & speakers
- Internet connection (speech recognition, gTTS, OpenAI API, Google Calendar API)
- Recommended: virtual environment

Python packages (install via `pip install -r requirements.txt`):
- SpeechRecognition, PyAudio, gTTS, pygame
- wikipedia, customtkinter, Pillow
- langchain, langchain-openai (for AI responses)
- google-api-python-client, google-auth-httplib2, google-auth-oauthlib (for Calendar)
- python-dotenv

> **Windows tip:** If `pip install pyaudio` fails, install [`pipwin`](https://pypi.org/project/pipwin/) and run `pipwin install pyaudio`.

## Setup

### 1. Clone and Install Dependencies
```bash
git clone https://github.com/shreyass0007/Aria
cd ARIA
python -m venv .venv
.venv\Scripts\activate          # PowerShell
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file (same directory as `brain.py`) if you want AI-powered responses:
```
OPEN_AI_API_KEY=your_openai_api_key_here
```

### 3. Setup Google Calendar (Optional)
To enable calendar features:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID for Desktop application)
5. Download the credentials file and save it as `credentials.json` in the project root
6. On first run, Aria will open a browser for authentication and save a `token.pickle` file

> **Note:** Calendar features will gracefully disable if `credentials.json` is not found, allowing Aria to function normally for other tasks.

## Running Aria
### Chat-style GUI
```bash
python gui.py
```
- Type messages at the bottom input field or toggle the mic button to go hands-free.
- Use the gear icon for quick actions (clear chat, toggle theme, about dialog).
- Voice mode listens for the wake word ("aria" by default) even while the UI stays responsive.

### Voice-first CLI
```bash
python main.py
```
- You'll hear "Welcome back. I am ready."
- Say "Aria" (or similar-sounding variants) to wake it, then issue your command.
- Say "exit" or press `Ctrl+C` to quit.

## What You Can Ask
- **Open desktop apps**: "open spotify", "open chrome" (uses Start Menu index + fuzzy matching)
- **Launch websites**: "open instagram", "open whatsapp", "open google.com", "open netflix"
- **Google search**: "google python decorators", "search nearest cafes"
- **Calendar management**: 
  - "schedule a meeting tomorrow at 3pm"
  - "remind me to call John next Friday at 2pm"
  - "what do i have coming up?" / "my schedule" / "upcoming events"
- **Time and date**: "what time is it?", "what's the date?"
- **Music**: "play my playlist", "play believer" (looks up `music_library.music`)
- **Small talk & exits**: "tum best ho", "exit", "quit"

If a command isn't recognized and OpenAI is configured, AriaBrain will attempt an intelligent response; otherwise you'll get a friendly fallback message.

## Customization
- **Music library**: Update `music_library.py` with your own mapping:
  ```python
  music = {
      "lofi beats": "https://youtu.be/your_playlist",
      "believer": "https://youtu.be/7wtfhZwyrcc",
  }
  ```
- **Wake word**: Change `self.wake_word` in `AriaCore` or say "change wake word to <phrase>".
- **GUI look & feel**: Adjust colors/fonts in `gui.py` or swap the send button icon (`send_icon.png` placeholder).
- **Command mapping**: Extend the keyword → URL list in `aria_core.py` to add new quick links.

## Troubleshooting
- **Microphone not detected**: Ensure PyAudio installed correctly, check Windows privacy settings, and verify default recording device.
- **Speech not recognized**: Reduce background noise; Aria auto-adjusts ambient noise but works best in quiet environments.
- **No voice output**: gTTS requires internet; pygame mixer needs an available audio device.
- **Desktop apps not opening**: Allow indexing some time after startup; Aria scans `%ProgramData%` and `%AppData%` Start Menu folders.
- **OpenAI errors**: Confirm `.env` contains a valid `OPEN_AI_API_KEY` and that your account has access to the OpenAI API.
- **Calendar not working**: 
  - Ensure `credentials.json` is in the project root
  - Check that Google Calendar API is enabled in your Google Cloud project
  - Delete `token.pickle` and re-authenticate if you encounter authorization errors
  - Calendar features will be disabled gracefully if credentials are missing

## Technology Stack
- **AI Engine**: OpenAI GPT-4o via LangChain for intelligent responses and calendar intent parsing
- **Speech Recognition**: Google Speech Recognition API via `SpeechRecognition`
- **Text-to-Speech**: Google Text-to-Speech (gTTS)
- **Calendar Integration**: Google Calendar API v3
- **GUI Framework**: CustomTkinter for modern, native-looking interface

## Future Updates
- **MongoDB workspace memory**: Persist notes, tasks, meeting transcripts, and contextual preferences so Aria can resume conversations across sessions.
- **ElevenLabs neural voice**: Replace the basic gTTS output with ultra-realistic voices and emotion controls using the ElevenLabs API.
- **Model Context Protocol (MCP)**: Add formal MCP hooks so other agents/tools can stream context into AriaCore, enabling richer multi-agent workflows.
- **Enhanced agentic behaviors**: Expand the brain to take structured notes, manage task lists, and follow up on reminders automatically.
- **Better automations**: Integrate with email APIs, expose plugin hooks for custom commands, and ship a settings panel for mapping additional desktop apps/services.
- **Cross-platform polish**: Package the GUI into a standalone executable, add auto-update checks, and tighten microphone/audio setup flows for macOS/Linux users.

## Contributing
Pull requests and feature ideas are welcome! Feel free to open issues for bugs, new voice intents, or GUI improvements.

## License
Provided "as is" for personal use — adapt it, learn from it, and have fun building your own assistant.
