import time
from hook_theory_search_engine import run_search

def main():
    test_cases = [
        # 1. Metadata Search
        {"description": "Artist Filter (Adele)", "params": {"artist": "Adele"}},
        {"description": "Genre Filter (Jazz)", "params": {"genre": "Jazz"}},
        
        # # 2. Progression Search
        {"description": "Chord Progression (1,5,6,4)", "params": {"progression": "1,5,6,4"}},
        
        # # 3. Complexity/Discovery Search
        # # Limiting discovery to avoid massive crawl during simple test
        {"description": "High Chord Complexity (Discovery Mode)", "params": {"complexity_chord": "high"}},
        {"description": "Low Melodic Complexity (Discovery Mode)", "params": {"complexity_melodic": "low"}},
        
        # # 4. Combined Filters
        {"description": "Progression + Key Filter", "params": {"progression": "1,6,4,5", "key": "C"}},
        {"description": "Artist + Complexity Filter", "params": {"artist": "Nirvana", "complexity_chord": "medium"}},

        # 5. Trending Songs
        {"description": "Trending Songs", "params": {"trend": "true"}},
        {"description": "Trending Songs (Discovery Mode)", "params": {"trend": "true", "discovery": "true"}},

        # 6. Additional Test Cases
        {"description": "High Melodic Complexity", "params": {"complexity_melodic": "high"}},
        {"description": "Specific Key & Mode (A Minor)", "params": {"key": "A", "mode": "Minor"}},
        {"description": "High Chord-Melody Tension", "params": {"tension": "high"}},
        {"description": "High Progression Novelty", "params": {"novelty": "high"}},
        {"description": "Complex Rock Discovery", "params": {"genre": "Rock", "complexity_chord": "high"}},
    ]

    # 7. Top 20 Pop Artists
    pop_artists = [
        "Taylor Swift", "Ed Sheeran", "Ariana Grande", "Justin Bieber", "Katy Perry",
        "Rihanna", "Lady Gaga", "Bruno Mars", "The Weeknd", "Dua Lipa",
        "Harry Styles", "Shawn Mendes", "Miley Cyrus", "Selena Gomez", "Billie Eilish",
        "Maroon 5", "Coldplay", "Beyonce", "Drake", "Post Malone"
    ]
    for artist in pop_artists:
        test_cases.append({"description": f"Artist Filter ({artist})", "params": {"artist": artist}})

    print(f"Starting execution of {len(test_cases)} test cases...")
    print("\n") 
    #Showing the params for each test case
    print("Showing the params for each test case:")
    for test in test_cases:
        print(f"\n==================================================")
        print(f"Test: {test['description']}")
        print(f"Params: {test['params']}")
        print(f"==================================================")
        
        try:
            run_search(test['params'])
            print("Status: SUCCESS")
        except Exception as e:
            print(f"Status: FAILED ({e})")
            
        time.sleep(0.02) # Brief pause between tests

if __name__ == "__main__":
    main()
