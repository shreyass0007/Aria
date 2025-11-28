"""
Fine-Tuning Dataset Generator for ARIA
Programmatically generates additional training examples for model fine-tuning
"""

import json
import random
from typing import List, Dict


class TrainingDataGenerator:
    """Generate training examples for ARIA command classification"""
    
    def __init__(self):
        self.intents = {
            "shutdown": ["shutdown", "turn off", "power off", "shut down"],
            "restart": ["restart", "reboot"],
            "lock": ["lock", "lock screen"],
            "sleep": ["sleep", "put to sleep", "enter sleep mode"],
            "volume_set": ["set volume to {level}", "volume {level}", "change volume to {level}"],
            "volume_up": ["increase volume", "turn up volume", "louder", "volume up"],
            "volume_down": ["decrease volume", "turn down volume", "quieter", "volume down"],
            "volume_mute": ["mute", "mute system", "silence audio"],
            "volume_unmute": ["unmute", "unmute system", "restore audio"],
            "file_create": ["create file {filename}", "create {filename} on {location}", "make file {filename}"],
            "file_read": ["read {filename}", "show {filename}", "open {filename}"],
            "file_search": ["find {pattern} in {location}", "search for {pattern}", "search {location} for {pattern}"],
            "web_search": ["search for {query}", "google {query}", "look up {query}"],
            "app_open": ["open {app}", "launch {app}", "start {app}"],
            "web_open": ["open {site}", "go to {site}"],
            "screenshot_take": ["take screenshot", "capture screen", "screenshot"],
            "battery_check": ["check battery", "battery status", "battery level"],
            "cpu_check": ["check CPU", "CPU usage", "processor usage"],
            "ram_check": ["check RAM", "memory usage", "check memory"],
            "weather_check": ["weather in {city}", "check weather in {city}", "what's the weather in {city}"]
        }
        
        self.locations = ["desktop", "downloads", "documents", "pictures", "music"]
        self.filenames = ["notes.txt", "report.pdf", "test.py", "data.csv", "image.png"]
        self.apps = ["Chrome", "VS Code", "Calculator", "Spotify", "Notion"]
        self.sites = ["YouTube", "Gmail", "GitHub", "Instagram", "LinkedIn"]
        self.cities = ["London", "New York", "Tokyo", "Paris", "Sydney"]
        self.patterns = ["*.pdf", "*.txt", "image*", "report*"]
        self.queries = ["Python tutorials", "best restaurants", "AI news", "how to code"]
    
    def generate_examples(self, intent: str, count: int = 10) -> List[Dict]:
        """Generate training examples for a specific intent"""
        examples = []
        patterns = self.intents.get(intent, [])
        
        for _ in range(count):
            pattern = random.choice(patterns)
            
            # Replace placeholders
            text = pattern
            params = {}
            
            if "{level}" in text:
                level = random.choice([10, 25, 50, 75, 100])
                text = text.replace("{level}", str(level))
                params["level"] = level
            
            if "{filename}" in text:
                filename = random.choice(self.filenames)
                text = text.replace("{filename}", filename)
                params["filename"] = filename
            
            if "{location}" in text:
                location = random.choice(self.locations)
                text = text.replace("{location}", location)
                params["location"] = location
            
            if "{pattern}" in text:
                pattern = random.choice(self.patterns)
                text = text.replace("{pattern}", pattern)
                params["pattern"] = pattern
            
            if "{app}" in text:
                app = random.choice(self.apps)
                text = text.replace("{app}", app)
                params["app_name"] = app
            
            if "{site}" in text:
                site = random.choice(self.sites)
                text = text.replace("{site}", site)
                params["url"] = f"https://{site.lower()}.com"
                params["name"] = site
            
            if "{city}" in text:
                city = random.choice(self.cities)
                text = text.replace("{city}", city)
                params["city"] = city
            
            if "{query}" in text:
                query = random.choice(self.queries)
                text = text.replace("{query}", query)
                params["query"] = query
            
            examples.append({
                "messages": [
                    {
                        "role": "system",
                        "content": "You are ARIA, an AI desktop assistant. Classify user commands into intents and extract parameters."
                    },
                    {
                        "role": "user",
                        "content": text
                    },
                    {
                        "role": "assistant",
                        "content": json.dumps({
                            "intent": intent,
                            "confidence": round(random.uniform(0.95, 0.99), 2),
                            "parameters": params
                        })
                    }
                ]
            })
        
        return examples
    
    def generate_full_dataset(self, output_file: str = "generated_fine_tuning_data.jsonl"):
        """Generate a complete fine-tuning dataset"""
        all_examples = []
        
        for intent in self.intents.keys():
            examples = self.generate_examples(intent, count=5)
            all_examples.extend(examples)
        
        # Write to JSONL file
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in all_examples:
                f.write(json.dumps(example) + '\n')
        
        print(f"Generated {len(all_examples)} training examples")
        print(f"Saved to: {output_file}")
        
        return len(all_examples)


def main():
    """Generate fine-tuning dataset"""
    generator = TrainingDataGenerator()
    count = generator.generate_full_dataset()
    print(f"\n✓ Successfully generated {count} fine-tuning examples")
    print("\nTo use this dataset:")
    print("1. Combine with fine_tuning_dataset.jsonl")
    print("2. Upload to OpenAI for fine-tuning")
    print("3. Use: openai api fine_tunes.create -t generated_fine_tuning_data.jsonl -m gpt-3.5-turbo")


if __name__ == "__main__":
    main()
