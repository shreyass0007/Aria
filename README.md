# Aria – Desktop AI Assistant

Premium local-first AI copilot that pairs a Python brain with a polished Electron interface. Aria listens for a wake word, understands natural language, controls desktop apps, searches the web, schedules calendar events through Google Calendar, and replies with neural TTS.

---

## Highlights
- 🎯 **Unified assistant** – same core powers a sidebar Electron app, CustomTkinter window, and CLI listener
- 🎨 **Premium UX** – Arc-style glassmorphism, light/dark themes, subtle animations, onboarding messages
- 🧠 **LangChain + OpenAI** – `brain.py` orchestrates GPT‑4o for free-form questions and calendar parsing
- 🗓️ **Calendar automation** – authenticate once, then say “schedule standup tomorrow 9am” to create events
- 🎙️ **Hands-free voice mode** – microphone loop with wake word, speech recognition, and gTTS playback
- 🧭 **Desktop control** – fuzzy .lnk indexing lets you open installed apps (“open figma”, “open chrome”)
- 🌐 **Smart browsing** – curated shortcuts plus generic “open site.com” and “google <query>” flows

---

## Architecture Overview

```
┌───────────────┐        HTTP /voice + /message        ┌────────────────────┐
│ Electron UI   │ <──────────────────────────────────> │ Flask API backend  │
│ (renderer/)   │                                       │ backend_api.py     │
└──────┬────────┘                                       └─────────┬──────────┘
       │ preload IPC                                               │
       │                                                           ▼
 ┌─────▼────────┐      speech, commands, calendar      ┌────────────────────┐
 │ main.js      │──────────────┬──────────────────────▶│ AriaCore / Brain   │
 │ launches .venv│             │                       │ aria_core.py       │
 └──────────────┘             │                       │ brain.py           │
                              │                       └────────────────────┘
                              │ gTTS / SpeechRecognition / Google Calendar
                              ▼
                        Optional GUIs (`gui.py`, `main.py`)
```

Key components:
- `backend_api.py` – Flask API that exposes `/health`, `/message`, and `/voice/*` routes for the Electron app.
- `aria_core.py` – orchestrates speech, intent routing, desktop control, and fallback to `AriaBrain`.
- `brain.py` – LangChain bridge to GPT‑4o plus calendar-intent parsing; needs `OPEN_AI_API_KEY`.
- `calendar_manager.py` – Google Calendar OAuth storing `token.pickle`; requires `credentials.json`.
- `electron/` – sidebar UI that spawns the Python backend, renders chat/voice controls, and handles theme + settings.
- `gui.py` / `main.py` – legacy CustomTkinter UI and CLI listener that run the same core logic.

---

## Prerequisites

| Requirement | Version / Notes |
|-------------|-----------------|
| Python | 3.10+ recommended (project tested on Windows 11) |
| Node.js & npm | Node 18+ (Electron 28 requires ≥18.0.0) |
| FFmpeg (optional) | Improves gTTS MP3 playback reliability |
| Microphone & speakers | Needed for voice mode and audio responses |
| OpenAI API key | Set `OPEN_AI_API_KEY` in `.env` for LangChain |
| Google Cloud project | Download `credentials.json` for Calendar API access |

SpeechRecognition on Windows also requires PyAudio; install the correct wheel if pip fails with build errors.

---

## Setup

### 1. Python environment

```powershell
cd D:\CODEING\PROJECTS\ARIA
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` in the project root:

```
OPEN_AI_API_KEY=sk-...
```

### 2. Node / Electron

```powershell
cd electron
npm install
```

### 3. Google Calendar credentials (optional but recommended)
1. Enable the Google Calendar API in Google Cloud Console.
2. Create an **OAuth client ID (Desktop App)** and download `credentials.json`.
3. Place the file at the project root next to `calendar_manager.py`.
4. First run will open a browser window; consent and a `token.pickle` file will be cached for later use.

### 4. Optional tuning
- Edit `music_library.py` to map song names to URLs (`music = {"lofi": "https://..."}`).
- Update `aria_core.py` mappings for additional quick-launch sites or custom wake words.
- Replace assets in `aria_logo.png`, `send_icon.png`, or update colors inside `electron/renderer/styles.css`.

---

## Running Aria

### Electron desktop experience (recommended)
```powershell
cd D:\CODEING\PROJECTS\ARIA\electron
npm start
```
- Spawns the Python backend from `.venv`, opens a sidebar window, and connects via HTTP.
- Use `npm run dev` to open Chrome DevTools alongside the window.
- Build installers with `npm run build` (Electron Builder, NSIS target).

### CustomTkinter window
```powershell
.venv\Scripts\activate
python gui.py
```
- Offers the same premium styling in a native CustomTkinter app with voice toggle and settings.

### Wake-word CLI loop
```powershell
.venv\Scripts\activate
python main.py
```
- Minimal interface that keeps listening for “aria” (or “neo”), then processes the next utterance.

### Backend-only mode (for API testing)
```powershell
.venv\Scripts\activate
python backend_api.py
```
Endpoints will be available at `http://localhost:5000` for REST clients or the Electron renderer.

---

## API Surface

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Simple status check used by the renderer watchdogs |
| POST | `/message` | Body `{ "message": "text" }`; returns `{ response: "..." }` from Aria |
| POST | `/voice/start` | Flags the backend to begin microphone polling |
| GET | `/voice/listen` | Long-poll endpoint returning transcribed text once wake word detected |
| POST | `/voice/stop` | Stops the background listening loop |

All responses are JSON; errors return `{ status: "error", error: "<message>" }`.

---

## Feature Details

- **Voice pipeline** – `SpeechRecognition` with a thread-safe lock avoids microphone contention. Wake-word “aria” (configurable) triggers command parsing; replies are synthesized with `gTTS` + `pygame` playback.
- **Desktop launching** – `aria_core.py` indexes shortcuts under `ProgramData` and `%APPDATA%` Start Menu folders. It supports exact, substring, and fuzzy matches, then falls back to `os.startfile`.
- **Web automation** – curated commands like “open instagram” or “play my playlist” map to known URLs; otherwise any “open <site>” request tries `.com` or provided domain.
- **LangChain brain** – if a voice/text request is not matched by heuristics, Aria forwards it to GPT‑4o via `langchain-openai`. The same LLM extracts structured `summary`, `start_time`, and `end_time` for calendar events.
- **Calendar manager** – creates events in the primary calendar (defaults to Asia/Kolkata). `get_upcoming_events()` summarizes the next five meetings for prompts like “what do I have today?”.
- **Electron renderer** – `app.js` handles chat rendering, voice state, local theme persistence, settings modal, and communicates with Flask via `fetch`. CSS replicates Arc browser-inspired visuals.
- **CustomTkinter UI** – replicates the Electron UX natively, complete with animated buttons, scrollable chat cards, and theme toggles.

---

## Project Structure

```
ARIA/
├── aria_core.py             # Command router, speech IO, desktop control
├── backend_api.py           # Flask server exposing REST + voice polling endpoints
├── brain.py                 # LangChain/OpenAI brain + calendar intent parsing
├── calendar_manager.py      # Google Calendar OAuth and event utilities
├── gui.py                   # CustomTkinter experience
├── main.py                  # Wake-word CLI loop
├── music_library.py         # User-editable song → URL mapping
├── requirements.txt         # Python dependencies
├── electron/
│   ├── main.js              # Electron main process, spawns backend
│   ├── preload.js           # Secure IPC bridge
│   └── renderer/            # HTML/CSS/JS frontend assets
└── verify_*.py              # Helper scripts to validate LangChain/OpenAI wiring
```

---

## Troubleshooting & Tips

- **Backend fails to start from Electron** – ensure the `.venv` path matches `electron/main.js`. If you renamed the venv, adjust `pythonExecutable`.
- **SpeechRecognition errors** – install PyAudio wheels that match your Python version, e.g. `pip install pipwin && pipwin install pyaudio`.
- **Calendar auth dialog not opening** – delete `token.pickle` and relaunch to re-run the OAuth flow; confirm `credentials.json` exists.
- **Voice mode stuck on “waiting”** – background noise may trip the energy threshold; tweak `self.recognizer.energy_threshold` or increase `phrase_time_limit`.
- **No AI responses** – confirm `.env` contains `OPEN_AI_API_KEY` and restart so `load_dotenv()` picks it up. Use `verify_openai.py` or `verify_langchain.py` to smoke-test the key.
- **Packaged build** – `npm run build` outputs NSIS artifacts in `electron/dist`. Bundle your `.venv` or ship a backend installer depending on your distribution plan.

---

## License

MIT License. See `LICENSE` (coming soon) or embed your preferred terms before distribution.

---

Developed with ❤️ by Shreyas – now with a comprehensive README.
