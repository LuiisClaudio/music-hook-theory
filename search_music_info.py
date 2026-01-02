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

def extract_type(content):
    # Determine section type (Chorus, Verse, etc.) - case insensitive
    content_lower = content.lower()
    if "pre-chorus" in content_lower or "prechorus" in content_lower:
        return "Pre-Chorus"
    if "chorus" in content_lower:
        return "Chorus"
    if "verse" in content_lower:
        return "Verse"
    if "intro" in content_lower:
        return "Intro"
    if "outro" in content_lower:
        return "Outro"
    if "bridge" in content_lower:
        return "Bridge"
    if "hook" in content_lower:
        return "Hook"
    if "interlude" in content_lower:
        return "Interlude"
    return "Unknown"

def extract_start_measure(content):
    # Multiple patterns for start measure
    patterns = [
        r"Start Measure\s*[:\-]?\s*(\d+)",
        r"measures?\s+(\d+)\s*[-–to]+\s*\d+",
        r"m\.?\s*(\d+)\s*[-–to]+\s*\d+",
        r"from\s+measure\s+(\d+)",
        r"begins?\s+(?:at\s+)?(?:measure\s+)?(\d+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

def extract_end_measure(content):
    # Multiple patterns for end measure
    patterns = [
        r"End Measure\s*[:\-]?\s*(\d+)",
        r"measures?\s+\d+\s*[-–to]+\s*(\d+)",
        r"m\.?\s*\d+\s*[-–to]+\s*(\d+)",
        r"to\s+measure\s+(\d+)",
        r"ends?\s+(?:at\s+)?(?:measure\s+)?(\d+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

def extract_roman_numeral(content):
    # Match Roman numeral chords: I, ii, IV, V7, bVII, #iv, etc.
    # Returns list of all Roman numerals found
    pattern = r'\b([b#♭♯]?(?:III|II|IV|VII|VI|V|I|iii|ii|iv|vii|vi|v|i)(?:M|m|dim|aug|add|sus|maj|min)?[0-9]*)(?:/[0-9A-Ga-g#♭♯b]+)?\b'
    matches = re.findall(pattern, content)
    if matches:
        # Return unique chords preserving order
        seen = set()
        unique = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                unique.append(m)
        return unique if unique else None
    return None

def extract_absolute_root(content):
    # Extract root notes like A, Bb, C#, D♯, E♭
    pattern = r'\b([A-G][b#♭♯]?)\s*(?:Major|Minor|maj|min|m|M)?\b'
    matches = re.findall(pattern, content)
    if matches:
        # Return unique roots
        seen = set()
        unique = []
        for m in matches:
            normalized = m.replace('♭', 'b').replace('♯', '#')
            if normalized not in seen:
                seen.add(normalized)
                unique.append(normalized)
        return unique if unique else None
    return None

def extract_inversion(content):
    # Detect inversions: slash chords like "I/3", "V/5", "IV/B"
    # HookTheory uses scale degree notation (1-7) or note names
    pattern = r'\b([b#♭♯]?(?:III|II|IV|VII|VI|V|I|iii|ii|iv|vii|vi|v|i)[^/]*)/([1-7]|[A-G][b#♭♯]?)\b'
    matches = re.findall(pattern, content)
    if matches:
        inversions = [{"chord": m[0], "bass": m[1]} for m in matches]
        return inversions if inversions else None
    return None

def extract_chord_progression(content):
    # Multiple patterns for chord progressions
    # Pattern 1: Labeled progression (e.g., "Progression: I V vi IV")
    labeled = re.search(
        r"(?:Progression|Chords?)\s*[:\-]?\s*((?:[b#♭♯]?(?:III|II|IV|VII|VI|V|I|iii|ii|iv|vii|vi|v|i)(?:M|m|dim|aug|add|sus|maj|min)?[0-9]*(?:/[1-7A-G#♭♯b])?[\s,\-–→]+)+[b#♭♯]?(?:III|II|IV|VII|VI|V|I|iii|ii|iv|vii|vi|v|i)(?:M|m|dim|aug|add|sus|maj|min)?[0-9]*(?:/[1-7A-G#♭♯b])?)",
        content, re.IGNORECASE
    )
    if labeled:
        prog = labeled.group(1)
        # Normalize separators
        prog = re.sub(r'[\s,\-–→]+', ' ', prog).strip()
        return prog
    
    # Pattern 2: Standalone sequence of Roman numerals (3+ chords)
    standalone = re.search(
        r'\b((?:[b#♭♯]?(?:III|II|IV|VII|VI|V|I|iii|ii|iv|vii|vi|v|i)(?:M|m|dim|aug|add|sus|maj|min)?[0-9]*(?:/[1-7A-G#♭♯b])?\s+){2,}[b#♭♯]?(?:III|II|IV|VII|VI|V|I|iii|ii|iv|vii|vi|v|i)(?:M|m|dim|aug|add|sus|maj|min)?[0-9]*(?:/[1-7A-G#♭♯b])?)\b',
        content
    )
    if standalone:
        return standalone.group(1).strip()
    
    return None

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
        "chord_bass_melody": extract_chord_bass_melody(content),
        
        "type": extract_type(content),
        "start_measure": extract_start_measure(content),
        "end_measure": extract_end_measure(content),
        "roman_numeral": extract_roman_numeral(content),
        "absolute_root": extract_absolute_root(content),
        "inversion": extract_inversion(content),
        "chord_progression": extract_chord_progression(content)
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
                        "chord_complexity", "melodic_complexity", "trend_probability", "chord_melody_tension", "chord_progression_novelty", "chord_bass_melody",
                        "type", "start_measure", "end_measure", "roman_numeral", "absolute_root", "inversion", "chord_progression"]
    
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