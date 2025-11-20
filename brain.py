import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AriaBrain:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.chat_session = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Use a model that supports function calling if needed, or just standard chat for now
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.chat_session = self.model.start_chat(history=[])
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
        else:
            print("Warning: GEMINI_API_KEY not found in environment variables. Agentic features will be limited.")

    def ask(self, user_input: str) -> str:
        """
        Send a message to the LLM and get a response.
        If the API is not configured, return a fallback message.
        """
        if not self.model or not self.chat_session:
            return "I'm sorry, but my agentic brain is not connected. Please check your API key."

        try:
            # We can add a system prompt or context here if needed, 
            # but for now let's just send the user input.
            response = self.chat_session.send_message(user_input)
            return response.text
        except Exception as e:
            return f"I encountered an error thinking about that: {e}"

    def is_available(self) -> bool:
        return self.model is not None
