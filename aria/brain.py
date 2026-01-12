import os
import json
import datetime
import socket
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate


load_dotenv()

class AriaBrain:
    def __init__(self):
        self.api_key = os.getenv("OPEN_AI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.local_model_name = os.getenv("LOCAL_MODEL_NAME", "llama3.2")
        
        # print(f"DEBUG: OpenAI Key found: {bool(self.api_key)}")
        # print(f"DEBUG: Google Key found: {bool(self.google_api_key)}")
        # print(f"DEBUG: Anthropic Key found: {bool(self.anthropic_api_key)}")
        
        # Model instances - Private storage for lazy loading
        self._llm_gpt_5_1 = None
        self._llm_gpt_4o = None
        self._llm_gpt_4o_mini = None
        self._llm_gpt_35_turbo = None
        
        # Claude models
        self._llm_claude_sonnet = None
        self._llm_claude_haiku = None
        self._llm_claude_opus_4_5 = None
        self._llm_claude_opus_4_1 = None
        
        # Gemini
        self._llm_gemini = None

        # Local Ollama
        self._llm_ollama = None
        
        # Active Mode (normal, coder, study, jarvis)
        self.active_mode = "normal"

        # Note: We do NOT initialize models here anymore. They are lazy loaded.
        if not self.api_key:
            print("Warning: OPEN_AI_API_KEY not found.")
        if not self.anthropic_api_key:
             print("Info: ANTHROPIC_API_KEY not found. Claude models will not be available.")
        if not self.google_api_key:
            print("Info: GOOGLE_API_KEY not found. Gemini will not be available.")

    def _is_online(self):
        """Checks for internet connectivity."""
        try:
            # Connect to a public DNS server (Google's 8.8.8.8)
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    # --- Lazy Loading Properties ---

    @property
    def llm_ollama(self):
        if self._llm_ollama is None:
             try:
                try:
                    from langchain_ollama import ChatOllama
                except ImportError:
                    from langchain_community.chat_models import ChatOllama
                    
                # Lower temperature for local model to improve stability and coherence
                self._llm_ollama = ChatOllama(model=self.local_model_name, base_url=self.ollama_base_url, temperature=0.3)
             except Exception as e:
                 print(f"Error init Ollama: {e}")
        return self._llm_ollama


    @property
    def llm_gpt_4o(self):
        if self._llm_gpt_4o is None and self.api_key:
             try:
                from langchain_openai import ChatOpenAI
                self._llm_gpt_4o = ChatOpenAI(model="gpt-4o", api_key=self.api_key, temperature=0.7)
             except Exception as e:
                 print(f"Error init GPT-4o: {e}")
        return self._llm_gpt_4o

    @property
    def llm_gpt_4o_mini(self):
        if self._llm_gpt_4o_mini is None and self.api_key:
             try:
                from langchain_openai import ChatOpenAI
                self._llm_gpt_4o_mini = ChatOpenAI(model="gpt-4o-mini", api_key=self.api_key, temperature=0.7)
             except Exception as e:
                 print(f"Error init GPT-4o-mini: {e}")
        return self._llm_gpt_4o_mini

    @property
    def llm_gpt_35_turbo(self):
        if self._llm_gpt_35_turbo is None and self.api_key:
             try:
                from langchain_openai import ChatOpenAI
                self._llm_gpt_35_turbo = ChatOpenAI(model="gpt-3.5-turbo", api_key=self.api_key, temperature=0.7)
             except Exception as e:
                 print(f"Error init GPT-3.5: {e}")
        return self._llm_gpt_35_turbo

    @property
    def llm_gpt_5_1(self):
        # Fallback logic preserved from original
        return self.llm_gpt_4o

    @property
    def llm_gpt_5(self):
        return self.llm_gpt_4o
        
    @property
    def llm_gpt_5_mini(self):
        return self.llm_gpt_4o_mini

    # Claude Properties
    @property
    def llm_claude_sonnet(self):
        if self._llm_claude_sonnet is None and self.anthropic_api_key:
            try:
                from langchain_anthropic import ChatAnthropic
                self._llm_claude_sonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620", anthropic_api_key=self.anthropic_api_key, temperature=0.7)
            except Exception as e:
                print(f"Error init Claude Sonnet: {e}")
        return self._llm_claude_sonnet

    @property
    def llm_claude_haiku(self):
        if self._llm_claude_haiku is None and self.anthropic_api_key:
            try:
                from langchain_anthropic import ChatAnthropic
                self._llm_claude_haiku = ChatAnthropic(model="claude-3-haiku-20240307", anthropic_api_key=self.anthropic_api_key, temperature=0.7)
            except Exception as e:
                print(f"Error init Claude Haiku: {e}")
        return self._llm_claude_haiku

    @property
    def llm_claude_opus_4_5(self):
        if self._llm_claude_opus_4_5 is None and self.anthropic_api_key:
            try:
                from langchain_anthropic import ChatAnthropic
                self._llm_claude_opus_4_5 = ChatAnthropic(model="claude-3-opus-20240229", anthropic_api_key=self.anthropic_api_key, temperature=0.7)
            except Exception as e:
                print(f"Error init Claude Opus: {e}")
        return self._llm_claude_opus_4_5

    @property
    def llm_claude_opus_4_1(self):
         return self.llm_claude_opus_4_5 if self.llm_claude_opus_4_5 else self.llm_claude_sonnet

    # Gemini
    @property
    def llm_gemini(self):
        if self._llm_gemini is None and self.google_api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self._llm_gemini = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=self.google_api_key, temperature=0.7, convert_system_message_to_human=True)
            except Exception as e:
                print(f"Error init Gemini: {e}")
        return self._llm_gemini

    def get_llm(self, model_name: str = "gpt-4o"):
        """Returns the requested LLM instance with fallback support."""
        
        # 1. Check Internet Connection
        if not self._is_online():
            print("Warning: No internet connection detected. Falling back to Local Ollama.")
            return self.llm_ollama

        # Direct lookup to avoid triggering all properties
        llm = None
        
        # Override default request if it's the generic "gpt-4o" to use "gpt-4o-mini" by default (User Preference)
        if model_name == "gpt-4o":
            model_name = "gpt-4o-mini"

        if model_name == "gpt-4o-mini":
            llm = self.llm_gpt_4o_mini
        elif model_name == "gpt-4o" or model_name == "openai": # Explicit fallback if mini fails or specifically asked (logic below handles exact match)
            llm = self.llm_gpt_4o
        elif model_name == "gpt-3.5-turbo":
            llm = self.llm_gpt_35_turbo
        elif model_name == "claude-sonnet":
            llm = self.llm_claude_sonnet
        elif model_name == "claude-haiku":
            llm = self.llm_claude_haiku
        elif model_name == "claude-opus-4-5":
            llm = self.llm_claude_opus_4_5
        elif model_name == "gemini" or model_name == "gemini-pro":
             llm = self.llm_gemini
        elif model_name == "local" or model_name == "ollama":
             llm = self.llm_ollama
        
        # Dynamic Local Model Support (e.g. llama3.2-vision, qwen2.5-vl)
        elif "vision" in model_name or "llama" in model_name or "qwen" in model_name:
             try:
                from langchain_ollama import ChatOllama
                return ChatOllama(model=model_name, base_url=self.ollama_base_url, temperature=0.3)
             except Exception as e:
                 print(f"Error creating dynamic Ollama model {model_name}: {e}")
        
        if llm:
            return llm

        # Smart Fallback (Try preferred models in order)
        print(f"Model {model_name} not available, attempting fallback...")
        
        fallback_order = [
            self.llm_gpt_4o_mini,  # Default Preferred
            self.llm_gpt_4o,
            self.llm_claude_sonnet,
            self.llm_gemini,
            self.llm_gpt_35_turbo,
            self.llm_ollama # Final fallback
        ]
        
        for candidate in fallback_order:
            if candidate:
                return candidate
        
        return None

    def get_model_name_from_llm(self, llm) -> str:
        """Helper to extract model name from various LLM objects."""
        if not llm:
            return "Unknown"
        
        # Try common attributes
        if hasattr(llm, "model_name"): return llm.model_name # OpenAI, Google
        if hasattr(llm, "model"): return llm.model # Ollama, Anthropic
        
        return str(llm.__class__.__name__)

    def get_fast_llm(self):
        """Returns the fastest available LLM for low-latency tasks (e.g., Intent Classification)."""
        
        if not self._is_online():
             return self.llm_ollama

        # Checks trigger properties individually
        if self.llm_gpt_4o_mini:
            return self.llm_gpt_4o_mini
        if self.llm_gpt_35_turbo:
            return self.llm_gpt_35_turbo
        if self.llm_claude_haiku:
            return self.llm_claude_haiku
        
        # Fallback to standard
        return self.get_llm("gpt-4o")

    def _get_system_prompt(self, model_name: str = "gpt-4o") -> str:
        """Reads the system prompt. Returns a simplified version for local models to prevent hallucination."""
        
        # SPECIALIZED PROMPT FOR LOCAL / SMALL MODELS
        # Small models (like Llama 3.2 3B) often overdo "personality" instructions.
        # We give them a stricter, cleaner prompt.
        if model_name and ("local" in model_name.lower() or "ollama" in model_name.lower() or "llama" in model_name.lower()):
            return """You are Aria, a helpful and precise AI assistant.
            
CORE INSTRUCTIONS:
- You are a friend to the user ("Shreyas"). Be polite, warm, and professional.
- Keep answers CONCISE and to the point.
- Do NOT be "cheeky", "playful", or "witty". Just be helpful.
- Speak naturally but clearly.
- If you don't know something, admit it directly.
- CURRENT CONTEXT: The user is a developer."""

        try:
            # Try to find the file in the current directory or project root
            paths = ["llm_system_prompt.txt", "d:\\CODEING\\PROJECTS\\ARIA\\llm_system_prompt.txt"]
            for path in paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        return f.read()
            return "You are Aria, an advanced AI assistant. You are helpful, friendly, and conversational."
        except Exception as e:
            print(f"Error reading system prompt: {e}")
            return "You are Aria, an advanced AI assistant. You are helpful, friendly, and conversational."

    def set_mode(self, mode: str) -> str:
        """Sets the AI's personality mode."""
        mode = mode.lower()
        if mode in ["coder", "coding", "dev"]:
            self.active_mode = "coder"
            return "Coder Mode activated. Ready to code."
        elif mode in ["study", "learning", "tutor"]:
            self.active_mode = "study"
            return "Study Mode activated. Let's learn."
        elif mode in ["jarvis", "butler"]:
            self.active_mode = "jarvis"
            return "At your service, sir."
        elif mode in ["normal", "default", "reset"]:
            self.active_mode = "normal"
            return "Back to normal mode."
        else:
            return f"Unknown mode: {mode}. Keeping current mode."

    def _get_mode_instruction(self) -> str:
        """Returns the system prompt suffix based on the active mode."""
        if self.active_mode == "coder":
            return "\n\n[MODE: CODER]\nYou are an expert software engineer. Your responses must be:\n1. Technical and precise.\n2. Code-heavy (use markdown).\n3. Concise (minimize fluff).\n4. Focus on best practices and performance."
        elif self.active_mode == "study":
            return "\n\n[MODE: STUDY]\nYou are an expert tutor. Your responses must be:\n1. Educational and explanatory.\n2. Use analogies to explain complex topics.\n3. Verify user understanding.\n4. Encouraging and patient."
        elif self.active_mode == "jarvis":
            return "\n\n[MODE: JARVIS]\nYou are J.A.R.V.I.S. Your responses must be:\n1. Ultra-concise and witty.\n2. Address the user as 'Sir'.\n3. Professional and servant-like.\n4. No emojis."
        return ""

    def ask(self, user_input: str, model_name: str = "gpt-4o", conversation_history: list = None, long_term_context: list = None, search_context: str = None) -> str:
        """
        Passes the user's message to the selected model via LangChain.
        
        Args:
            user_input: The current user message
            model_name: The AI model to use
            conversation_history: Optional list of previous messages
            long_term_context: Optional list of relevant past messages
            search_context: Optional string containing real-time search results
        """
        llm = self.get_llm(model_name)
        
        if not llm:
            return "I'm sorry, but no AI models are available. Please check your API keys or internet connection."

        try:
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            # Build message list with conversation history
            messages = []
            
            # Add system message for context
            system_prompt = self._get_system_prompt(model_name=model_name)
            
            # Inject current date and time
            now = datetime.datetime.now()
            current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            day_of_week = now.strftime("%A")
            system_prompt += f"\n\nCurrent Date and Time: {current_time_str} ({day_of_week})"
            
            # Append mode-specific instruction
            system_prompt += self._get_mode_instruction()
            messages.append(SystemMessage(content=system_prompt))
            
            # Add long-term memory context if provided
            if long_term_context:
                context_str = "Relevant context from past conversations:\n"
                for item in long_term_context:
                    # item is expected to be a dict with 'text', 'timestamp', etc.
                    timestamp = item.get('timestamp', 'Unknown time')
                    text = item.get('text', '')
                    context_str += f"- [{timestamp}] {text}\n"
                
                messages.append(SystemMessage(content=context_str))
            
            # Add search context if provided (Real-time data)
            if search_context:
                search_prompt = f"""
                Here is real-time information from a web search. 
                Use this information to answer the user's question accurately and conversationally.
                If the search results don't answer the question, say so.
                
                {search_context}
                """
                messages.append(SystemMessage(content=search_prompt))
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg.get("content", "")))
            
            # Add current user message
            messages.append(HumanMessage(content=user_input))
            
            # Invoke the model with message history
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I encountered an error thinking about that with {model_name}: {e}"

    def ask_vision(self, user_input: str, image_base64: str, model_name: str = "local-vision") -> str:
        """
        Asks the AI to analyze an image (Base64).
        Prioritizes Local VLM (Llama 3.2 Vision / Moondream).
        """
        # Determine model
        llm = self.llm_ollama # Default to local
        if model_name != "local-vision":
             llm = self.get_llm(model_name)
        
        if not llm:
            return "Vision model not available."

        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = []
            
            # System prompt for vision
            messages.append(SystemMessage(content="You are an AI vision assistant. Analyze the provided image and answer the user's question clearly."))
            
            # Multimodal Human Message
            # LangChain standard format for images
            messages.append(HumanMessage(content=[
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]))
            
            # invoke
            response = llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Vision error: {e}")
            return f"I couldn't look at that: {e}"

    def stream_ask(self, user_input: str, model_name: str = "gpt-4o", conversation_history: list = None, long_term_context: list = None, search_context: str = None):
        """
        Streams the response from the selected model.
        Yields chunks of text as they are generated.
        
        Args:
            user_input: The current user message
            model_name: The AI model to use
            conversation_history: Optional list of previous messages in format:
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            long_term_context: Optional list of relevant past messages from other conversations
            search_context: Optional string containing real-time search results
        """

        llm = self.get_llm(model_name)
        
        if not llm:
            yield "I'm sorry, but no AI models are available."
            return

        try:
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            # Build message list with conversation history
            messages = []
            
            # Add system message for context
            system_prompt = self._get_system_prompt(model_name=model_name)
            
            # Inject current date and time
            now = datetime.datetime.now()
            current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            day_of_week = now.strftime("%A")
            system_prompt += f"\n\nCurrent Date and Time: {current_time_str} ({day_of_week})"
            
            # Append mode-specific instruction
            system_prompt += self._get_mode_instruction()
            messages.append(SystemMessage(content=system_prompt))
            
            # Add long-term memory context if provided
            if long_term_context:
                context_str = "Relevant context from past conversations:\n"
                for item in long_term_context:
                    # item is expected to be a dict with 'text', 'timestamp', etc.
                    timestamp = item.get('timestamp', 'Unknown time')
                    text = item.get('text', '')
                    context_str += f"- [{timestamp}] {text}\n"
                messages.append(SystemMessage(content=context_str))
            
            # Add search context if provided (Real-time data)
            if search_context:
                search_prompt = f"""
                Here is real-time information from a web search. 
                Use this information to answer the user's question accurately and conversationally.
                If the search results don't answer the question, say so.
                
                {search_context}
                """
                messages.append(SystemMessage(content=search_prompt))
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg.get("content", "")))
            
            # Add current user message
            messages.append(HumanMessage(content=user_input))
            
            # Stream the response with runtime fallback
            fallback_attempted = False
            active_llm = llm
            active_model_name = model_name
            
            while True:
                try:
                    for chunk in active_llm.stream(messages):
                        yield chunk.content
                    break # Success, exit loop
                except Exception as e:
                    if fallback_attempted:
                        yield f"I encountered an error thinking about that with {active_model_name}: {e}"
                        return
                    
                    print(f"\n⚠️ Runtime Error with {active_model_name}: {e}")
                    print(f"🔄 Switching to Fallback: gpt-4o-mini\n")
                    
                    fallback_attempted = True
                    active_model_name = "gpt-4o-mini"
                    active_llm = self.get_llm("gpt-4o-mini")
                    
                    if not active_llm:
                        yield f"Fallback model not available."
                        return
        except Exception as e:
            yield f"I encountered an error preparing the request: {e}"

    def is_available(self) -> bool:
        """Check if at least one AI model is available."""
        # If offline, check if Ollama is responsive
        if not self._is_online():
            return self.llm_ollama is not None

        return any([
            self.llm_gpt_5_1,
            self.llm_gpt_4o,
            self.llm_gpt_4o_mini,
            self.llm_gpt_35_turbo,
            self.llm_claude_sonnet,
            self.llm_claude_haiku,
            self.llm_claude_opus_4_5,
            self.llm_claude_opus_4_1,
            self.llm_gemini,
            self.llm_ollama
        ])
    
    def get_available_models(self) -> list:
        """Returns a list of available model names."""
        available = []
        
        # Ollama / Local
        if self.llm_ollama:
             available.append({"id": "local", "name": f"Local ({self.local_model_name})", "provider": "Ollama"})

        if self.llm_gpt_5_1:
            available.append({"id": "gpt-5.1", "name": "GPT-5.1", "provider": "OpenAI"})
        
        if self.llm_gpt_4o:
            available.append({"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI"})
            
        if self.llm_gpt_4o_mini:
            available.append({"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI"})
            
        if self.llm_gpt_35_turbo:
            available.append({"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "OpenAI"})

        # Claude Models
        if self.llm_claude_sonnet:
            available.append({"id": "claude-sonnet", "name": "Claude 3.5 Sonnet", "provider": "Anthropic"})
            
        if self.llm_claude_haiku:
            available.append({"id": "claude-haiku", "name": "Claude 3 Haiku", "provider": "Anthropic"})
            
        if self.llm_claude_opus_4_5:
            available.append({"id": "claude-opus-4-5", "name": "Claude 3 Opus", "provider": "Anthropic"})
            
        if self.llm_claude_opus_4_1:
            available.append({"id": "claude-opus-4-1", "name": "Claude Opus 4.1", "provider": "Anthropic"})
        
        if self.llm_gemini:
            available.append({"id": "gemini-pro", "name": "Gemini Pro", "provider": "Google"})
        
        return available

    def parse_calendar_intent(self, text: str) -> dict:
        """
        Uses OpenAI (default) to extract event details. 
        For structured tasks, we prefer OpenAI for reliability, but could switch if needed.
        """
        llm = self.get_llm("gpt-4o")
        
        if not llm:
            return {}

        # Get current time for context (Explicitly mention IST)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        day_of_week = datetime.datetime.now().strftime("%A")
        
        template = """
        You are a calendar assistant. Extract the event details from the user's request.
        The current time is {now} ({day_of_week}). Assume the user is in Indian Standard Time (IST).
        If the user says "tomorrow", calculate the date based on the current time provided above.
        
        User Request: "{text}"
        
        Return ONLY a JSON object with the following fields:
        - summary: A short title for the event.
        - start_time: The start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS) in local IST. DO NOT convert to UTC.
        - end_time: The end time in ISO 8601 format in local IST. If the user specifies a duration (e.g., "for 2 hours", "for 30 minutes"), calculate the end_time as start_time + duration. If not specified, leave it null.
        
        Example JSON:
        {{
            "summary": "Meeting with John",
            "start_time": "2023-10-27T15:00:00",
            "end_time": "2023-10-27T16:00:00"
        }}
        """
        
        prompt = PromptTemplate(
            input_variables=["now", "day_of_week", "text"],
            template=template
        )
        
        try:
            # Create the prompt and invoke the model
            formatted_prompt = prompt.format(now=now, day_of_week=day_of_week, text=text)
            response = llm.invoke(formatted_prompt)
            # print(f"DEBUG: Raw response: {response.content}")
            
            # Clean up code blocks if present
            cleaned_text = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)
            # print(f"DEBUG: Parsed JSON: {parsed}")
            return parsed
        except Exception as e:
            print(f"Error parsing calendar intent: {e}")
            return {}

    def parse_notion_intent(self, text: str) -> dict:
        """
        Uses OpenAI (or fallback) to extract Notion page details.
        """
        llm = self.get_llm("gpt-4o")
        if not llm:
            return {}

        template = """
        You are a personal assistant. Extract the task or note details from the user's request for Notion.
        
        User Request: "{text}"
        
        Return ONLY a JSON object with the following fields:
        - title: The main title of the task or note.
        - content: Any additional details or body text. If none, leave empty string.
        - target: The name of the specific page or database to add this to (e.g. "Grocery List", "Work Tasks"). If not specified, leave null.
        
        Example JSON:
        {{
            "title": "Buy groceries",
            "content": "Milk, eggs, bread",
            "target": "Grocery List"
        }}
        """
        
        prompt = PromptTemplate(
            input_variables=["text"],
            template=template
        )
        
        try:
            formatted_prompt = prompt.format(text=text)
            response = llm.invoke(formatted_prompt)
            
            cleaned_text = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)
            return parsed
        except Exception as e:
            print(f"Error parsing Notion intent: {e}")
            return {}

    def summarize_text(self, text: str, max_sentences: int = 5) -> str:
        """
        Summarizes long text into a concise summary.
        """
        llm = self.get_llm("gpt-4o")
        if not llm:
            return "I'm sorry, but my summarization capability is not available right now."

        # Handle edge cases
        if not text or len(text.strip()) < 50:
            return "The content is too short to summarize meaningfully."

        template = """
        You are a helpful assistant that creates concise, informative summaries.
        
        Please summarize the following text in approximately {max_sentences} sentences.
        Focus on the main points and key information.
        Be clear and concise.
        
        Text to summarize:
        {text}
        
        Summary:
        """
        
        prompt = PromptTemplate(
            input_variables=["text", "max_sentences"],
            template=template
        )
        
        try:
            formatted_prompt = prompt.format(text=text, max_sentences=max_sentences)
            response = llm.invoke(formatted_prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error summarizing text: {e}")
            return f"I encountered an error while summarizing: {e}"

    def extract_notion_page_id(self, text: str) -> dict:
        """
        Extracts Notion page ID or page search query.
        """
        llm = self.get_llm("gpt-4o")
        if not llm:
            return {}

        template = """
        You are a helpful assistant that extracts Notion page identifiers from user commands.
        
        User Command: "{text}"
        
        Analyze the command and extract:
        1. If there's a Notion URL (like https://notion.so/abc123 or notion.so/workspace/page-abc123), extract the page ID (the 32-character hex string at the end).
        2. If there's no URL but a page title or topic is mentioned, extract it as a search query.
        
        Return ONLY a JSON object with ONE of these fields:
        - page_id: The 32-character page ID (if URL found)
        - search_query: The page title or topic to search for (if no URL)
        
        Examples:
        Command: "summarize notion page https://notion.so/My-Page-abc123def456"
        Response: {{"page_id": "abc123def456"}}
        
        Command: "summarize my notion page about project planning"
        Response: {{"search_query": "project planning"}}
        
        Command: "summarize the grocery list page"
        Response: {{"search_query": "grocery list"}}
        """
        
        prompt = PromptTemplate(
            input_variables=["text"],
            template=template
        )
        
        try:
            formatted_prompt = prompt.format(text=text)
            response = llm.invoke(formatted_prompt)
            
            cleaned_text = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)
            return parsed
        except Exception as e:
            print(f"Error extracting page ID: {e}")
            return {}

    def parse_email_intent(self, text: str) -> dict:
        """
        Extracts email details.
        """
        llm = self.get_llm("gpt-4o")
        if not llm:
            return {}

        template = """
        You are a helpful assistant. Extract the email details from the user's request.
        
        User Request: "{text}"
        
        Return ONLY a JSON object with the following fields:
        - to: The recipient's email address. If a name is given (e.g., "John"), try to infer or leave it as the name if no email is found.
        - subject: A short subject line for the email. If the user does not specify a subject, GENERATE a relevant one based on the body content. Do NOT leave this empty.
        - body: The main content of the email.
        
        Example JSON:
        {{
            "to": "john@example.com",
            "subject": "Meeting Reminder",
            "body": "Hi John, just a reminder about our meeting tomorrow."
        }}
        """
        
        prompt = PromptTemplate(
            input_variables=["text"],
            template=template
        )
        
        try:
            formatted_prompt = prompt.format(text=text)
            response = llm.invoke(formatted_prompt)
            
            cleaned_text = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)
            return parsed
        except Exception as e:
            print(f"Error parsing email intent: {e}")
            return {}

    def generate_email_draft(self, to: str, subject: str, context: str, sender_name: str = "User") -> str:
        """
        Generates a polite email draft.
        """
        llm = self.get_llm("gpt-4o")
        if not llm:
            return context

        template = """
        You are a professional email assistant. Write a polished, well-formatted email.
        
        Recipient: {to}
        Subject: {subject}
        Context/Message: "{context}"
        Sender Name: {sender_name}
        
        Write ONLY the email body with the following structure:
        1. Start with an appropriate greeting (e.g., "Hi [name]," or "Dear [name],")
        2. Write the main message in clear paragraphs (use double line breaks between paragraphs)
        3. End with a professional sign-off using the sender name
        
        Keep it concise, professional, and warm. Do NOT include the subject line.
        """
        
        prompt = PromptTemplate(
            input_variables=["to", "subject", "context", "sender_name"],
            template=template
        )
        
        try:
            formatted_prompt = prompt.format(to=to, subject=subject, context=context, sender_name=sender_name)
            response = llm.invoke(formatted_prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating draft: {e}")
            return context
    def analyze_image(self, image_data, prompt: str = "Describe what is on this screen.") -> str:
        """
        Analyzes an image using a Multimodal LLM (Gemini or GPT-4o).
        image_data: PIL Image or bytes.
        """
        import base64
        from io import BytesIO
        from langchain_core.messages import HumanMessage
        
        # Convert PIL to base64
        if hasattr(image_data, 'save'):
            buffered = BytesIO()
            image_data.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        else:
            # Assume it's already bytes or b64?
            img_str = image_data
            
        # Prioritize Gemini for Vision (Fast/Good)
        llm = self.llm_gemini
        model_type = "gemini"
        
        if not llm:
            llm = self.llm_gpt_4o
            model_type = "gpt-4o"
            
        if not llm:
            return "I'm sorry, I don't have a vision-capable AI model available right now (Gemini or GPT-4o required)."
            
        try:
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_str}"},
                    },
                ]
            )
            
            response = llm.invoke([message])
            return response.content
        except Exception as e:
            return f"I encountered an error looking at that image: {e}"
        except Exception as e:
            return f"I encountered an error looking at that image: {e}"

    def generate_briefing_summary(self, weather_info: str, calendar_events: list, email_count: int, user_name: str = "Shreyas", mode: str = "morning briefing") -> str:
        """
        Generates a radio-host style briefing.
        """
        llm = self.get_llm("gpt-4o")
        if not llm:
            return f"Here is your data: {weather_info}. You have {len(calendar_events)} events and {email_count} unread emails."

        # Format calendar events for the prompt
        events_str = "No events scheduled."
        if calendar_events:
            events_str = "\n".join([str(e) for e in calendar_events])

        template = """
        You are Aria, an energetic and professional AI assistant giving a {mode}.
        
        User: {user_name}
        Current Weather: {weather_info}
        Calendar Events:
        {events_str}
        Unread Emails: {email_count}
        
        Task: Generate a concise, engaging, 30-second script.
        - Start with a warm greeting appropriate for the time of day.
        - Summarize the weather.
        - Highlight the most important events, specifically looking for keywords like 'Meeting', 'Exam', 'Call', 'Zoom', or 'Interview'.
        - Mention the unread email count.
        - End with a motivating closing.
        - Do NOT use markdown or bullet points. Write it as a spoken paragraph.
        """
        
        prompt = PromptTemplate(
            input_variables=["mode", "user_name", "weather_info", "events_str", "email_count"],
            template=template
        )
        
        try:
            formatted_prompt = prompt.format(
                mode=mode,
                user_name=user_name,
                weather_info=weather_info,
                events_str=events_str,
                email_count=email_count
            )
            response = llm.invoke(formatted_prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating briefing summary: {e}")
            return f"I couldn't generate the full briefing, but here is what I know: {weather_info}. You have {len(calendar_events)} events."
