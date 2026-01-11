"""
Fine-Tuning Dataset Generator for ARIA
Programmatically generates additional training examples for model fine-tuning
using llm_training_dataset.json as the source of truth.
"""

import json
import random
import os
from typing import List, Dict, Any

class TrainingDataGenerator:
    """Generate training examples for ARIA command classification"""
    
    def __init__(self, dataset_path: str = "llm_training_dataset.json"):
        self.dataset_path = dataset_path
        self.data = self._load_dataset()
        
        # Dynamic templates for generating variations
        self.templates = {
            "email_send": [
                "send email to {recipient} about {subject}",
                "email {recipient} regarding {subject}",
                "compose an email to {recipient} with subject {subject}",
                "send a message to {recipient} about {subject}"
            ],
            "calendar_create": [
                "schedule {event} {time}",
                "create a meeting for {event} {time}",
                "add {event} to my calendar {time}",
                "remind me to {event} {time}"
            ],
            "notion_create": [
                "add {content} to {list} in notion",
                "create a notion page for {content} in {list}",
                "append {content} to my {list} notion page",
                "save {content} to {list}"
            ],
            "weather_check": [
                "what's the weather in {city}",
                "check weather for {city}",
                "weather forecast {city}",
                "how is the weather in {city}"
            ],
            "file_create": [
                "create a file named {filename}",
                "make a new file {filename}",
                "create {filename} in {location}",
                "generate {filename}"
            ]
        }
        
        # Data pools for dynamic generation
        self.pools = {
            "recipient": ["john@example.com", "sarah@work.com", "team@company.com", "boss@office.com", "mom@gmail.com"],
            "subject": ["project update", "meeting notes", "vacation plans", "budget review", "lunch"],
            "event": ["team sync", "doctor appointment", "lunch with client", "project review", "gym session"],
            "time": ["tomorrow at 3 PM", "next Monday at 9 AM", "in 2 hours", "at 5 PM today", "on Friday at 10 AM"],
            "content": ["buy milk", "finish report", "call mom", "update website", "book flights"],
            "list": ["grocery list", "todo list", "ideas", "project notes", "reading list"],
            "city": ["London", "New York", "Tokyo", "Paris", "Berlin", "San Francisco", "Toronto"],
            "filename": ["notes.txt", "report.pdf", "script.py", "data.csv", "image.png", "backup.zip"],
            "location": ["desktop", "downloads", "documents", "pictures", "music"]
        }

    def _load_dataset(self) -> Dict:
        """Load the training dataset from JSON"""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset file not found: {self.dataset_path}")
            
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_message(self, user_input: str, intent: str, parameters: Dict) -> Dict:
        """Create a standard training message format"""
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."
                },
                {
                    "role": "user",
                    "content": user_input
                },
                {
                    "role": "assistant",
                    "content": json.dumps({
                        "intent": intent,
                        "confidence": round(random.uniform(0.95, 0.99), 2),
                        "parameters": parameters
                    })
                }
            ]
        }

    def generate_static_examples(self) -> List[Dict]:
        """Generate examples directly from the JSON dataset"""
        examples = []
        
        for item in self.data.get("training_examples", []):
            intent = item["intent"]
            
            for example in item.get("examples", []):
                # Add the main input
                examples.append(self._create_message(
                    example["input"], 
                    intent, 
                    example.get("parameters", {})
                ))
                
                # Add variations
                for variation in example.get("variations", []):
                    # Note: Variations in the JSON don't always have explicit parameters mapped
                    # We assume they share the same parameters as the main example for now, 
                    # or empty if not specified.
                    examples.append(self._create_message(
                        variation, 
                        intent, 
                        example.get("parameters", {})
                    ))
                    
        return examples

    def generate_dynamic_examples(self, count_per_template: int = 20) -> List[Dict]:
        """Generate synthetic examples using templates"""
        examples = []
        
        for intent, templates in self.templates.items():
            for _ in range(count_per_template):
                template = random.choice(templates)
                text = template
                params = {}
                
                # Replace placeholders and build parameters
                for key, pool in self.pools.items():
                    placeholder = f"{{{key}}}"
                    if placeholder in text:
                        value = random.choice(pool)
                        text = text.replace(placeholder, value)
                        params[key] = value
                
                examples.append(self._create_message(text, intent, params))
                
        return examples

    def generate_full_dataset(self, output_file: str = "fine_tuning_dataset.jsonl"):
        """Generate and save the complete dataset"""
        all_examples = []
        
        # 1. Static examples from JSON
        static_examples = self.generate_static_examples()
        print(f"Loaded {len(static_examples)} static examples from {self.dataset_path}")
        all_examples.extend(static_examples)
        
        # 2. Dynamic examples from templates
        dynamic_examples = self.generate_dynamic_examples()
        print(f"Generated {len(dynamic_examples)} dynamic examples from templates")
        all_examples.extend(dynamic_examples)
        
        # Shuffle the dataset
        random.shuffle(all_examples)
        
        # Write to JSONL
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in all_examples:
                f.write(json.dumps(example) + '\n')
                
        print(f"\nTotal dataset size: {len(all_examples)} examples")
        print(f"Saved to: {output_file}")
        return len(all_examples)

def main():
    generator = TrainingDataGenerator()
    generator.generate_full_dataset()

if __name__ == "__main__":
    main()
