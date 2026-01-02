import time
from hook_theory_search_engine import run_search

def main():
    test_cases = [
        # 1. Metadata Search
        # {"description": "Artist Filter (Adele)", "params": {"artist": "Adele"}},
        # {"description": "Genre Filter (Jazz)", "params": {"genre": "Jazz"}},
        
        # # 2. Progression Search
        # {"description": "Chord Progression (1,5,6,4)", "params": {"progression": "1,5,6,4"}},
        
        # # 3. Complexity/Discovery Search
        # # Limiting discovery to avoid massive crawl during simple test
        # {"description": "High Chord Complexity (Discovery Mode)", "params": {"complexity_chord": "high"}},
        # {"description": "Low Melodic Complexity (Discovery Mode)", "params": {"complexity_melodic": "low"}},
        
        # # 4. Combined Filters
        # {"description": "Progression + Key Filter", "params": {"progression": "1,6,4,5", "key": "C"}},
        # {"description": "Artist + Complexity Filter", "params": {"artist": "Nirvana", "complexity_chord": "medium"}},

        # 5. Trending Songs
        {"description": "Trending Songs", "params": {"trend": "true"}},
        {"description": "Trending Songs (Discovery Mode)", "params": {"trend": "true", "discovery": "true"}},
    ]

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
