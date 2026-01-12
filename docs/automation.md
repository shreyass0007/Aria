# Aria Desktop Automation - System Documentation

## 1. Architecture Overview
Aria's Desktop Automation transforms the conversational AI into an autonomous agent using a "Three-Brain Architecture":
- **Chat Brain**: Handles conversations (GPT/Claude).
- **RAG Brain**: Manages memory and knowledge (ChromaDB).
- **Planner Brain**: Executes desktop tasks (Llama 3.2).

### System Flow
User Input -> Intent Classifier -> Planner Brain -> JSON Plan -> Safety Gate -> Executor -> OS

## 2. Action Vocabulary (Phase 1)
The following actions are supported in the initial release:
1. `open_app`: Launch an application.
2. `close_app`: Close an application.
3. `type`: Type text at current focus.
4. `press`: Press a keyboard key or combination.
5. `wait`: Pause execution for N seconds.
6. `click`: Click at specific coordinates.
7. `read_screen`: Capture text from screen.

## 3. Safety Guidelines
Safety is paramount. The system enforces:
- **Action Whitelist**: Only approved actions are allowed.
- **Action Limit**: Maximum of 10 actions per plan.
- **Prohibited Actions**: `delete_file`, `run_shell`, `download`, `network_request`, etc.
- **User Confirmation**: Required for high-risk actions or unknown patterns.

## 4. Developer Guide
- **Planner**: Located in `aria.brains.planner_brain`.
- **Executor**: Located in `aria.executor`.
- **Safety**: Located in `aria.safety`.
- **Adapters**: OS-specific adapters in `aria.executor`.
