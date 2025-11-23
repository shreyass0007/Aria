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

    def parse_notion_intent(self, text: str) -> dict:
        """
        Uses OpenAI via LangChain to extract Notion page details.
        Returns a dict with keys: title, content (optional), target (optional).
        """
        if not self.llm:
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
            response = self.llm.invoke(formatted_prompt)
            
            cleaned_text = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)
            return parsed
        except Exception as e:
            print(f"Error parsing Notion intent: {e}")
            return {}

    def summarize_text(self, text: str, max_sentences: int = 5) -> str:
        """
        Summarizes long text into a concise summary.
        Returns a summary with approximately max_sentences sentences.
        """
        if not self.llm:
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
            response = self.llm.invoke(formatted_prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error summarizing text: {e}")
            return f"I encountered an error while summarizing: {e}"

    def extract_notion_page_id(self, text: str) -> dict:
        """
        Extracts Notion page ID or page search query from user's command.
        Returns a dict with either 'page_id' or 'search_query'.
        """
        if not self.llm:
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
            response = self.llm.invoke(formatted_prompt)
            
            cleaned_text = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)
            return parsed
        except Exception as e:
            print(f"Error extracting page ID: {e}")
            return {}
