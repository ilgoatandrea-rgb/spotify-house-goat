import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import json

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public"))

track_uris = [
    "spotify:track:4VdkZUcLJkgiCLAy3VYG28", # Do It To It (Tiësto Remix)
    "spotify:track:42qIRXhORN4WppDp4twEs5"  # Crystalised (3Beat)
]

print("Checking specific tracks...")
tracks = sp.tracks(track_uris)['tracks']

for track in tracks:
    print(f"\nTrack: {track['name']}")
    print(f"Artist: {track['artists'][0]['name']}")
    album = track['album']
    print(f"Album: {album['name']}")
    print(f"Album ID: {album['id']}")
    print(f"Release Date: {album['release_date']}")
    print(f"Album Type: {album['album_type']}")
    print(f"Album Group: {album.get('album_group')}") # Might be None if fetched via track
    
    # Check artist's albums to see if this album appears
    artist_id = track['artists'][0]['id']
    print(f"Checking if album appears in {track['artists'][0]['name']}'s artist_albums...")
    results = sp.artist_albums(artist_id, album_type='album,single', limit=50)
    found = False
    for a in results['items']:
        if a['id'] == album['id']:
            print(f"  -> FOUND in artist_albums! Group: {a.get('album_group')}")
            found = True
            break
    if not found:
        print("  -> NOT FOUND in artist_albums (maybe it's a compilation or appears_on?)")
