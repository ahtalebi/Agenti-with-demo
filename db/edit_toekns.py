import json
import os

# Path to the tokens.json file
tokens_file = "./tokens.json"

# Create a backup first
if os.path.exists(tokens_file):
    with open(tokens_file, "r") as f:
        os.system(f"cp {tokens_file} {tokens_file}.backup")
    
    # Read the current tokens
    with open(tokens_file, "r") as f:
        tokens = json.load(f)
    
    # Select only the first 3 active tokens (or fewer if there aren't 3)
    active_tokens = [t for t in tokens if t["status"] == "active"]
    if len(active_tokens) > 3:
        active_tokens = active_tokens[:3]
    
    # Write the reduced list back to the file
    with open(tokens_file, "w") as f:
        json.dump(active_tokens, f, indent=2)
    
    print(f"Tokens reduced to {len(active_tokens)} entries.")
    print(f"Backup saved to {tokens_file}.backup")
else:
    print(f"Error: {tokens_file} not found.")
