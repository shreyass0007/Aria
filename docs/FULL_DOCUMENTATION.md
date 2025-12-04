# Aria - The Advanced Agentic AI Assistant

**Aria** is a next-generation, cross-platform desktop assistant designed to bridge the gap between traditional voice assistants and modern agentic AI. By combining a robust Python backend with a sleek Electron-based frontend, Aria offers a premium, highly interactive user experience capable of complex tasks ranging from natural language conversation to system automation and productivity management.

---

## 1. Technology Stack

Aria is built on a hybrid architecture leveraging the best of system-level Python and web-based rendering.

### **Core Backend (Python 3.10+)**
- **Logic & Orchestration**: `AriaCore` (Custom state machine for command processing).
- **AI & NLP**: 
  - **LangChain**: For orchestrating LLM interactions and structured data parsing.
  - **OpenAI GPT-4o**: The primary intelligence engine for reasoning, summarization, and intent extraction.
  - **Google Gemini**: (Legacy/Alternative) Supported for specific NLP tasks.
- **Speech Processing**:
  - **Input**: `SpeechRecognition` (Google Speech API) for high-accuracy wake-word and command detection.
  - **Output**: `gTTS` (Google Text-to-Speech) and `pygame` for fluid, natural-sounding voice responses.
- **System Integration**:
  - `subprocess`, `os`, `webbrowser`: For controlling system apps, file system, and web navigation.
  - `difflib`: For fuzzy matching application names and commands.

### **Frontend & UI**
- **Electron (Node.js)**: Provides a modern, responsive "web-like" interface for the desktop.
  - **HTML5/CSS3**: For a polished, chat-bubble style layout with animations.
  - **IPC (Inter-Process Communication)**: Bridges the JavaScript UI with the Python backend.
- **CustomTkinter (Legacy/Native)**: A secondary native Python GUI for lightweight usage or system tray operations.

### **Integrations & APIs**
- **Google Calendar API**: For scheduling and event management.
- **Notion API**: For knowledge base management, page summarization, and note-taking.
- **Spotify/YouTube**: For media playback control.

---

## 2. Architecture

Aria follows a **Client-Server-Service** model running locally on the user's machine.

```mermaid
graph TD
    subgraph "Frontend (Electron)"
        UI[User Interface] -->|IPC/HTTP| Bridge[Electron Main Process]
    end

    subgraph "Backend (Python)"
        Bridge -->|JSON| API[Flask/REST API]
        API --> Core[Aria Core]
        
        Core --> Brain[Aria Brain (LangChain)]
        Core --> Ears[Speech Recognition]
        Core --> Mouth[TTS Engine]
        
        Core --> Mgr1[Calendar Manager]
        Core --> Mgr2[Notion Manager]
        Core --> Mgr3[System Controller]
    end

    subgraph "External Cloud Services"
        Brain <-->|API| OpenAI[OpenAI GPT-4o]
        Mgr1 <-->|API| GCal[Google Calendar]
        Mgr2 <-->|API| Notion[Notion Cloud]
    end
```

### **Data Flow**
1.  **Input**: User speaks ("Hey Aria...") or types a command.
2.  **Processing**: 
    - Audio is converted to text via `SpeechRecognition`.
    - Text is analyzed by `AriaCore` for local commands (e.g., "Open Chrome").
    - Complex queries are routed to `AriaBrain`.
3.  **Intelligence**: `AriaBrain` uses LangChain to prompt GPT-4o, extracting intent (e.g., "Schedule a meeting") or generating a conversational response.
4.  **Action**: The backend executes the action (e.g., API call to Notion) or generates speech.
5.  **Response**: The result is sent back to the Electron UI to be displayed as a chat bubble and spoken aloud.

---

## 3. System Design

### **Core Modules**
- **`main.py`**: The entry point. Initializes the `AriaCore` and starts the UI event loop.
- **`aria_core.py`**: The central nervous system. It handles the "Listen-Think-Act" loop, manages threads for listening, and routes commands to specific managers.
- **`brain.py`**: The cognitive layer. Encapsulates all LLM logic. It contains prompt templates for:
    - General conversation.
    - Calendar intent parsing (JSON extraction).
    - Notion page search and summarization.
- **`gui.py` / `electron/`**: Handles visual presentation. The Electron app reads the state and renders the chat history, while `gui.py` offers a native fallback.

### **Key Design Patterns**
- **Singleton Pattern**: Used for `AriaCore` to ensure only one instance controls the microphone and system resources.
- **Factory Pattern**: Used in `brain.py` to generate different types of LangChain chains based on the user's intent.
- **Observer Pattern**: The UI subscribes to events from `AriaCore` to update the chat window in real-time when the AI speaks or acts.

---

## 4. User Interface (UI)

Aria's UI is designed to be **"Invisible but Present"**.

- **Aesthetics**: Modern, glassmorphism-inspired design with a blur backdrop.
- **Layout**:
    - **Sidebar Mode**: Docks to the side of the screen to act as a companion without obscuring work.
    - **Chat Bubbles**: distinct, color-coded bubbles (Right for User, Left for Aria).
- **Visual Feedback**:
    - **Pulsing Orb**: Indicates when Aria is listening or processing.
    - **Dynamic Avatars**: Changes state based on context (Listening, Speaking, Idle).
- **Themes**: Native support for Light and Dark modes, respecting system preferences.

---

## 5. Use Cases

### **1. Productivity & Organization**
- **Smart Scheduling**: "Schedule a meeting with the design team next Tuesday at 3 PM."
- **Knowledge Management**: "Summarize my Notion page about 'Project Alpha'."
- **Note Taking**: "Add a task to my Notion to buy groceries."

### **2. System Control**
- **App Launching**: "Open VS Code", "Launch Spotify".
- **Web Navigation**: "Open YouTube", "Search Google for latest AI news".

### **3. Information & Research**
- **Summarization**: "Summarize this article..." (via clipboard or URL).
- **Q&A**: "Explain quantum computing in simple terms."

### **4. Entertainment**
- **Music Control**: "Play some lo-fi music."
- **Casual Chat**: Natural, context-aware conversation.

---

## 6. Development Roadmap (Phases 1-6)

### **Phase 1: The Foundation (Completed)**
- **Goal**: Build a basic voice-activated command runner.
- **Features**:
    - Basic Speech-to-Text (STT) and Text-to-Speech (TTS).
    - Simple keyword matching ("Open Chrome", "Time").
    - Native `customtkinter` GUI.

### **Phase 2: Intelligence Upgrade (Completed)**
- **Goal**: Move from regex to LLM-based understanding.
- **Features**:
    - Integration of Google Gemini API.
    - Basic conversational abilities beyond hardcoded commands.
    - Context-aware greetings ("Good Morning").

### **Phase 3: The Agentic Shift (Completed)**
- **Goal**: Enable the AI to take actions, not just talk.
- **Features**:
    - Migration to **LangChain + OpenAI GPT-4o**.
    - **Structured Output**: Ability to output JSON for function calling.
    - **Notion Integration**: Reading and writing to Notion databases.

### **Phase 4: Modernization (Current)**
- **Goal**: Create a premium, consumer-ready UI.
- **Features**:
    - **Electron Migration**: Replacing Tkinter with a React/Vanilla JS frontend.
    - **Hybrid Architecture**: Python backend + Web frontend.
    - **Visual Polish**: Animations, themes, and responsive design.

### **Phase 5: Deep Integration (Planned)**
- **Goal**: Full OS-level control and advanced scheduling.
- **Features**:
    - **Google Calendar Write Access**: Full CRUD operations for events.
    - **File System Agent**: "Find the PDF I downloaded yesterday."
    - **Email Management**: Draft and send emails via voice.

### **Phase 6: The Autonomous Future (Future)**
- **Goal**: Proactive assistance and multi-modal capabilities.
- **Features**:
    - **Vision**: "Look at my screen and tell me what's wrong with this code."
    - **Proactive Suggestions**: "You have a meeting in 10 mins, should I open the Zoom link?"
    - **Local LLM Support**: Running Llama/Mistral locally for privacy.

---

## 7. How to Use Aria Effectively

### **Setup**
1.  **Install Dependencies**: `pip install -r requirements.txt` & `npm install` (in `electron/`).
2.  **Environment Variables**: Create a `.env` file with:
    ```env
    OPENAI_API_KEY=sk-...
    NOTION_TOKEN=secret_...
    GOOGLE_CREDENTIALS=...
    ```
3.  **Launch**: Run `python main.py` (or `npm start` for dev mode).

### **Voice Commands**
- **Wake Word**: Say **"Aria"** to grab attention.
- **Natural Language**: You don't need rigid commands.
    - *Instead of:* "Open Calculator"
    - *Try:* "I need to do some math, open the calculator."
- **Context**: Aria remembers the last few turns of conversation.

### **Text Mode**
- Use the input box at the bottom of the UI to type complex queries or code snippets that are hard to dictate.

---

## 8. Future Development

The vision for Aria is to become a **fully autonomous AI agent** that lives on your desktop.

- **Plugin System**: Allow developers to write Python plugins for new apps (e.g., Trello, Slack).
- **Memory**: Long-term memory vector database (Pinecone/Chroma) to remember user preferences and past projects indefinitely.
- **Voice Cloning**: Allow users to clone their own voice or choose from high-quality neural voices for Aria.
