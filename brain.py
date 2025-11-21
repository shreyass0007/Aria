import os
import json
import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

class AriaBrain:
    def __init__(self):
        self.api_key = os.getenv("OPEN_AI_API_KEY")
        print(f"DEBUG: API Key found: {bool(self.api_key)}, Length: {len(self.api_key) if self.api_key else 0}")
        self.llm = None
        
        if self.api_key:
            try:
                # Ensure clean key
                self.api_key = self.api_key.strip()
                
                # Initialize LangChain's ChatOpenAI
                self.llm = ChatOpenAI(
                    model="gpt-4o",
                    api_key=self.api_key,
                    temperature=0.7
                )
            except Exception as e:
                print(f"Error initializing OpenAI via LangChain: {e}")
        else:
            print("Warning: OPEN_AI_API_KEY not found in environment variables. Agentic features will be limited.")

    def ask(self, user_input: str) -> str:
        """
        Passes the user's message to OpenAI via LangChain and returns the response.
        """
        if not self.llm:
            return "I'm sorry, but my agentic brain is not connected. Please check your API key."

        try:
            # Invoke the model directly
            response = self.llm.invoke(user_input)
            return response.content
        except Exception as e:
            return f"I encountered an error thinking about that: {e}"

    def is_available(self) -> bool:
        return self.llm is not None

    def parse_calendar_intent(self, text: str) -> dict:
        """
        Uses OpenAI via LangChain to extract event details from natural language.
        Returns a dict with keys: summary, start_time, end_time (optional).
        """
        if not self.llm:
            return {}

        # Get current time for context
        now = datetime.datetime.now().isoformat()
        
        template = """
        You are a calendar assistant. Extract the event details from the user's request.
        The current time is {now}.
        
        User Request: "{text}"
        
        Return ONLY a JSON object with the following fields:
        - summary: A short title for the event.
        - start_time: The start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS). Calculate relative dates (e.g. "tomorrow", "next friday") based on the current time.
        - end_time: The end time in ISO 8601 format. If not specified, leave it null or omit it.
        
        Example JSON:
        {{
            "summary": "Meeting with John",
            "start_time": "2023-10-27T15:00:00",
            "end_time": "2023-10-27T16:00:00"
        }}
        """
        
        prompt = PromptTemplate(
            input_variables=["now", "text"],
            template=template
        )
        
        try:
            # Create the prompt and invoke the model
            formatted_prompt = prompt.format(now=now, text=text)
            response = self.llm.invoke(formatted_prompt)
            print(f"DEBUG: Raw OpenAI response: {response.content}")
            
            # Clean up code blocks if present
            cleaned_text = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)
            print(f"DEBUG: Parsed JSON: {parsed}")
            return parsed
        except Exception as e:
            print(f"Error parsing calendar intent: {e}")
            return {}
