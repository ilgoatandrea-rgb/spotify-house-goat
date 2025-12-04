import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import datetime
import json

load_dotenv()

SCOPE = "playlist-modify-public playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))

def debug_artist(artist_name):
    print(f"Debugging {artist_name}...")
    results = sp.search(q=artist_name, type='artist', limit=1)
    if not results['artists']['items']:
        print("Artist not found")
        return
    
    artist = results['artists']['items'][0]
    artist_id = artist['id']
    print(f"ID: {artist_id}")
    
    # Fetch albums exactly as manager.py does
    results = sp.artist_albums(artist_id, album_type='album,single', limit=20)
    albums = results['items']
    
    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(days=7)
    
    print(f"Current time: {now}")
    print(f"7 days ago: {seven_days_ago}")
    
    for album in albums:
        try:
            if album['release_date_precision'] != 'day':
                continue
                
            release_date = datetime.datetime.strptime(album['release_date'], '%Y-%m-%d')
            
            if release_date >= seven_days_ago:
                print(f"MATCH! New Release Found:")
                print(f"  Name: {album['name']}")
                print(f"  ID: {album['id']}")
                print(f"  Date: {album['release_date']}")
                print(f"  Type: {album.get('album_type')}")
                print(f"  Group: {album.get('album_group')}")
                
        except ValueError as e:
            print(f"  -> ERROR parsing date: {e}")

print("--- Debugging ACRAZE ---")
debug_artist("ACRAZE")
print("\n--- Debugging 3Beat ---")
debug_artist("3Beat")
