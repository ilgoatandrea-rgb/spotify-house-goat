import os
import json
import datetime
import random
import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

STATE_FILE = 'playlist_state.json'
SCOPE = "playlist-modify-public playlist-modify-private"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"playlist_id": None, "artists": [], "tracks": []}
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def get_spotify_client():
    # Check if we are in a headless environment (GitHub Actions) and need to restore cache
    if not os.path.exists(".cache"):
        cache_content = os.environ.get("SPOTIFY_CACHE")
        if cache_content:
            print("Restoring Spotify cache from environment variable...")
            with open(".cache", "w") as f:
                f.write(cache_content)
    
    # Prevent interactive prompt hanging in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        import builtins
        def fail_input(prompt=None):
            raise Exception(f"Interactive input prevented in GitHub Actions (Prompt: {prompt})")
        builtins.input = fail_input

    try:
        # open_browser=False prevents legitimate local browser opening, but we only strictly need it 
        # to prevent popping windows on servers. Combined with the input patch above, this is safe.
        return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE, open_browser=False))

    except Exception as e:
        print(f"\nCRITICAL ERROR: Authentication failed.\nDetails: {e}")
        print("\nACTION REQUIRED: likely missing 'SPOTIFY_CACHE' secret in GitHub.")
        print("Please verify your GitHub Repository Secrets and update 'SPOTIFY_CACHE'.\n")
        raise e

def add_artist(name):
    state = load_state()
    # Check if already exists (simple check)
    if any(a['name'].lower() == name.lower() for a in state['artists']):
        print(f"Artist '{name}' is already in the list.")
        return

    sp = get_spotify_client()
    # Fuzzy search: remove 'artist:' prefix to allow broader matching
    results = sp.search(q=name, type='artist', limit=1)
    items = results['artists']['items']
    if not items:
        print(f"Artist '{name}' not found on Spotify.")
        return
    
    artist_name = items[0]['name']
    artist_id = items[0]['id']
    
    # Check if ID already exists
    if any(a['id'] == artist_id for a in state['artists']):
         print(f"Artist '{artist_name}' is already in the list.")
         return

    state['artists'].append({"name": artist_name, "id": artist_id})
    save_state(state)
    print(f"Added artist: {artist_name}")

def remove_artist(name):
    state = load_state()
    initial_count = len(state['artists'])
    
    # Filter out artist (case insensitive)
    state['artists'] = [a for a in state['artists'] if a['name'].lower() != name.lower()]
    
    if len(state['artists']) < initial_count:
        save_state(state)
        print(f"Removed artist: {name}")
    else:
        print(f"Artist '{name}' not found.")

def list_artists():
    state = load_state()
    if not state['artists']:
        print("No artists in the list.")
    else:
        print("Tracked Artists:")
        for artist in state['artists']:
            print(f"- {artist['name']}")

def get_new_releases(sp, artist_id, artist_name):
    """Fetches tracks from albums/singles released in the last 7 days."""
    new_tracks = []
    # Get albums (includes singles)
    results = sp.artist_albums(artist_id, album_type='album,single', limit=20)
    albums = results['items']
    
    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(days=7)
    
    for album in albums:
        try:
            # Release date precision can be 'year', 'month', 'day'
            if album['release_date_precision'] != 'day':
                continue
            
            release_date = datetime.datetime.strptime(album['release_date'], '%Y-%m-%d')
            
            if release_date >= seven_days_ago:
                # It's a new release! Fetch tracks.
                tracks = sp.album_tracks(album['id'])['items']
                for track in tracks:
                    # Enrich track data
                    track['album'] = album # Inject album info manually since album_tracks doesn't have it
                    track['artist_name'] = artist_name
                    new_tracks.append(track)
        except ValueError:
            continue # Skip if date format is weird

    return new_tracks

def get_back_catalog_tracks(sp, artist_id, artist_name):
    """Fetches top tracks."""
    tracks = sp.artist_top_tracks(artist_id)['tracks']
    for track in tracks:
        track['artist_name'] = artist_name
        # Top tracks usually have 'album' object already
    return tracks

def update_playlist():
    sp = get_spotify_client()
    state = load_state()
    user_id = sp.current_user()['id']

    # 1. Ensure Playlist Exists
    PLAYLIST_NAME = "NEW RELEASE HOUSE GOAT 2.0"
    if not state['playlist_id']:
        print("Creating new playlist...")
        playlist = sp.user_playlist_create(user_id, PLAYLIST_NAME, public=True, description="Updated weekly with New Releases and favorites from my artists.")
        state['playlist_id'] = playlist['id']
        save_state(state)
    
    playlist_id = state['playlist_id']
    print(f"Managing playlist: {playlist_id}")
    
    # Ensure name is up to date
    try:
        sp.playlist_change_details(playlist_id, name=PLAYLIST_NAME)
        print(f"Playlist name updated to: {PLAYLIST_NAME}")
    except Exception as e:
        print(f"Could not update playlist name: {e}")

    # 2. Remove Old Tracks (Older than 7 days) AND Orphaned Tracks (Artist removed)
    now = datetime.datetime.now()
    valid_artist_ids = {a['id'] for a in state['artists']}
    remaining_tracks = []
    
    for track in state['tracks']:
        try:
            added_at = datetime.datetime.fromisoformat(track['added_at'])
            is_expired = (now - added_at).days >= 7
            is_orphaned = track['artist_id'] not in valid_artist_ids
            
            if not is_expired and not is_orphaned:
                remaining_tracks.append(track)
        except ValueError:
            continue # Skip if date format is weird
    
    state['tracks'] = remaining_tracks
    save_state(state)

    # 3. Add New Tracks
    current_track_uris = {t['uri'] for t in state['tracks']}
    current_track_names = {t['name'].lower() for t in state['tracks']}
    
    import concurrent.futures

    print(f"Checking {len(state['artists'])} artists in parallel...")
    
    tracks_to_add_global = []

    def process_artist(artist):
        try:
            # A. Check New Releases
            new_releases = get_new_releases(sp, artist['id'], artist['name'])
            if new_releases:
                return new_releases
        except Exception as e:
            print(f"  Error processing {artist['name']}: {e}")
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_artist = {executor.submit(process_artist, artist): artist for artist in state['artists']}
        for future in concurrent.futures.as_completed(future_to_artist):
            artist = future_to_artist[future]
            try:
                results = future.result()
                if results:
                    tracks_to_add_global.extend(results)
                    print(f"  + {artist['name']}: {len(results)} new songs")
            except Exception as e:
                print(f"  Error getting result for {artist['name']}: {e}")

    # Add to state
    for track in tracks_to_add_global:
        if track['name'].lower() in current_track_names:
            continue
            
        # Ensure we have metadata
        album_name = track['album']['name'] if 'album' in track else "Unknown Album"
        track_number = track['track_number'] if 'track_number' in track else 0
        
        state['tracks'].append({
            "uri": track['uri'],
            "name": track['name'],
            "artist_id": track['artists'][0]['id'], # Use track's primary artist ID
            "artist_name": track['artist_name'],
            "album_name": album_name,
            "track_number": track_number,
            "added_at": now.isoformat()
        })
        current_track_uris.add(track['uri'])
        current_track_names.add(track['name'].lower())

    # 4. Sort Tracks
    # Sort by: Artist Name -> Album Name -> Track Number
    print("Sorting playlist...")
    
    def sort_key(t):
        return (
            t.get('artist_name', '').lower(), 
            t.get('album_name', '').lower(), 
            t.get('track_number', 0)
        )

    state['tracks'].sort(key=sort_key)
    
    # 5. Sync to Spotify (Replace Items)
    final_uris = [t['uri'] for t in state['tracks']]
    
    if final_uris:
        print(f"Syncing {len(final_uris)} tracks to Spotify...")
        # replace_items can handle max 100 tracks. If more, we replace first 100 then add the rest.
        
        first_chunk = final_uris[:100]
        sp.playlist_replace_items(playlist_id, first_chunk)
        
        if len(final_uris) > 100:
            remaining = final_uris[100:]
            for i in range(0, len(remaining), 100):
                chunk = remaining[i:i+100]
                sp.playlist_add_items(playlist_id, chunk)
    else:
        print("Playlist is empty, clearing Spotify playlist...")
        sp.playlist_replace_items(playlist_id, [])

    save_state(state)
    print("Update complete.")

def import_playlist(playlist_url):
    sp = get_spotify_client()
    state = load_state()
    
    print(f"Fetching tracks from playlist: {playlist_url}...")
    try:
        # Handle pagination to get all tracks
        results = sp.playlist_items(playlist_url, additional_types=['track'])
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
            
        print(f"Found {len(tracks)} tracks. Extracting artists...")
        
        added_count = 0
        existing_ids = {a['id'] for a in state['artists']}
        
        for item in tracks:
            if not item['track']: continue
            
            # Get primary artist of the track
            artist = item['track']['artists'][0]
            artist_id = artist['id']
            artist_name = artist['name']
            
            if artist_id not in existing_ids:
                state['artists'].append({"name": artist_name, "id": artist_id})
                existing_ids.add(artist_id)
                added_count += 1
                print(f"  + {artist_name}")
        
        save_state(state)
        print(f"Import complete! Added {added_count} new artists.")
        
    except Exception as e:
        print(f"Error importing playlist: {e}")

def check_genres():
    sp = get_spotify_client()
    state = load_state()
    artists = state['artists']
    
    # Keywords that indicate the artist is "safe" (belongs to requested genres)
    SAFE_KEYWORDS = ['house', 'tech', 'deep', 'afro', 'minimal', 'electronic', 'dance', 'techno', 'disco', 'club', 'edm']
    
    print(f"Checking genres for {len(artists)} artists...")
    
    artist_ids = [a['id'] for a in artists if a.get('id')]
    suspicious_artists = []
    
    print(f"Valid IDs found: {len(artist_ids)}")

    for i in range(0, len(artist_ids), 50):
        chunk = artist_ids[i:i+50]
        try:
            full_artists = sp.artists(chunk)['artists']
        except Exception as e:
            print(f"Error fetching chunk {i}: {e}")
            continue
        
        for artist in full_artists:
            if not artist: continue # Skip if artist is None
            
            genres = artist.get('genres', [])
            if not genres:
                # No genres listed? Might be obscure or new. Mark as suspicious?
                # Or maybe safe? Let's mark as suspicious to be safe.
                suspicious_artists.append(f"{artist['name']} (No genres found)")
                continue

            # Check if ANY genre matches ANY keyword
            is_safe = False
            for genre in genres:
                if not genre: continue
                for keyword in SAFE_KEYWORDS:
                    if keyword in genre.lower():
                        is_safe = True
                        break
                if is_safe: break
            
            if not is_safe:
                suspicious_artists.append(f"{artist['name']} (Genres: {', '.join(genres)})")

    if suspicious_artists:
        print("\nPossible non-electronic artists found:")
        for a in suspicious_artists:
            print(f"- {a}")
    else:
        print("\nAll artists seem to fit the electronic/house genres.")

def main():
    parser = argparse.ArgumentParser(description="Spotify Dynamic Playlist Manager")
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add', help='Add an artist')
    add_parser.add_argument('name', help='Name of the artist')
    
    remove_parser = subparsers.add_parser('remove', help='Remove an artist')
    remove_parser.add_argument('name', help='Name of the artist')

    list_parser = subparsers.add_parser('list', help='List tracked artists')

    update_parser = subparsers.add_parser('update', help='Update the playlist')
    
    import_parser = subparsers.add_parser('import', help='Import artists from a playlist')
    import_parser.add_argument('url', help='Spotify Playlist URL')
    
    genre_parser = subparsers.add_parser('check_genres', help='Check for non-electronic artists')

    args = parser.parse_args()

    if args.command == 'add':
        add_artist(args.name)
    elif args.command == 'remove':
        remove_artist(args.name)
    elif args.command == 'list':
        list_artists()
    elif args.command == 'update':
        update_playlist()
    elif args.command == 'import':
        import_playlist(args.url)
    elif args.command == 'check_genres':
        check_genres()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
