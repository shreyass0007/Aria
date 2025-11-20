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
                # We're using the flash model for speed, but we can swap this out later.
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.chat_session = self.model.start_chat(history=[])
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
        else:
            print("Warning: GEMINI_API_KEY not found in environment variables. Agentic features will be limited.")

    def ask(self, user_input: str) -> str:
        """
        Passes the user's message to Gemini and returns the response.
        Handles the case where the API isn't set up yet.
        """
        if not self.model or not self.chat_session:
            return "I'm sorry, but my agentic brain is not connected. Please check your API key."

        try:
            # Send the message to the chat session
            response = self.chat_session.send_message(user_input)
            return response.text
        except Exception as e:
            return f"I encountered an error thinking about that: {e}"

    def is_available(self) -> bool:
        return self.model is not None
