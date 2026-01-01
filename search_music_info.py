import re

def extract_chord_complexity(content):
    match = re.search(r"Chord Complexity\s*(\d+)", content)
    return int(match.group(1)) if match else None

def extract_melodic_complexity(content):
    match = re.search(r"Melodic Complexity\s*(\d+)", content)
    return int(match.group(1)) if match else None

def extract_key_and_mode(content):
    # Matches "written in the key of X Minor/Major"
    key_match = re.search(r"written in the key of\s+([A-G][♭♯#b]?)\s+(Minor|Major)", content, re.IGNORECASE)
    if key_match:
        return key_match.group(1), key_match.group(2)
    return None, None

def extract_bpm(content):
    match = re.search(r"(?:bpm|tempo)[:\s]+(\d+)", content, re.IGNORECASE)
    return int(match.group(1)) if match else None

def extract_genre(content):
    match = re.search(r"(?:genre|style)[:\s]+([A-Za-z\s\-]+)", content, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_trend_probability(content):
    match = re.search(r"trend[_\s]?probability[:\s]+(\d+(?:\.\d+)?)", content, re.IGNORECASE)
    return float(match.group(1)) if match else None

def extract_chord_melody_tension(content):
    match = re.search(r"Chord-Melody Tension\s*(\d+)", content)
    return int(match.group(1)) if match else None

def extract_chord_progression_novelty(content):
    match = re.search(r"Chord Progression Novelty\s*(\d+)", content)
    return int(match.group(1)) if match else None

def extract_chord_bass_melody(content):
    match = re.search(r"Chord Bass Melody\s*(\d+)", content)
    return int(match.group(1)) if match else None

def extract_title_artist(content):
    match = re.search(r"(.+?)\s+by\s+(.+?)\s+Chords", content)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

def extract_music_info_from_text(content):
    """
    Extract music information from a raw text string.
    """
    results = {
        "bpm": extract_bpm(content),
        "key_tonic": None,
        "mode": None,
        "genre": extract_genre(content),
        "chord_complexity": extract_chord_complexity(content),
        "melodic_complexity": extract_melodic_complexity(content),
        "trend_probability": extract_trend_probability(content),
        "chord_melody_tension": extract_chord_melody_tension(content),
        "chord_progression_novelty": extract_chord_progression_novelty(content),
        "chord_bass_melody": extract_chord_bass_melody(content)
    }
    
    key, mode = extract_key_and_mode(content)
    if key:
        results["key_tonic"] = key
        results["mode"] = mode
    
    # Title and Artist
    title, artist = extract_title_artist(content)
    if title:
        results["song_title"] = title
        results["artist"] = artist
    
    return results

def extract_music_info(file_path):
    """
    Extract music information from HookTheory text content dump.
    Searches for: bpm, key_tonic, mode, genre, chord_complexity, 
    melodic_complexity, trend_probability
    """
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return extract_music_info_from_text(content)


def main():
    file_path = "song_text_content.txt"
    
    print("Extracting music information from HookTheory dump...")
    print("-" * 50)
    
    info = extract_music_info(file_path)
    
    # Print requested fields
    print("\n=== Requested Fields ===")
    requested_fields = ["bpm", "key_tonic", "mode", "genre", 
                        "chord_complexity", "melodic_complexity", "trend_probability", "chord_melody_tension", "chord_progression_novelty", "chord_bass_melody"]
    
    for field in requested_fields:
        value = info.get(field)
        status = "[FOUND]" if value is not None else "[MISSING]"
        try:
            print(f"{field}: {value if value is not None else 'N/A'} {status if value is None else ''}")
        except UnicodeEncodeError:
            safe_value = str(value).encode('ascii', 'replace').decode('ascii')
            print(f"{field}: {safe_value} {status if value is None else ''}")
    
    # Print additional info found
    print("\n=== Additional Info Found ===")
    additional_fields = ["song_title", "artist"]
    
    for field in additional_fields:
        if field in info and info[field] is not None:
            print(f"{field}: {info[field]}")
    
    return info


if __name__ == "__main__":
    main()