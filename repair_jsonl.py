
import json

input_path = "fine_tuning_dataset.jsonl"
output_path = "fine_tuning_dataset_repaired.jsonl"

print(f"Scanning {input_path}...")
valid_lines = []
bad_line_count = 0

with open(input_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        line = line.strip()
        if not line:
            continue
            
        try:
            json.loads(line)
            valid_lines.append(line)
        except json.JSONDecodeError as e:
            print(f"Error on line {i+1}: {e}")
            bad_line_count += 1

print(f"\nFound {len(valid_lines)} valid lines and {bad_line_count} bad lines.")

if bad_line_count > 0:
    print(f"Writing repaired file to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in valid_lines:
            f.write(line + "\n")
    print("Done.")
else:
    print("File appears valid.")
