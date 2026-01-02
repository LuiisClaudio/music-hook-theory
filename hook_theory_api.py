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
from search_music_info import extract_music_info_from_text

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
            'melodic_complexity': None,
            'chord_melody_tension': None,
            'chord_progression_novelty': None,
            'chord_bass_melody': None,
            
            'type': None,
            'roman_numeral': None,
            'absolute_root': None,
            'inversion': None,

            'chord_progression': None,
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
                #Dump the text content to a file
                with open("song_text_content.txt", "w", encoding="utf-8") as f:
                    f.write(text_content)
                
                # Parse metadata from text
                # Using the imported helper from search_music_info
                scraped_data = extract_music_info_from_text(text_content)
                metadata.update(scraped_data)

        except Exception as e:
            print(f"Failed to scrape {song_url}: {e}")
        
        return metadata





    def calculate_spiral_array_tension(self, chord_symbol: str, key_tonic: str, mode: str) -> float:
        """
        Calculates a simplified Spiral Array 'tensile strain' (distance from key).
        Uses a basic Pythagorean tuning logic where Perfect 5th = 1 unit height.
        Key Center is at (0,0,0) in relative space.
        """
        # Simplified Spiral Array positions (Relative to C Major)
        # Position k on spiral: x = r*sin(k*theta), y = r*cos(k*theta), z = k*h
        # Here we just use pre-computed relative distances or a simple lookup table for demonstration
        # Logic: 
        # I (Tonic) -> Distance 0 (Reference)
        # V (Dominant) -> Close (1 step)
        # IV (Subdominant) -> Close (1 step in other direction)
        # vi (Relative Minor) -> Moderate
        # vii (Leading Tone) -> High Tension
        
        # Normalize chord symbol
        chord_clean = chord_symbol.replace('7','').replace('maj','').replace('min','')
        
        # Tension Map (Heuristic based on Spiral Array Distance from Tonic I)
        tension_map = {
            '1': 0.0, 'I': 0.0, 'i': 0.5,
            '5': 1.0, 'V': 1.0, 'v': 1.5,
            '4': 1.0, 'IV': 1.0, 'iv': 1.5,
            '6': 2.0, 'vi': 2.0, 'VI': 2.5,
            '3': 3.0, 'iii': 3.0, 'III': 3.5,
            '2': 2.5, 'ii': 2.5, 'II': 3.0,
            '7': 4.5, 'vii': 4.5, 'VII': 4.0
        }
        
        # Check against map
        base_tension = tension_map.get(chord_clean, 2.0) # Default moderate tension
        
        # Modifiers
        if '7' in chord_symbol: base_tension += 0.5
        if 'dim' in chord_symbol: base_tension += 1.5
        if 'aug' in chord_symbol: base_tension += 1.5
            
        return base_tension

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
                    'url': url,
                    'title': title,
                    'artist': artist,
                    'bpm': meta.get('bpm'),
                    'key_tonic': meta.get('key_tonic'),
                    'mode': meta.get('mode'),
                    'genre': meta.get('genre'),
                    'chord_complexity': meta.get('chord_complexity'),
                    'melodic_complexity': meta.get('melodic_complexity'),
                    'chord_melody_tension': meta.get('chord_melody_tension'),
                    'chord_progression_novelty': meta.get('chord_progression_novelty'),
                    'chord_bass_melody': meta.get('chord_bass_melody'),
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
            #print chord numerals
            print(f"Chord numerals: {chord_numerals}")
            
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
                    'roman_numeral': numeral,
                    'absolute_root': abs_root,
                    'inversion': 0, # Placeholder
                    'tension_strain': tension
                })

        # Create DataFrames
        df_songs = pd.DataFrame(list(songs_dict.values()))
        df_events = pd.DataFrame(events_records)
        
        return df_songs, df_events
    
    def process_single_url(self, url: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetches metadata for a single URL and orchestrates process_data to return DataFrames.
        """
        print(f"Processing URL: {url}")
        
        # 1. Scrape first to get Title/Artist needed for ID generation and Entry construction
        meta = self.fetch_song_metadata_from_page(url)
        #Print meta
        print(f"Meta: {meta}")
        
        #Dump meta to a txt file
        with open("meta.txt", "w", encoding="utf-8") as f:
            f.write(str(meta))
        
        title = meta.get('song_title', 'Unknown')
        artist = meta.get('artist', 'Unknown')
        
        # Generate ID consistent with main logic
        ht_id = int(hashlib.md5(f"{artist}{title}".encode()).hexdigest(), 16) % (10**8)
        
        # 2. Construct Song Dictionary directly (as requested)
        song_entry = {
            'hooktheory_id': ht_id,
            'url': url,
            'title': title,
            'artist': artist,
            'bpm': meta.get('bpm'),
            'key_tonic': meta.get('key_tonic'),
            'mode': meta.get('mode'),
            'genre': meta.get('genre'),
            'chord_complexity': meta.get('chord_complexity'),
            'melodic_complexity': meta.get('melodic_complexity'),
            'chord_melody_tension': meta.get('chord_melody_tension'),
            'chord_progression_novelty': meta.get('chord_progression_novelty'),
            'chord_bass_melody': meta.get('chord_bass_melody'),
            'trend_probability': meta.get('trend_probability')
        }
        
        # 3. Construct Events Records directly checks
        events_records = []
        path_str = meta.get('chord_progression', '')
        
        if path_str:
            chord_numerals = [c.strip() for c in path_str.split(',') if c.strip()]
            current_key = song_entry.get('key_tonic', 'C')
            
            section_name = meta.get('type', 'Unknown')
            section_id = f"{ht_id}_{section_name}".replace(" ", "_").lower()
            
            print(f"Chord numerals: {chord_numerals}")
            
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
                
                tension = self.calculate_spiral_array_tension(numeral, current_key, song_entry.get('mode'))

                events_records.append({
                    'section_id': section_id,
                    'song_id': ht_id,
                    'type': section_name,
                    'roman_numeral': numeral,
                    'absolute_root': abs_root,
                    'inversion': 0, # Placeholder
                    'tension_strain': tension
                })
        
        # 4. Create DataFrames
        df_songs = pd.DataFrame([song_entry])
        df_events = pd.DataFrame(events_records)
        
        return df_songs, df_events

    def append_to_csv(self, df: pd.DataFrame, csv_path: str):
        """
        Appends a DataFrame to a CSV file, handling header creation.
        """
        import os
        df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
        print(f"Appended {len(df)} rows to {csv_path}.")

    def process_single_url_and_append(self, url: str, csv_path: str = 'hooktheory_songs.csv'):
        """
        Orchestrates processing a single URL and appending to CSV.
        """
        try:
            df_songs,df_events = self.process_single_url(url)
            self.append_to_csv(df_songs, csv_path)
            self.append_to_csv(df_events, 'hooktheory_chords.csv')
            print("Successfully processed and appended single URL.")
        except Exception as e:
            print(f"Error processing URL {url}: {e}")



def main(): 
    if not USERNAME or not PASSWORD:
        print("Error: Set HOOKTHEORY_USER and HOOKTHEORY_PASS.")
        return

    client = HookTheoryClient(USERNAME, PASSWORD)
    try:
        client.authenticate()
    except Exception:
        return

    # print("Starting data fetch...")
    # raw_data = client.crawl_common_progressions()
    
    # print(f"Collected {len(raw_data)} raw entries.")
    
    # df_songs, df_events = client.process_data(raw_data)
    
    # # Save
    # df_songs.to_csv('hooktheory_songs.csv', index=False)
    # df_events.to_csv('hooktheory_chords.csv', index=False) 
    
    # print("\nSaved tables to CSV.")
    # print("Songs:", len(df_songs))
    # print("Events (Chords flattened):", len(df_events))
    
    # Example usage of the new function
    url = "https://www.hooktheory.com/theorytab/view/scorpions/still-loving-you"
    client.process_single_url_and_append(url)

if __name__ == "__main__":
    main()
