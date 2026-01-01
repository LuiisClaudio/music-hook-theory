import os
import requests
import pandas as pd
import time
import hashlib
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# Configuration
USERNAME = os.getenv('HOOKTHEORY_USER')
PASSWORD = os.getenv('HOOKTHEORY_PASS')
BASE_URL = "https://api.hooktheory.com/v1"

class HookTheoryClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()

    def authenticate(self):
        """Authenticates with HookTheory API to get the ActiveKey."""
        url = f"{BASE_URL}/users/auth"
        payload = {"username": self.username, "password": self.password}
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("activkey")
            print("Successfully authenticated.")
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            if response.content:
                print(f"Response: {response.content}")
            raise

    def get_headers(self):
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def fetch_songs_by_progression(self, chord_progression: str) -> List[Dict]:
        """
        Fetches songs containing a specific chord progression.
        """
        url = f"{BASE_URL}/trends/songs"
        params = {"cp": chord_progression}
        try:
            response = self.session.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching progression '{chord_progression}': {e}")
            return []

    def fetch_song_metadata_from_page(self, song_url: str) -> Dict:
        """
        Attempts to scrape detailed metadata (BPM, Key, Genre) from the public song page.
        This is a fallback/enhancement since the API might not provide all fields.
        """
        metadata = {
            'bpm': None,
            'key_tonic': None,
            'mode': None,
            'genre': None
        }
        
        if not song_url:
            return metadata

        try:
            # We don't need the API token for the public page, just a standard request
            # But using the session is fine.
            if not song_url.startswith('http'):
                song_url = f"https://www.hooktheory.com{song_url}"
                
            response = requests.get(song_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # These selectors are hypothetical and need adjustment based on actual page structure
                # Typically, HookTheory pages list "Key: C Major", "Tempo: 120 bpm"
                
                # Example scraping logic (robustness depends on page stability):
                text_content = soup.get_text()
                
                # Simple heuristic search
                # In a real scenario, we'd inspect the DOM. 
                # For now, we return placeholders or what we can reasonably parse if clear tags exist.
                # Often metadata is in <meta> tags or specific spans.
                
                import re
                
                # Try to find BPM
                bpm_match = re.search(r'(\d+)\s*bpm', text_content, re.IGNORECASE)
                if bpm_match:
                    metadata['bpm'] = int(bpm_match.group(1))
                
                # Try to find Key
                key_match = re.search(r'Key:\s*([A-G][#b]?)\s*(Major|Minor|Dorian|Mixolydian|Phrygian|Lydian|Locrian)', text_content, re.IGNORECASE)
                if key_match:
                    metadata['key_tonic'] = key_match.group(1)
                    metadata['mode'] = key_match.group(2)
                    
                # Try to find Genre
                genre_match = re.search(r'Genre:\s*([A-Za-z\s]+)', text_content, re.IGNORECASE)
                if genre_match:
                    metadata['genre'] = genre_match.group(1).strip()
                
        except Exception as e:
            print(f"Failed to scrape metadata for {song_url}: {e}")
        
        return metadata

    def crawl_common_progressions(self):
        """
        Crawls a set of common progressions to build a dataset.
        """
        seeds = [
            "1,5,6,4", "1,4,5,1", "1,6,4,5", 
            "2,5,1", "1,5", "1,4"
        ]
        
        all_songs_data = []
        seen_ids = set()

        for seed in seeds:
            print(f"Fetching songs for progression: {seed}")
            songs = self.fetch_songs_by_progression(seed)
            print(f"Found {len(songs)} songs.")
            
            for song in songs:
                # The API typically returns 'id' (int) or we construct one.
                # Assuming 'id' is the HookTheory ID.
                s_id = song.get('id')
                # If API doesn't return 'id', we assume unique by artist+song
                if not s_id:
                     # Create a temporary pseudo-ID for internal logic if real ID missing
                     s_id = int(hashlib.md5(f"{song['artist']}{song['song']}".encode()).hexdigest(), 16) % (10**8)
                     song['id'] = s_id
                
                # We collect all occurrences (different sections of same song might appear)
                # But for the *Songs* table, we only need unique songs.
                # For *Sections*, we need specific entries.
                
                song['queried_progression'] = seed
                all_songs_data.append(song)
            
            time.sleep(1) 
            
        return all_songs_data

    def process_data(self, raw_data):
        """
        Transforms raw API data into:
        1. Songs Table (Metadata)
        2. Sections Table
        """
        songs_dict = {}
        sections_records = []
        
        for entry in raw_data:
            # Extract Song Data ---
            ht_id = entry.get('id')
            title = entry.get('song')
            artist = entry.get('artist')
            
            # If we haven't processed this song yet, create the entry
            if ht_id not in songs_dict:
                # Try to get extra metadata (expensive operation, use carefully)
                # url = entry.get('url')
                # meta = self.fetch_song_metadata_from_page(url) 
                
                # For now, we initialize with None or defaults as API doesn't give them directly in 'trends'
                songs_dict[ht_id] = {
                    'hooktheory_id': ht_id,
                    'title': title,
                    'artist': artist,
                    'bpm': None, # Placeholder
                    'key_tonic': None, # Placeholder
                    'mode': None, # Placeholder
                    'genre': None # Placeholder
                }
            
            # Extract Section Data ---
            # section_id: Unique identifier for this specific section instance
            # We can construct it from song_id + section name (if unique per song)
            section_name = entry.get('section', 'Unknown')
            section_id = f"{ht_id}_{section_name}".replace(" ", "_").lower()
            
            # 'start_measure' is likely not in the simple response, defaulting to None
            
            sections_records.append({
                'section_id': section_id,
                'song_id': ht_id,
                'type': section_name,
                'start_measure': None # Placeholder
            })

        # Create DataFrames
        df_songs = pd.DataFrame(list(songs_dict.values()))
        df_sections = pd.DataFrame(sections_records)
        
        # Deduplicate sections if same section appeared multiple times (e.g. matched multiple progressions)
        if not df_sections.empty:
            df_sections.drop_duplicates(subset=['section_id'], inplace=True)

        return df_songs, df_sections

def main():
    print("HookTheory Username: ", USERNAME)
    # Hide password in logs
    print("HookTheory Password: ", "*****" if PASSWORD else "Not Set")

    if not USERNAME or not PASSWORD:
        print("Error: Please set HOOKTHEORY_USER and HOOKTHEORY_PASS environment variables.")
        return

    client = HookTheoryClient(USERNAME, PASSWORD)
    try:
        client.authenticate()
    except Exception:
        print("Exiting due to auth failure.")
        return

    print("Starting data fetch...")
    raw_data = client.crawl_common_progressions()
    
    print(f"Collected {len(raw_data)} raw entries.")
    
    df_songs, df_sections = client.process_data(raw_data)
    
    print("\nSongs Table")
    print(df_songs.head())
    print(df_songs.columns.tolist())
    print(f"Total Unique Songs: {len(df_songs)}")
    
    print("\nSections Table")
    print(df_sections.head())
    print(df_sections.columns.tolist())
    print(f"Total Sections: {len(df_sections)}")
    
    # Save to CSV
    df_songs.to_csv('songs.csv', index=False)
    df_sections.to_csv('sections.csv', index=False)
    print("\nSaved to songs.csv and sections.csv")

if __name__ == "__main__":
    main()
