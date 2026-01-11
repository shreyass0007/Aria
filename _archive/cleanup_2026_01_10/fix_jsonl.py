
import json

new_data = [
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "remind me to drink water"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_start\", \"confidence\": 0.98, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "start water reminder"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_start\", \"confidence\": 0.99, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "enable water alerts"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_start\", \"confidence\": 0.97, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "stop water reminder"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_stop\", \"confidence\": 0.99, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "disable water alerts"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_stop\", \"confidence\": 0.98, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "don't remind me to drink water anymore"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_stop\", \"confidence\": 0.97, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "remind me to drink water every 30 minutes"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_interval\", \"confidence\": 0.99, \"parameters\": {\"interval\": 30}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "set water reminder interval to 45 mins"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_interval\", \"confidence\": 0.98, \"parameters\": {\"interval\": 45}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "change water alert frequency to 1 hour"}, {"role": "assistant", "content": "{\"intent\": \"water_reminder_interval\", \"confidence\": 0.97, \"parameters\": {\"interval\": 60}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "hey beautiful"}, {"role": "assistant", "content": "{\"intent\": \"general_chat\", \"confidence\": 0.99, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "you are looking cute today"}, {"role": "assistant", "content": "{\"intent\": \"general_chat\", \"confidence\": 0.99, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "who's a good AI?"}, {"role": "assistant", "content": "{\"intent\": \"general_chat\", \"confidence\": 0.98, \"parameters\": {}}"}]},
    {"messages": [{"role": "system", "content": "You are Aria, an AI desktop assistant. Classify user commands into intents and extract parameters."}, {"role": "user", "content": "flirt with me"}, {"role": "assistant", "content": "{\"intent\": \"general_chat\", \"confidence\": 0.99, \"parameters\": {}}"}]}
]

# Append to the clean file
with open("fine_tuning_dataset_repaired.jsonl", "a", encoding="utf-8") as f:
    for entry in new_data:
        f.write(json.dumps(entry) + "\n")

print("Appended successfully.")
