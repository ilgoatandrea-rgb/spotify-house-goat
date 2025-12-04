import json

with open('playlist_state.json', 'r') as f:
    data = json.load(f)

print("Searching for artists...")
for artist in data['artists']:
    name = artist['name'].lower()
    if 'c4' in name or 'h1' in name or 'israel' in name or 'die' in name or 'rael' in name:
        print(f"Found: {artist['name']} (ID: {artist['id']})")
