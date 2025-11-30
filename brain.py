import os
import json
import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate

load_dotenv()

class AriaBrain:
    def __init__(self):
        self.api_key = os.getenv("OPEN_AI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # print(f"DEBUG: OpenAI Key found: {bool(self.api_key)}")
        # print(f"DEBUG: Google Key found: {bool(self.google_api_key)}")
        # print(f"DEBUG: Anthropic Key found: {bool(self.anthropic_api_key)}")
        
        # Model instances - OpenAI variants
        self.llm_gpt_5_1 = None
        self.llm_gpt_4o = None
        self.llm_gpt_4o_mini = None
        self.llm_gpt_35_turbo = None
        
        # Claude models
        self.llm_claude_sonnet = None
        self.llm_claude_haiku = None
        self.llm_claude_opus_4_5 = None
        self.llm_claude_opus_4_1 = None
        
        # Gemini
        self.llm_gemini = None
        
        # Initialize OpenAI models
        if self.api_key:
            try:
                # GPT-5.1 (future-proof)
                try:
                    self.llm_gpt_5_1 = ChatOpenAI(
                        model="gpt-5.1",
                        api_key=self.api_key,
                        temperature=0.7
                    )
                except Exception as e:
                    print(f"GPT-5.1 not yet available: {e}")
                
                # GPT-4o (default)
                self.llm_gpt_4o = ChatOpenAI(
                    model="gpt-4o",
                    api_key=self.api_key,
                    temperature=0.7
                )
                
                # GPT-4o-mini
                self.llm_gpt_4o_mini = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=self.api_key,
                    temperature=0.7
                )
                
                # GPT-3.5-turbo
                self.llm_gpt_35_turbo = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    api_key=self.api_key,
                    temperature=0.7
                )
            except Exception as e:
                print(f"Error initializing OpenAI models: {e}")
        else:
            print("Warning: OPEN_AI_API_KEY not found.")

        # Initialize Claude models
        if self.anthropic_api_key:
            try:
                # Claude 3.5 Sonnet (balanced)
                self.llm_claude_sonnet = ChatAnthropic(
                    model="claude-sonnet-4-5-20250929",
                    anthropic_api_key=self.anthropic_api_key,
                    temperature=0.7
                )
                
                # Claude Haiku 4.5 (fast)
                self.llm_claude_haiku = ChatAnthropic(
                    model="claude-haiku-4-5-20250929",
                    anthropic_api_key=self.anthropic_api_key,
                    temperature=0.7
                )
                
                # Claude Opus 4.5 (most capable)
                self.llm_claude_opus_4_5 = ChatAnthropic(
                    model="claude-opus-4-5-20250929",
                    anthropic_api_key=self.anthropic_api_key,
                    temperature=0.7
                )

                # Claude Opus 4.1
                self.llm_claude_opus_4_1 = ChatAnthropic(
                    model="claude-opus-4-1-20250620",
                    anthropic_api_key=self.anthropic_api_key,
                    temperature=0.7
                )
            except Exception as e:
                print(f"Error initializing Claude models: {e}")
        else:
            print("Info: ANTHROPIC_API_KEY not found. Claude models will not be available.")

        # Initialize Gemini
        if self.google_api_key:
            try:
                self.llm_gemini = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.google_api_key,
                    temperature=0.7,
                    convert_system_message_to_human=True
                )
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
        else:
            print("Info: GOOGLE_API_KEY not found. Gemini will not be available.")

    def get_llm(self, model_name: str = "gpt-4o"):
        """Returns the requested LLM instance with fallback support."""
        # Model mapping
        model_map = {
            "gpt-5.1": self.llm_gpt_5_1,
            "gpt-4o": self.llm_gpt_4o,
            "gpt-4o-mini": self.llm_gpt_4o_mini,
            "gpt-3.5-turbo": self.llm_gpt_35_turbo,
            "claude-sonnet": self.llm_claude_sonnet,
            "claude-haiku": self.llm_claude_haiku,
            "claude-opus-4-5": self.llm_claude_opus_4_5,
            "claude-opus-4-1": self.llm_claude_opus_4_1,
            "gemini-pro": self.llm_gemini,
            # Legacy aliases for backward compatibility
            "openai": self.llm_gpt_4o,
            "gemini": self.llm_gemini,
        }
        
        # Get requested model
        llm = model_map.get(model_name)
        
        # If requested model not available, fallback to first available
        if not llm:
            print(f"Model {model_name} not available, using fallback")
            for fallback_llm in model_map.values():
                if fallback_llm:
                    return fallback_llm
        
        return llm

    def _get_system_prompt(self) -> str:
        """Reads the system prompt from the file or returns a default."""
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

    def ask(self, user_input: str, model_name: str = "gpt-4o", conversation_history: list = None, long_term_context: list = None) -> str:
        """
        Passes the user's message to the selected model via LangChain.
        
        Args:
            user_input: The current user message
            model_name: The AI model to use
            conversation_history: Optional list of previous messages in format:
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            long_term_context: Optional list of relevant past messages from other conversations
        """
        llm = self.get_llm(model_name)
        
        if not llm:
            return "I'm sorry, but no AI models are available. Please check your API keys."

        try:
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            # Build message list with conversation history
            messages = []
            
            # Add system message for context
            system_prompt = self._get_system_prompt()
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

    def stream_ask(self, user_input: str, model_name: str = "gpt-4o", conversation_history: list = None, long_term_context: list = None):
        """
        Streams the response from the selected model.
        Yields chunks of text as they are generated.
        
        Args:
            user_input: The current user message
            model_name: The AI model to use
            conversation_history: Optional list of previous messages in format:
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            long_term_context: Optional list of relevant past messages from other conversations
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
            system_prompt = self._get_system_prompt()
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
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg.get("content", "")))
            
            # Add current user message
            messages.append(HumanMessage(content=user_input))
            
            # Stream the response with message history
            for chunk in llm.stream(messages):
                yield chunk.content
        except Exception as e:
            yield f"I encountered an error thinking about that with {model_name}: {e}"

    def is_available(self) -> bool:
        """Check if at least one AI model is available."""
        return any([
            self.llm_gpt_5_1,
            self.llm_gpt_4o,
            self.llm_gpt_4o_mini,
            self.llm_gpt_35_turbo,
            self.llm_claude_sonnet,
            self.llm_claude_haiku,
            self.llm_claude_opus_4_5,
            self.llm_claude_opus_4_1,
            self.llm_gemini
        ])
    
    def get_available_models(self) -> list:
        """Returns a list of available model names."""
        available = []
        
        if self.llm_gpt_5_1:
            available.append({"id": "gpt-5.1", "name": "GPT-5.1", "provider": "OpenAI"})
        if self.llm_gpt_4o:
            available.append({"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI"})
        if self.llm_gpt_4o_mini:
            available.append({"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI"})
        if self.llm_gpt_35_turbo:
            available.append({"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "OpenAI"})
        if self.llm_claude_sonnet:
            available.append({"id": "claude-sonnet", "name": "Claude Sonnet 4.5", "provider": "Anthropic"})
        if self.llm_claude_haiku:
            available.append({"id": "claude-haiku", "name": "Claude Haiku 4.5", "provider": "Anthropic"})
        if self.llm_claude_opus_4_5:
            available.append({"id": "claude-opus-4-5", "name": "Claude Opus 4.5", "provider": "Anthropic"})
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
        - subject: A short subject line for the email.
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
