# Aria – Voice & GUI AI Assistant

Aria is a Windows-friendly personal assistant that combines a modern CustomTkinter GUI, wake-word voice controls, and Gemini-powered small talk. It can open desktop apps, launch websites, search Google, summarize topics with Wikipedia, and play custom music links — all while keeping a lightweight footprint that anyone can run locally.

## Highlights
- **Two ways to interact**: Wake-word driven CLI loop (`main.py`) or a floating chat-style GUI (`gui.py`) with voice toggle.
- **Desktop automation**: Indexes your Start Menu shortcuts so `open spotify` can launch the installed desktop app before falling back to web links.
- **Smart browsing shortcuts**: Built-in phrases for Instagram, YouTube, GitHub, LinkedIn, WhatsApp, and more, plus generic URL handling.
- **Search & knowledge**: Google searches for anything it cannot open directly and fetches short Wikipedia summaries for quick facts.
- **Music launcher**: Point `music_library.py` to your own playlist URLs and ask Aria to play them (fuzzy matching included).
- **Optional agentic replies**: Connect a `GEMINI_API_KEY` to let AriaBrain answer arbitrary questions via Google’s Gemini models.
- **Voice + TTS pipeline**: Uses SpeechRecognition + PyAudio for microphone input and gTTS + pygame for spoken feedback.

## Project Structure
| Path | Description |
|------|-------------|
| `main.py` | Wake-word CLI loop (voice-only) |
| `gui.py` | CustomTkinter chat UI with text + voice controls |
| `aria_core.py` | Core assistant logic (speech, intents, app/indexing, web helpers) |
| `brain.py` | Gemini integration via `google-generativeai` |
| `music_library.py` | User-editable dict of song name → URL mappings |
| `requirements.txt` | Python dependencies |

## Requirements
- Python 3.10+ (tested on Windows 10/11)
- Working microphone & speakers
- Internet connection (speech recognition, gTTS, Gemini)
- Recommended: virtual environment

Python packages (install via `pip install -r requirements.txt`):
- SpeechRecognition, PyAudio, gTTS, pygame
- wikipedia, customtkinter, Pillow
- google-generativeai, python-dotenv

> **Windows tip:** If `pip install pyaudio` fails, install [`pipwin`](https://pypi.org/project/pipwin/) and run `pipwin install pyaudio`.

## Setup
```bash
git clone https://github.com/shreyass0007/Aria
cd ARIA
python -m venv .venv
.venv\Scripts\activate          # PowerShell
pip install -r requirements.txt
```

Create a `.env` file (same directory as `brain.py`) if you want Gemini-powered responses:
```
GEMINI_API_KEY=your_api_key_here
```

## Running Aria
### Chat-style GUI
```bash
python gui.py
```
- Type messages at the bottom input field or toggle the mic button to go hands-free.
- Use the gear icon for quick actions (clear chat, toggle theme, about dialog).
- Voice mode listens for the wake word (“aria” by default) even while the UI stays responsive.

### Voice-first CLI
```bash
python main.py
```
- You’ll hear “Welcome back. I am ready.”
- Say “Aria” (or similar-sounding variants) to wake it, then issue your command.
- Say “exit” or press `Ctrl+C` to quit.

## What You Can Ask
- **Open desktop apps**: “open spotify”, “open chrome” (uses Start Menu index + fuzzy matching)
- **Launch websites**: “open instagram”, “open whatsapp”, “open google.com”, “open netflix”
- **Google search**: “google python decorators”, “search nearest cafes”
- **Wikipedia summaries**: “tell me about Ada Lovelace”, “who is Virat Kohli”
- **Music**: “play my playlist”, “play believer” (looks up `music_library.music`)
- **Small talk & exits**: “tum best ho”, “exit”, “quit”

If a command isn’t recognized and Gemini is configured, AriaBrain will attempt a generative response; otherwise you’ll get a friendly fallback message.

## Customization
- **Music library**: Update `music_library.py` with your own mapping:
  ```python
  music = {
      "lofi beats": "https://youtu.be/your_playlist",
      "believer": "https://youtu.be/7wtfhZwyrcc",
  }
  ```
- **Wake word**: Change `self.wake_word` in `AriaCore` or say “change wake word to <phrase>”.
- **GUI look & feel**: Adjust colors/fonts in `gui.py` or swap the send button icon (`send_icon.png` placeholder).
- **Command mapping**: Extend the keyword → URL list in `aria_core.py` to add new quick links.

## Troubleshooting
- **Microphone not detected**: Ensure PyAudio installed correctly, check Windows privacy settings, and verify default recording device.
- **Speech not recognized**: Reduce background noise; Aria auto-adjusts ambient noise but works best in quiet environments.
- **No voice output**: gTTS requires internet; pygame mixer needs an available audio device.
- **Desktop apps not opening**: Allow indexing some time after startup; Aria scans `%ProgramData%` and `%AppData%` Start Menu folders.
- **Gemini errors**: Confirm `.env` contains a valid `GEMINI_API_KEY` and that the account has access to `gemini-1.5-flash`.

## Future Updates
- **MongoDB workspace memory**: Persist notes, tasks, meeting transcripts, and contextual preferences so Aria can resume conversations across sessions.
- **ElevenLabs neural voice**: Replace the basic gTTS output with ultra-realistic voices and emotion controls using the ElevenLabs API.
- **Model Context Protocol (MCP)**: Add formal MCP hooks so other agents/tools can stream context into AriaCore, enabling richer multi-agent workflows.
- **Agentic behaviors**: Expand the brain to schedule meetings, take structured notes, manage task lists, and follow up on reminders automatically.
- **Better automations**: Integrate with calendar/email APIs, expose plugin hooks for custom commands, and ship a settings panel for mapping additional desktop apps/services.
- **Cross-platform polish**: Package the GUI into a standalone executable, add auto-update checks, and tighten microphone/audio setup flows for macOS/Linux users.

## Contributing
Pull requests and feature ideas are welcome! Feel free to open issues for bugs, new voice intents, or GUI improvements.

## License
Provided “as is” for personal use — adapt it, learn from it, and have fun building your own assistant.
