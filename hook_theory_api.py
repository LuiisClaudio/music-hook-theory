import os
import requests
import pandas as pd
import time
import hashlib
import re
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import warnings

# Attempt to import music21
try:
    import music21
    HAS_MUSIC21 = True
except ImportError:
    HAS_MUSIC21 = False
    print("Warning: music21 not found. Some calculations will be skipped.")

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
        """Authenticates with HookTheory API."""
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
            raise

    def get_headers(self):
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def fetch_songs_by_progression(self, chord_progression: str) -> List[Dict]:
        """Fetches songs containing a specific chord progression."""
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
        Scrapes detailed metadata (BPM, Key, Complexity) from the public song page.
        """
        metadata = {
            'bpm': None,
            'key_tonic': None,
            'mode': None,
            'genre': None,
            'chord_complexity': None,
            'melodic_complexity': None
        }
        
        # Song URL validation
        #print song url
        #print(f"Fetching song metadata from: {song_url}\n")
        if not song_url:
            return metadata

        try:
            if not song_url.startswith('http'):
                song_url = f"https://www.hooktheory.com{song_url}"
                
            response = requests.get(song_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text()
                #print text_content
                #print(f"Text content: {text_content}\n")
                
                # Parse metadata from text
                scraped_data = self._parse_metadata_from_text(text_content)
                metadata.update(scraped_data)

        except Exception as e:
            print(f"Failed to scrape {song_url}: {e}")
        
        return metadata

    def _parse_bpm(self, text_content: str) -> Optional[int]:
        match = re.search(r'(\d+)\s*bpm', text_content, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _parse_key_and_mode(self, text_content: str) -> Tuple[Optional[str], Optional[str]]:
        #print(text_content)
        match = re.search(r'Key:\s*([A-G][#b]?)\s*(Major|Minor|Dorian|Mixolydian|Phrygian|Lydian|Locrian)', text_content, re.IGNORECASE)
        if match:
            # print(match.group(1))
            print("Achei um match")
            return match.group(1), match.group(2)
        return None, None

    def _parse_genre(self, text_content: str) -> Optional[str]:
        match = re.search(r'Genre:\s*([A-Za-z\s]+)', text_content, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _parse_chord_complexity(self, text_content: str) -> Optional[int]:
        match = re.search(r'Chord Complexity:?\s*(\d{1,3})', text_content, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _parse_melodic_complexity(self, text_content: str) -> Optional[int]:
        match = re.search(r'Melodic Complexity:?\s*(\d{1,3})', text_content, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _parse_metadata_from_text(self, text_content: str) -> Dict:
        """Parses metadata fields from the raw text content of a song page."""
        data = {}
        
        bpm = self._parse_bpm(text_content)
        if bpm: data['bpm'] = bpm
        
        key, mode = self._parse_key_and_mode(text_content)
        if key: 
            data['key_tonic'] = key
            data['mode'] = mode
            
        genre = self._parse_genre(text_content)
        if genre: data['genre'] = genre
        
        cc = self._parse_chord_complexity(text_content)
        if cc is not None: data['chord_complexity'] = cc
        
        mc = self._parse_melodic_complexity(text_content)
        if mc is not None: data['melodic_complexity'] = mc
        
        return data



    def crawl_common_progressions(self):
        seeds = ["1,5,6,4", "1,4,5,1", "1,6,4,5"] 
        all_songs_data = []
        
        for seed in seeds:
            print(f"Fetching songs for progression: {seed}")
            songs = self.fetch_songs_by_progression(seed)
            print(f"Found {len(songs)} songs.")
            
            for song in songs:
                s_id = song.get('id')
                if not s_id:
                     s_id = int(hashlib.md5(f"{song['artist']}{song['song']}".encode()).hexdigest(), 16) % (10**8)
                     song['id'] = s_id
                
                song['queried_progression'] = seed
                all_songs_data.append(song)
            time.sleep(1)
        return all_songs_data

    def calculate_spiral_array_tension(self, chord_symbol: str, key_tonic: str, mode: str) -> float:
        """
        Calculates a simplified Spiral Array 'tensile strain' (distance from key).
        """
        return 0.0

    def process_data(self, raw_data):
        songs_dict = {}
        events_records = []
        
        for entry in raw_data:
            ht_id = entry.get('id')
            title = entry.get('song')
            artist = entry.get('artist')
            url = entry.get('url')
            
            # SONGS TABLE (Merged with Metrics)
            if ht_id not in songs_dict:
                # Scrape detailed metadata
                meta = self.fetch_song_metadata_from_page(url)
                
                songs_dict[ht_id] = {
                    'hooktheory_id': ht_id,
                    'title': title,
                    'artist': artist,
                    'bpm': meta['bpm'],
                    'key_tonic': meta['key_tonic'],
                    'mode': meta['mode'],
                    'genre': meta['genre'],
                    'chord_complexity': meta['chord_complexity'],
                    'melodic_complexity': meta['melodic_complexity'],
                    'trend_probability': None # Placeholder
                }

            # EVENTS/CHORDS TABLE (Flattened)
            section_name = entry.get('section', 'Unknown')
            # Create a unique section_id
            section_id = f"{ht_id}_{section_name}".replace(" ", "_").lower()
            
            path_str = entry.get('path', '')
            if not path_str:
                path_str = entry.get('queried_progression', '')
            
            chord_numerals = path_str.split(',')
            current_key = songs_dict[ht_id].get('key_tonic', 'C') 
            
            for i, numeral in enumerate(chord_numerals):
                abs_root = -1
                if HAS_MUSIC21 and current_key:
                    try:
                        rn_str = numeral
                        if numeral.isdigit():
                            rn_map = {'1':'I', '2':'ii', '3':'iii', '4':'IV', '5':'V', '6':'vi', '7':'vii'}
                            rn_str = rn_map.get(numeral, 'I')
                        
                        rn = music21.roman.RomanNumeral(rn_str, current_key)
                        abs_root = rn.root().pitchClass
                    except Exception:
                        pass
                
                tension = self.calculate_spiral_array_tension(numeral, current_key, songs_dict[ht_id].get('mode'))

                events_records.append({
                    'section_id': section_id,
                    'song_id': ht_id,
                    'type': section_name,
                    'start_measure': None, # Placeholder
                    'roman_numeral': numeral,
                    'absolute_root': abs_root,
                    'inversion': 0, # Placeholder
                    'tension_strain': tension
                })

        # Create DataFrames
        df_songs = pd.DataFrame(list(songs_dict.values()))
        df_events = pd.DataFrame(events_records)
        
        return df_songs, df_events

def main(): 
    if not USERNAME or not PASSWORD:
        print("Error: Set HOOKTHEORY_USER and HOOKTHEORY_PASS.")
        return

    client = HookTheoryClient(USERNAME, PASSWORD)
    try:
        client.authenticate()
    except Exception:
        return

    print("Starting data fetch...")
    raw_data = client.crawl_common_progressions()
    
    print(f"Collected {len(raw_data)} raw entries.")
    
    df_songs, df_events = client.process_data(raw_data)
    
    # Save
    df_songs.to_csv('hooktheory_songs.csv', index=False)
    df_events.to_csv('hooktheory_chords.csv', index=False) 
    
    print("\nSaved tables to CSV.")
    print("Songs:", len(df_songs))
    print("Events (Chords flattened):", len(df_events))

if __name__ == "__main__":
    main()
