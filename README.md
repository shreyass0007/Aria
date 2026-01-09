# Aria

<div align="center">

<img src="electron/renderer/aria_logo.png" alt="Aria Logo" width="300" height="300">

### Your Premium Desktop AI Assistant

*A powerful local-first AI copilot with a Python brain and polished Electron interface*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Electron](https://img.shields.io/badge/Electron-28.0-47848F?style=for-the-badge&logo=electron&logoColor=white)](https://www.electronjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## ✨ Features

| Category | Capabilities |
|----------|-------------|
| 🎯 **Multi-Interface** | Electron desktop app, CustomTkinter GUI, CLI wake word mode |
| 🧠 **Multi-Model AI** | GPT-4o, Claude 3.5 Sonnet, Claude Opus, Gemini Pro via LangChain |
| 🎙️ **Voice Control** | Wake word detection, Faster-Whisper transcription, Edge-TTS |
| 📧 **Productivity** | Gmail, Google Calendar, Notion integration |
| 🗂️ **System Control** | File management, volume, power, clipboard, screenshots |
| 🎨 **6 Premium Themes** | Violet Dream, Ocean Breeze, Sunset Glow, Forest Mist, Azure, Mono |
| 💬 **Smart Memory** | ChromaDB RAG for semantic search across conversations |
| 🤖 **Proactive Actions** | Calendar monitoring, auto-launch apps, Deep Work mode |
| 👁️ **Computer Vision** | Screen analysis with YOLOv8 + PaddleOCR |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (3.11 recommended)
- **Node.js 18+** 
- **API Key** (OpenAI, Anthropic, or Google)

### Installation

```bash
# Clone repository
git clone https://github.com/shreyass0007/Aria.git
cd ARIA

# Setup Python environment
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Setup Electron frontend
cd electron
npm install

# Run the app
npm start
```

### Environment Setup

Create `.env` in project root:

```env
# Required - At least one AI provider
OPEN_AI_API_KEY=sk-your-key

# Optional
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-key
NOTION_API_KEY=your-key
OPENWEATHER_API_KEY=your-key
```

---

## 🎨 Themes

Aria features **6 beautiful themes** with light/dark mode support:

| Theme | Style | Best For |
|-------|-------|----------|
| **Violet Dream** | Purple gradients | Default, elegant |
| **Ocean Breeze** | Blue tones | Calm, professional |
| **Sunset Glow** | Orange/pink | Warm, creative |
| **Forest Mist** | Green hues | Natural, relaxing |
| **Azure** | White & blue | Clean, corporate |
| **Mono** | Black & white | Minimalist, matches logo |

Access themes via **Settings → Color Theme**.

---

## 🗣️ Voice Commands

```
"Hey Aria, what's on my calendar today?"
"Open VS Code"
"Set volume to 50"
"Send an email to john@example.com about the meeting"
"What's the weather like?"
"Search notion for project notes"
"Create a file called notes.txt on desktop"
"Take a screenshot"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Electron Frontend                 │
│    HTML/CSS + Glassmorphism UI              │
└─────────────────┬───────────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────────┐
│           FastAPI Backend                   │
│    21+ endpoints, background services       │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           Aria Core Engine                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │LangChain│ │Calendar │ │ File    │        │
│  │  Brain  │ │ Manager │ │ Manager │        │
│  └─────────┘ └─────────┘ └─────────┘        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │  TTS    │ │ Email   │ │ChromaDB │        │
│  │ Manager │ │ Manager │ │   RAG   │        │
│  └─────────┘ └─────────┘ └─────────┘        │
└─────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/greeting` | Time-based greeting |
| `GET` | `/briefing` | Morning briefing |
| `POST` | `/message` | Process message |
| `GET` | `/models/available` | List AI models |
| `POST` | `/models/set` | Switch model |
| `GET` | `/conversations` | List conversations |
| `POST` | `/voice/start` | Start voice input |
| `POST` | `/email/send` | Send email |

Full API documentation in [DOCUMENTATION.md](DOCUMENTATION.md).

---

## 🔧 Configuration

### Wake Word
```python
# aria_core.py
self.wake_word = "aria"  # or "neo"
```

### AI Models
Switch via Electron UI dropdown or `POST /models/set`:
- `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- `claude-sonnet`, `claude-haiku`, `claude-opus-4-5`
- `gemini-pro`

### Speech Engine
```python
# tiny, base, small, medium, large-v2
self.speech_engine = SpeechEngine(model_size="base")
```

---

## 📚 Documentation

- [User Manual](ARIA_USER_MANUAL.md)
- [Full Documentation](FULL_DOCUMENTATION.md)
- [Google Calendar Setup](GOOGLE_CALENDAR_SETUP.md)
- [Notion Setup](NOTION_SETUP.md)
- [System Control Guide](SYSTEM_CONTROL_GUIDE.md)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/Amazing`)
3. Commit changes (`git commit -m 'Add Amazing'`)
4. Push to branch (`git push origin feature/Amazing`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Shreyas** - [@shreyass0007](https://github.com/shreyass0007)

---

<div align="center">

**Made with ❤️ by Shreyas**

⭐ Star this repo if you find it helpful!

</div>
