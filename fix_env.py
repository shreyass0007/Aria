import os

env_path = ".env"
key = "PICOVOICE_ACCESS_KEY=QJPFnEcErSt2waY2xStdxas8TtTN9tcDuVjCgYLpyuTTXJYovwZyRw=="

# Read existing lines
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        lines = f.readlines()
else:
    lines = []

# Remove any existing PICOVOICE_ACCESS_KEY lines to avoid duplicates
lines = [line for line in lines if "PICOVOICE_ACCESS_KEY" not in line]

# Ensure last line has newline
if lines and not lines[-1].endswith("\n"):
    lines[-1] += "\n"

# Append key
lines.append(key + "\n")

# Write back
with open(env_path, "w") as f:
    f.writelines(lines)

print("Fixed .env file.")
