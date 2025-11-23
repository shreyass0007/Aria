# Aria Assistant – Full Documentation

## 📅 Project Timeline
| Phase | Dates | Core Goals |
|------|-------|------------|
| **Phase -1** | **Pre‑Sept 2025** | Conceptual design, requirements gathering, tech‑stack selection (Python, CustomTkinter, LLM integration). |
| **Phase 0** | **Early Sept 2025** | Prototype skeleton: basic UI, placeholder voice input, simple echo bot. |
| **Phase 1** | **Sept 21 2025 – Oct 15 2025** | • **Open API** – `backend_api.py` with `/chat` & `/play` endpoints.  
| | | • **Website function** – Electron wrapper (`electron/main.js`, `preload.js`) serving a minimal web UI.  
| | | • **Music playback** – `music_library.py` scans a `music/` folder and plays tracks. |
| **Phase 2** | **Oct 16 2025 – Oct 30 2025** | UI polish: dark mode, chat‑bubble layout, micro‑animations, responsive design. |
| **Phase 3** | **Nov 1 2025 – Present** | **API‑key handling** – secure loading of `GEMINI_API_KEY` and `OPENAI_API_KEY` from a `.env` file via `python‑dotenv`.  
| | | LLM upgrade: switched to LangChain + OpenAI `gpt‑4o` in `brain.py`.  
| | | Structured‑output demo (`demo_structured_output.py`). |
| **Phase 4** | **Future (Nov 2025)** | Feature expansion: Google Calendar integration, wake‑word customization, TTS improvements, richer UI components. |
| **Phase 5** | **Future** | Stability & testing: extensive unit tests, CI pipeline, cross‑platform packaging with PyInstaller. |
| **Phase 6** | **Future** | Advanced roadmap: offline wake‑word detection, plugin ecosystem, on‑device LLM inference, multi‑modal UI (video calls, screen sharing). |

## 🔑 Key Components
- **`main.py`** – Application entry point, launches CustomTkinter UI.
- **`gui.py`** – UI definition, handles user interaction, theme toggling.
- **`brain.py`** – LLM interaction layer (LangChain + OpenAI). Uses API keys from `.env`.
- **`backend_api.py`** – Flask‑style REST API exposing chat and music endpoints.
- **`music_library.py`** – Scans `music/` directory, provides `play_song(title)`.
- **`calendar_manager.py`**, **`notion_manager.py`** – External service connectors (future phases).
- **`electron/`** – Electron main process (`main.js`) and preload script (`preload.js`) for web UI.
- **`.env`** – Stores `GEMINI_API_KEY` and `OPENAI_API_KEY` (Phase 3). 

## 📦 Setup & Usage
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create a `.env` file** (required from Phase 3 onward)
   ```
   GEMINI_API_KEY=your_gemini_key
   OPENAI_API_KEY=your_openai_key
   ```
3. **Run the application**
   ```bash
   python main.py
   ```
   - The Electron UI can be launched via `npm start` inside the `electron/` folder (if needed).
4. **API usage** – Send POST requests to `http://localhost:5000/chat` or `/play` (see `backend_api.py`).

## 🛠️ Development Notes
- All secret keys are loaded at runtime using `dotenv.load_dotenv()`; never commit `.env` to version control.
- Phase 3 introduced LangChain `ChatOpenAI` wrapper for structured responses.
- Future phases will add more environment variables (e.g., `GOOGLE_CALENDAR_TOKEN`).

---
*This documentation was generated from scratch to cover phases -1 through 6, with the current status at Phase 3.*
