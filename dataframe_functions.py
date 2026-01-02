
import pandas as pd
import numpy as np

def load_data(file_path):
    """
    Loads the dataset from a CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def clean_key_tonic(df):
    """
    Cleans the 'key_tonic' column by handling unicode characters and standardization.
    The console output suggested issues with unicode like \u266f (sharp).
    We will map common musical symbols to ASCII representations for easier handling if needed,
    or ensure they are properly treated as strings.
    """
    if 'key_tonic' not in df.columns:
        return df

    # Replace None/NaN with "Unknown"
    df['key_tonic'] = df['key_tonic'].fillna('Unknown')
    
    # Map unicode sharp/flat if they exist
    # \u266f is '♯' (sharp)
    # \u266d is '♭' (flat)
    
    def normalize_note(note):
        if not isinstance(note, str):
            return str(note)
        
        # Replace unicode symbols with text equivalents if desired for consistency
        # Or just strip garbage if the previous view showed "G?T?" type corruption
        # Based on "GT", it might be that the file encoding is utf-8 but read as cp1252 or vice versa.
        # However, purely within python, if read correctly, it should work.
        
        note = note.replace('\u266f', '#').replace('\u266d', 'b')
        return note.strip()

    df['key_tonic'] = df['key_tonic'].apply(normalize_note)
    return df

def process_numeric_columns(df):
    """
    Ensures that numeric columns are actually numeric.
    """
    numeric_cols = [
        'bpm', 'chord_complexity', 'melodic_complexity', 
        'chord_melody_tension', 'chord_progression_novelty', 
        'chord_bass_melody'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            # Coerce errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Fill NaN? 
            # For complexity metrics, maybe fill with mean or 0? 
            # Let's fill with 0 for now or leave as NaN if we want to exclude from plots
            # But dashboards usually prefer cleaner data.
            # let's fill BPM with mean? No, BPM is specific.
    
    return df

def clean_genre(df):
    """
    Cleans the genre column.
    """
    if 'genre' in df.columns:
        df['genre'] = df['genre'].fillna('Unknown')
    return df

def prepare_data(file_path):
    """
    Orchestration function to load and clean data.
    """
    df = load_data(file_path)
    if df is not None:
        df = clean_key_tonic(df)
        if 'trend_probability' in df.columns:
            df = df.drop(columns=['trend_probability'])
        df = process_numeric_columns(df)
        df = clean_genre(df)
        
        # Additional feature engineering if needed for dashboard
        # e.g. Categorizing complexity
        if 'chord_complexity' in df.columns:
            df['complexity_tier'] = pd.cut(
                df['chord_complexity'], 
                bins=[0, 33, 66, 100], 
                labels=['Low', 'Medium', 'High']
            )
            
    return df

if __name__ == "__main__":
    # Test run
    df = prepare_data("hooktheory_songs.csv")
    print(df.head())
    print(df.info())
    print(df['genre'].head())
