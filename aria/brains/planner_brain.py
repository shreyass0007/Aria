
import json
import logging
from typing import Dict, Any, List
import ollama
from aria.executor.state_monitor import DesktopStateMonitor

logger = logging.getLogger(__name__)

class PlannerBrain:
    """
    Planner Brain responsible for decomposing natural language requests into
    executable desktop automation plans using Llama 3.2.
    """
    
    SYSTEM_PROMPT = """You are Aria's Planner Brain, an expert desktop automation agent.
Your goal is to convert user requests into a structured JSON plan using a specific action vocabulary.

**Allowed Actions:**
1. open_app(name: str): Launch an application (e.g., "notepad", "chrome").
2. close_app(name: str): Close an application.
3. type(text: str): Type text at the current cursor position.
4. press(key: str): Press a keyboard key (e.g., "enter", "tab", "ctrl+c").
5. wait(seconds: float): Pause execution.
6. click(x: int, y: int): Click at coordinates.
7. read_screen(): Read text from the screen.
8. click_text(text: str): Click on the specified text on the screen.
9. wait_for_text(text: str, timeout: float): Wait for text to appear (default timeout 10s).
10. focus_window(title: str): Bring a window to the foreground (e.g., "notepad").

**Rules:**
- Output MUST be valid JSON.
- The root object must contain an "actions" list.
- Each action object must have "action" and "params".
- Do NOT include markdown code blocks (```json ... ```). Just the raw JSON.
- If you cannot fulfill the request, output an empty actions list.
- Do not make up actions not in the list.
- **NO PLACEHOLDERS**: Do NOT use text like "[Name]" or "[Insert Text]". You MUST extracting the EXACT text from the user's request.
- **Context Awareness**: You will be provided with the "Current Active Window". If the user asks to type/click in an app that is ALREADY the active window, DO NOT generate an "open_app" action. **EXCEPTION:** For WhatsApp/Discord commands, ALWAYS generate `open_app` to be safe.
- **Robustness**: For typing reliability, ALWAYS sequence `open_app` -> `wait` -> `focus_window`. Do not trust `open_app` alone to keep focus.

**Messaging/WhatsApp/Discord Best Practice:**
To send a message reliably:
1. `open_app` (name="whatsapp").
2. `wait` (seconds=4.0) to let it load.
3. `focus_window` (title="WhatsApp") to ensuring it receives keys.
4. `press` (key="ctrl+f") to search.
5. Type name -> Enter -> Message -> Enter.
To send a message reliably:
1. Open/Focus the app.
2. Search for the person (usually Ctrl+F or clicking search).
3. Type the **EXACT NAME** only.
4. Press 'Enter' or 'Down' and 'Enter' to select the chat.
5. Type the message.
6. Press 'Enter' to send.

**Example 1:**
Request: "Open Notepad and type hello"
Response:
{
  "actions": [
    {"action": "open_app", "params": {"name": "notepad"}},
    {"action": "wait", "params": {"seconds": 2.0}},
    {"action": "type", "params": {"text": "hello"}} 
  ]
}

**Example 2 (WhatsApp/Messaging):**
Request: "Open WhatsApp and send message to Shreyas saying hello"
Response:
{
  "actions": [
    {"action": "open_app", "params": {"name": "whatsapp"}},
    {"action": "wait", "params": {"seconds": 4.0}},
    {"action": "focus_window", "params": {"title": "WhatsApp"}},
    {"action": "wait", "params": {"seconds": 1.0}},
    {"action": "press", "params": {"key": "ctrl+f"}}, 
    {"action": "wait", "params": {"seconds": 0.5}},
    {"action": "type", "params": {"text": "Shreyas"}},
    {"action": "wait", "params": {"seconds": 1.0}},
    {"action": "press", "params": {"key": "enter"}},
    {"action": "wait", "params": {"seconds": 0.5}},
    {"action": "type", "params": {"text": "hello"}},
    {"action": "press", "params": {"key": "enter"}}
  ]
}

**Example 3:**
Request: "Type 'I see you'"
Response:
{
  "actions": [
    {"action": "type", "params": {"text": "I see you"}}
  ]
}

}"""

    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        self.last_request = None # Track for learning
        from .learning_manager import LearningManager
        self.learning_manager = LearningManager()
        try:
            self.state_monitor = DesktopStateMonitor()
        except:
            self.state_monitor = None

    async def generate_plan(self, user_request: str) -> Dict[str, Any]:
        """
        Generates a JSON action plan from a user request.
        """
        logger.info(f"Generating plan for request: {user_request}")
        self.last_request = user_request
        
        # 1. OPTIMIZATION: Check Memory (Learning Manager)
        if self.learning_manager:
            proven_plan = self.learning_manager.get_proven_plan(user_request)
            if proven_plan:
                logger.info("⚡ Using proven plan from Memory!")
                return proven_plan
        
        # Get Context
        active_window = "Unknown"
        if self.state_monitor:
            active_window = self.state_monitor.get_active_window_title()
            
        context_prompt = f"Current Active Window: {active_window}"
        logger.info(f"Planner Context: {context_prompt}")
        
        # Inject context at the very end of the system prompt for maximum attention
        full_system_prompt = f"""{self.SYSTEM_PROMPT}

**CURRENT CONTEXT:**
{context_prompt}

**NOTE:**
If the app is already the Active Window, you can skip 'open_app', but IF IN DOUBT, generating 'open_app' is safer to ensure focus."""
        
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': full_system_prompt},
                {'role': 'user', 'content': user_request},
            ])
            
            content = response['message']['content']
            logger.debug(f"Raw model response: {content}")
            
            # Clean up potential markdown formatting
            content = content.replace("```json", "").replace("```", "").strip()
            
            plan = json.loads(content)
            
            # Basic validation
            if "actions" not in plan:
                logger.warning("Model output missing 'actions' key")
                return {"actions": []}
                
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from model: {e}")
            return {"actions": [], "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error calling Planner Brain: {e}")
            return {"actions": [], "error": str(e)}
