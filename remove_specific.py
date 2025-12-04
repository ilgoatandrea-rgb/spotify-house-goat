import json

STATE_FILE = 'playlist_state.json'

def load_state():
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

state = load_state()
initial_count = len(state['artists'])

# Remove I$RÆL DIE! by ID
target_id = "3aBjZNBDJj8iMRbVGY9aVw"
state['artists'] = [a for a in state['artists'] if a['id'] != target_id]

if len(state['artists']) < initial_count:
    print("Removed I$RÆL DIE!")
    save_state(state)
else:
    print("I$RÆL DIE! not found (by ID).")

# List all artists to file for searching
with open('all_artists.txt', 'w', encoding='utf-8') as f:
    for a in state['artists']:
        f.write(f"{a['name']} ({a['id']})\n")
print("Dumped all artists to all_artists.txt")
