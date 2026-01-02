import argparse
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from hook_theory_api import HookTheoryClient
import time
import hashlib

# Load environment variables
load_dotenv()

# Constants
# The expected search page URL. 
# While exact URL parameters for some filters (meter/tempo) heavily depend on the specific form logic (possibly JS-based),
# a text query usually goes to /theorytab/results.
def slugify(text):
    return text.lower().replace(" ", "-").replace("'", "")

def crawl_search_results(params):
    """
    Crawls HookTheory by constructing Browse URLs for Artist/Genre, or guessing the Song URL.
    Returns a list of song URLs.
    """
    song_urls = []
    
    # Strategy 1: Direct Song URL (Best Guess)
    if params.get('artist') and params.get('song'):
        artist_slug = slugify(params['artist'])
        song_slug = slugify(params['song'])
        # HookTheory URL format: /theorytab/view/artist/song
        url = f"https://www.hooktheory.com/theorytab/view/{artist_slug}/{song_slug}"
        print(f"Guessing direct song URL: {url}")
        # Verify if it exists (HEAD request or GET)
        try:
            r = requests.head(url, timeout=5)
            if r.status_code == 200:
                song_urls.append(url)
            else:
                 # Try GET in case HEAD is blocked
                 r = requests.get(url, timeout=5)
                 if r.status_code == 200:
                    song_urls.append(url)
                 else:
                    print(f"Direct URL failed (Status {r.status_code}). Trying Artist browse...")
        except:
            pass

    # Strategy 2: Browse by Artist
    # URL: https://www.hooktheory.com/theorytab/artists/a/adele
    if not song_urls and params.get('artist'):
        artist_slug = slugify(params['artist'])
        first_char = artist_slug[0] if artist_slug else 'a'
        if first_char.isdigit(): first_char = '1' # HookTheory groups 0-9 under '1' usually or similar? Let's assume char.
        
        browse_url = f"https://www.hooktheory.com/theorytab/artists/{first_char}/{artist_slug}"
        print(f"Browsing Artist page: {browse_url}")
        
        song_urls.extend(crawl_list_page(browse_url))

    # Strategy 3: Browse by Genre
    # URL: https://www.hooktheory.com/theorytab/genres/pop
    if not song_urls and params.get('genre'):
        genre_slug = slugify(params['genre'])
        browse_url = f"https://www.hooktheory.com/theorytab/genres/{genre_slug}"
        print(f"Browsing Genre page: {browse_url}")
        
        song_urls.extend(crawl_list_page(browse_url))
        
    # Warn about unsupported filters for scraping
    if params.get('meter') or params.get('tempo') or params.get('key'):
        print("Warning: Meter, Tempo, and Key filters are not supported in this scraper mode (requires advanced search URL).")
        print("Returning results found by Artist/Genre/Song only.")

    return song_urls

def crawl_list_page(url):
    """Helper to extract song links from an overview page."""
    urls = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch list page: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse song links. 
        # On Artist/Genre pages, songs are usually keys <li><a>...
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Valid song link: /theorytab/view/artist/song
            # Avoid: /theorytab/artists/..., /theorytab/genres/...
            if href.startswith('/theorytab/view/') and 'common-chord-progressions' not in href:
                full_url = f"https://www.hooktheory.com{href}"
                if full_url not in urls:
                    urls.append(full_url)
    except Exception as e:
        print(f"Error crawling list page {url}: {e}")
    return urls

def main():
    parser = argparse.ArgumentParser(description="HookTheory Search Engine")
    
    # Form fields as requested
    parser.add_argument("--artist", help="Filter by Artist")
    parser.add_argument("--song", help="Filter by Song")
    parser.add_argument("--genre", help="Filter by Genre")
    parser.add_argument("--key", help="Filter by Key (e.g. C)")
    parser.add_argument("--scale", help="Filter by Scale (e.g. Major)")
    parser.add_argument("--meter", help="Filter by Meter (e.g. 4/4)")
    parser.add_argument("--tempo", help="Filter by Tempo")
    
# Additional imports might be needed if not present
import sys

def filter_dataframe(df_row, filters):
    """
    Checks if the processed song data (DataFrame row) matches the filters.
    """
    if df_row.empty: return False
    
    row = df_row.iloc[0]
    
    # 1. Exact/String matches
    if filters.get('key'):
        # Normalize: 'C' vs 'C Major' vs 'C#'. row['key_tonic'] usually just tonic e.g. 'C'
        # row['mode'] allows checking Scale.
        target_key = filters['key'].strip().lower()
        current_key = str(row.get('key_tonic', '')).lower()
        if target_key not in current_key: return False

    if filters.get('scale'):
        # e.g. Major/Minor
        target_scale = filters['scale'].strip().lower()
        current_mode = str(row.get('mode', '')).lower()
        if target_scale not in current_mode: return False

    if filters.get('meter'):
        # Meter isn't currently extracted in hook_theory_api metadata?
        # Check available columns. If not available, we can't filter (or warn).
        # Assuming extracted data has it or we skip.
        # User asked to search by it. If we don't extract it, we can't filter.
        # Proceeding without strict check if missing column, or implement extra scraping?
        # For now, if missing, ignored.
        pass
        
    if filters.get('tempo'):
        # BPM check. Allow range or exact?
        # User said "Search Tabs by ... Tempo". Assuming exact or close.
        pass

    # 2. Complexity Mapping
    # Logic: Low (0-33), Medium (34-66), High (67-100)
    # Range modifiers: "medium-high" -> 34-100? or > 50?
     
    metrics_map = {
        'complexity_chord': 'chord_complexity',
        'complexity_melodic': 'melodic_complexity',
        'complexity_tension': 'chord_melody_tension',
        'complexity_novelty': 'chord_progression_novelty',
        'complexity_bass': 'chord_bass_melody'
    }
    
    for filter_key, col_name in metrics_map.items():
        if filters.get(filter_key):
            val_str = str(row.get(col_name, '0')).replace('%', '')
            try:
                val = float(val_str)
            except:
                val = 0
            
            criteria = filters[filter_key].lower()
            
            # Simple fuzzy range logic
            is_match = False
            if 'low' in criteria:
                if val <= 40: is_match = True
            if 'medium' in criteria:
                if 25 <= val <= 75: is_match = True # Overlap generic
            if 'high' in criteria:
                if val >= 60: is_match = True
                
            # Specific composite handling "medium-high"
            if 'medium-high' in criteria:
                if val >= 40: is_match = True
                
            if not is_match:
                return False

    return True

def crawl_charts(limit=20):
    """Fallback: Crawls the Charts page to find candidate URLs."""
    print("Crawling Charts for candidates...")
    url = "https://www.hooktheory.com/theorytab/charts"
    return crawl_list_page(url)[:limit]

def crawl_common_progressions(client, seeds=None):
    if seeds is None:
        seeds = ["1,5,6,4", "1,4,5,1", "1,6,4,5"]
    elif isinstance(seeds, str):
        seeds = [seeds]
        
    all_songs_data = []
    
    for seed in seeds:
        print(f"Fetching songs for progression: {seed}")
        songs = client.fetch_songs_by_progression(seed)
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

def run_search(params):
    """
    Executes the search and processing logic with the given parameters.
    """
    print(f"\n--- Starting Search with Params: {params} ---")
    
    print("Initializing HookTheory Search Engine...")
    
    user = os.getenv('HOOKTHEORY_USER')
    password = os.getenv('HOOKTHEORY_PASS')
    client = HookTheoryClient(user, password)
    
    # Authenticate if needed (Progression search requires it)
    if params.get('progression'):
        try:
            client.authenticate()
        except:
            print("Authentication failed. Progression search may fail.")

    # 1. Gather Candidate URLs
    candidate_urls = []
    
    # Source A: Progression API
    if params.get('progression'):
        print(f"Searching by Progression: {params['progression']}")
        try:
            results = crawl_common_progressions(client, seeds=params['progression'])
            # Extract URLs from API results
            for r in results:
                if r.get('url'):
                    u = r['url']
                    if not u.startswith('http'): u = f"https://www.hooktheory.com{u}"
                    candidate_urls.append(u)
        except Exception as e:
            print(f"Progression search error: {e}")

    # Source B: Metadata search (Artist/Genre/song)
    if params.get('artist') or params.get('genre') or params.get('song'):
        print("Searching by Metadata (Artist/Genre)...")
        urls = crawl_search_results(params)
        candidate_urls.extend(urls)

    # Source C: Trending
    if params.get('trend'):
        print("Searching Trending Songs...")
        candidate_urls.extend(crawl_charts())

    # Source D: Passive/Discovery (Only complexity/theory provided)
    # If we have NO candidates yet, but have filters, we must browse Charts/Browse to find candidates.
    if not candidate_urls and not (params.get('artist') or params.get('genre') or params.get('song') or params.get('progression')):
        if any(k.startswith('complexity') for k in params) or params.get('key') or params.get('scale'):
             print("No direct search terms (Artist/Progression). Crawling Charts to find filtering matches...")
             candidate_urls.extend(crawl_charts())

    # De-duplicate
    candidate_urls = sorted(list(set(candidate_urls)))
    print(f"Found {len(candidate_urls)} candidate songs to process.")
    
    # 2. Process & Apply Filters
    processed_count = 0
    matched_count = 0
    
    for url in candidate_urls:
        try:
            # Process (Scrape & Build DF)
            # We use process_single_url to getting the DF without appending yet
            df_songs, df_events = client.process_single_url(url)
            
            # Check Filters
            if filter_dataframe(df_songs, params):
                print(f"Match found: {url}")
                client.append_to_csv(df_songs, 'hooktheory_songs.csv')
                client.append_to_csv(df_events, 'hooktheory_chords.csv')
                matched_count += 1
            else:
                print(f"Filtered out: {url}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"Failed to process {url}: {e}")

    print(f"\nSearch complete. Processed {processed_count} songs. Matched & Saved {matched_count}.")

def main():
    parser = argparse.ArgumentParser(description="HookTheory Search Engine")
    
    # Group 1: Standard Metadata
    parser.add_argument("--artist", help="Filter by Artist")
    parser.add_argument("--song", help="Filter by Song")
    parser.add_argument("--genre", help="Filter by Genre")
    
    # Group 2: Theory Filters
    parser.add_argument("--key", help="Filter by Key (e.g. C)")
    parser.add_argument("--scale", help="Filter by Scale (e.g. Major)")
    parser.add_argument("--meter", help="Filter by Meter (e.g. 4/4)")
    parser.add_argument("--tempo", help="Filter by Tempo/BPM")
    
    # Group 3: Progression
    parser.add_argument("--progression", help="Chord Progression (e.g. 1,5,6,4)")
    
    # Group 4: Complexity Metrics (Accepts 'low', 'medium', 'high', etc.)
    parser.add_argument("--complexity_chord", help="Chord Complexity")
    parser.add_argument("--complexity_melodic", help="Melodic Complexity")
    parser.add_argument("--complexity_tension", help="Chord Melody Tension")
    parser.add_argument("--complexity_novelty", help="Chord Progression Novelty")
    parser.add_argument("--complexity_bass", help="Bass Melody")

    # Group 5: Discovery
    parser.add_argument("--trend", action="store_true", help="Search for trending songs")

    args = parser.parse_args()
    params = {k: v for k, v in vars(args).items() if v is not None}
    
    if not params:
        # print("No args provided. Using Default Test (Artist=Nirvana).")
        # params = {'artist': 'Nirvana'}
        return
    else:
        run_search(params)

if __name__ == "__main__":
    main()
