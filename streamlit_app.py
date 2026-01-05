
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dataframe_functions import prepare_data
import code_visualization as cv

# --- Page Configuration ---
st.set_page_config(
    page_title="HookTheory Music Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Options / Styles ---
# Clean, Modern, Minimalist Light Theme
st.markdown("""
<style>
    /* Main Background - Clean White/Off-White */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* Sidebar - Subtle Light Grey */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    /* Headers - Dark distinctive sans-serif */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1a1a1a;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Metric Cards - Modern Card Style */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-color: #dee2e6;
    }
    div[data-testid="metric-label"] {
        color: #6c757d;
        font-weight: 500;
    }
    div[data-testid="metric-value"] {
        color: #212529;
        font-weight: 700;
    }
    
    /* Plotly Background (Transparent) */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
    
    /* Buttons - Modern Primary (Indigo/Purple) */
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #4338ca;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def get_data():
    df = prepare_data("hooktheory_songs.csv")
    return df

try:
    df = get_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

if df is None or df.empty:
    st.warning("No data found in hooktheory_songs.csv")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🎛️ Filters")

# 1. Title Search
all_titles = sorted(df['title'].dropna().unique().tolist())
search_title = st.sidebar.multiselect("Filter Titles", options=all_titles)

# 2. Artist Filter
all_artists = sorted(df['artist'].dropna().unique().tolist())
selected_artists = st.sidebar.multiselect("Filter Artists", options=all_artists)

# 3. Genre Filter
all_genres = sorted(df['genre'].dropna().unique().tolist())
if "Unknown" in all_genres:
    all_genres.remove("Unknown")
    all_genres.append("Unknown")
    
# selected_genres = st.sidebar.multiselect(
#     "Filter Genres",
#     options=all_genres
# )

# 4. Key Tonic Filter
all_keys = sorted(df['key_tonic'].dropna().unique().tolist())
selected_keys = st.sidebar.multiselect("Filter Keys", options=all_keys)

# 5. Mode Filter
all_modes = sorted(df['mode'].dropna().unique().tolist())
selected_modes = st.sidebar.multiselect("Filter Modes", options=all_modes)

# 6. BPM Filter
# valid_bpm = df['bpm'].dropna()
# if not valid_bpm.empty:
#     min_bpm = int(valid_bpm.min())
#     max_bpm = int(valid_bpm.max())
#     if min_bpm == max_bpm:
#         max_bpm += 1
#     bpm_range = st.sidebar.slider("BPM Range", min_value=min_bpm, max_value=max_bpm, value=(min_bpm, max_bpm))
# else:
#     bpm_range = None
#     st.sidebar.info("BPM data unavailable")

# --- Apply Filters ---
filtered_df = df.copy()

if search_title:
    filtered_df = filtered_df[filtered_df['title'].str.contains(search_title, case=False, na=False)]

if selected_artists:
    filtered_df = filtered_df[filtered_df['artist'].isin(selected_artists)]

# if selected_genres:
#     filtered_df = filtered_df[filtered_df['genre'].isin(selected_genres)]

if selected_keys:
    filtered_df = filtered_df[filtered_df['key_tonic'].isin(selected_keys)]

if selected_modes:
    filtered_df = filtered_df[filtered_df['mode'].isin(selected_modes)]

# if bpm_range:
#     # Only filter if the user has actually adjusted the sliders
#     # This prevents dropping rows with NaN BPMs when the filter is at default settings
#     is_default_range = (bpm_range[0] == min_bpm) and (bpm_range[1] == max_bpm)
#     if not is_default_range:
#         filtered_df = filtered_df[
#             (filtered_df['bpm'] >= bpm_range[0]) & 
#             (filtered_df['bpm'] <= bpm_range[1])
#         ]

st.title("🎵 HookTheory Advanced Analytics")
st.markdown("Deep dive into the structural DNA of popular music.")

# Define metrics list
metrics_list = [
    'chord_complexity', 'melodic_complexity', 
    'chord_melody_tension', 'chord_progression_novelty', 
    'chord_bass_melody'
]

# Ensure numeric columns are strictly numeric/filled for plotting
plot_df = filtered_df.copy()
for col in metrics_list:
    if col in plot_df.columns:
        plot_df[col] = pd.to_numeric(plot_df[col], errors='coerce').fillna(0)


# --- MODULE A: The Tonal Landscape ---
st.header("Module A: The Tonal Landscape")
st.markdown("""
**The Harmonic Foundation:**  
This module explores the fundamental building blocks of the music library—Keys and Modes. 
By analyzing these tonal centers, we can understand the "emotional baseline" of the dataset. 
Major keys often correlate with brighter, happier sounds, while Minor keys tend to be darker or more melancholic.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Hierarchical Tonal Sunburst")
    st.caption("""
    **Visual Guide**: The inner ring represents the **Key** (e.g., C, G), and the outer ring shows the **Mode** (Major/Minor).
    **Insight**: Larger slices indicate dominant tonal families. Use this to see if the library leans towards specific root notes.
    """)
    fig1 = cv.plot_sunburst_tonal_hierarchy(plot_df)
    if fig1: st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("2. Circle of Fifths Density")
    st.caption("""
    **Visual Guide**: Songs are mapped around the musical **Circle of Fifths**. 
    **Insight**: Clusters indicate preferred harmonic regions. A skew towards the right (G, D, A) suggests 'sharp' keys, while the left (F, Bb, Eb) suggests 'flat' keys.
    """)
    fig2 = cv.plot_polar_circle_of_fifths(plot_df)
    if fig2: st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("3. Modal Distribution")
    st.caption("""
    **Visual Guide**: The ratio of Major vs. Minor compositions.
    **Insight**: A basic proxy for the library's mood. A 50/50 split indicates emotional balance.
    """)
    fig3 = cv.plot_modal_donut(plot_df)
    if fig3: st.plotly_chart(fig3, use_container_width=True)
    
with col4:
    st.subheader("4. Key Signature Complexity")
    st.caption("""
    **Visual Guide**: Box plot showing the spread of **Chord Complexity** for each key.
    **Insight**: Do "harder" keys (with many sharps/flats like F#) result in more complex or simpler songs? 
    """)
    fig4 = cv.plot_key_complexity_box(plot_df)
    if fig4: st.plotly_chart(fig4, use_container_width=True)


# --- MODULE B: Metric Signatures ---
st.header("Module B: Metric Signatures")
st.markdown("""
**Feature Analysis:**  
Here we dissect specific musical traits. `Chord Complexity` measures harmonic sophistication (jazziness), 
while `Tension` measures dissonance. These "DNA markers" help fingerprint a song's uniqueness.
""")

# Select a song for focused analysis
song_options = plot_df['title'].unique()
selected_song = st.selectbox("Select a Song for DNA Analysis", options=song_options, index=0 if len(song_options) > 0 else None)

col5, col6 = st.columns(2)

with col5:
    st.subheader("5. Song DNA Radar")
    if selected_song:
        st.info(f"**Analyzing: {selected_song}**")
        st.caption("""
        **Visual Guide**: Blue Shape = Selected Song. Grey Dashed Line = Library Average.
        **Insight**: Spikes extending outward reveal the song's standout traits compared to the average.
        """)
        fig5 = cv.plot_song_dna_radar(plot_df, selected_song, metrics_list)
        if fig5: st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("7. Tension vs Resolution")
    st.caption("""
    **Visual Guide**: Scatter plot of **Harmoic Complexity** (X) vs **Musical Tension** (Y).
    **Insight**: High-Tension/High-Complexity (Top-Right) usually indicates Jazz/Fusion. Low-Tension/Low-Complexity (Bottom-Left) is typical for basic Pop/Folk.
    """)
    fig7 = cv.plot_tension_vs_resolution(plot_df)
    if fig7: st.plotly_chart(fig7, use_container_width=True)

st.subheader("6. Global Metric Distributions")
if selected_song:
    st.caption(f"""
    **Visual Guide**: Histograms showing the distribution of all songs. The **Blue Line** marks where *{selected_song}* falls.
    **Insight**: Is this song an outlier or does it sit safely in the middle of the pack?
    """)
    fig6 = cv.plot_global_metric_histograms(plot_df, selected_song, metrics_list)
    if fig6: st.plotly_chart(fig6, use_container_width=True)

st.subheader("8. Bass Line Independence (Top Artists)")
st.caption("""
**Visual Guide**: A ridge plot showing how often the bass note deviates from the root of the chord.
**Insight**: Wider distributions indicate artists who use more inversions and complex slash-chords (e.g., C/G), showing mastery of voice leading.
""")
fig8 = cv.plot_bass_line_ridge(plot_df)
if fig8: st.plotly_chart(fig8, use_container_width=True)


# --- MODULE C: Comparative Musicology ---
st.header("Module C: Comparative Musicology")
st.markdown("""
**Direct Comparison:**  
Compare songs and artists head-to-head. Identify what defines a specific artist's "Sound Signature" 
and how musical ideas flow through different structural categories.
""")

col_c1, col_c2 = st.columns(2)
with col_c1:
    st.subheader("9. Song Face-Off")
    if len(song_options) >= 2:
        s1 = st.selectbox("Song 1", options=song_options, index=0, key='sf1')
        s2 = st.selectbox("Song 2", options=song_options, index=1, key='sf2')
        st.caption("""
        **Visual Guide**: Dumbbell plot. The line connects the two songs' values for each metric.
        **Insight**: Long lines represent major differences in style. Short lines mean the songs are structural siblings.
        """)
        fig9 = cv.plot_face_off_dumbbell(plot_df, s1, s2, metrics_list)
        if fig9: st.plotly_chart(fig9, use_container_width=True)
    else:
        st.info("Need at least 2 songs for comparison.")

with col_c2:
    st.subheader("11. Metric Deviation (Uniqueness)")
    if selected_song:
        st.caption(f"""
        **Visual Guide**: Bars show deviation from the mean (0).
        **Insight**: What makes *{selected_song}* unique? Pink bars > Average, Blue bars < Average. 
        """)
        fig11 = cv.plot_diverging_metric_deviation(plot_df, selected_song, metrics_list)
        if fig11: st.plotly_chart(fig11, use_container_width=True)

st.subheader("10. Artist Complexity Evolution")
st.caption("""
**Visual Guide**: Artists plotted by average Chord Complexity (X) vs Melodic Complexity (Y). Bubble size = Number of songs.
**Insight**: Who are the "Complex" artists? (Top-Right). Who helps define the "Pop Standard"? (Bottom-Left).
""")
fig10 = cv.plot_artist_complexity_evolution(plot_df)
if fig10: st.plotly_chart(fig10, use_container_width=True)

st.subheader("12. The Flow of Music (Parallel Categories)")
st.caption("""
**Visual Guide**: Flow diagram connecting Mode -> Key -> Complexity Tier. Thicker paths = typical musical formulas.
**Insight**: Traces the most common "recipes" for a song. E.g., Do Minor keys usually lead to High Complexity?
""")
fig12 = cv.plot_parallel_categories_flow(plot_df)
if fig12: st.plotly_chart(fig12, use_container_width=True)


# --- MODULE D: Correlation & Causality ---
st.header("Module D: Correlation & Causality")
st.markdown("""
**Interactions & Patterns:**  
How do different musical metrics influence each other? Does high complexity force a trade-off in other areas? 
These views uncover the hidden mathematical relationships in the music.
""")

st.subheader("13. Trade-Off Visualizer (Parallel Coordinates)")
st.caption("""
**Visual Guide**: Each line is a song. Follow the lines across axes to see correlations.
**Insight**: Look for "Scissors" (lines crossing efficiently) which indicate inverse relationships.
""")
fig13 = cv.plot_parallel_coordinates(plot_df, metrics_list)
if fig13: st.plotly_chart(fig13, use_container_width=True)

col_d1, col_d2 = st.columns(2)
with col_d1:
    st.subheader("14. Correlation Matrix")
    st.caption("""
    **Visual Guide**: Heatmap. Red = Positive Correlation (move together). Blue = Negative Correlation (opposites).
    **Insight**: Which metrics are effectively the same thing? (Dark Red). Which are sworn enemies? (Dark Blue).
    """)
    fig14 = cv.plot_correlation_heatmap(plot_df, metrics_list)
    if fig14: st.plotly_chart(fig14, use_container_width=True)
    
with col_d2:
    st.subheader("16. Topography of Genre (Density)")
    st.caption("""
    **Visual Guide**: A topological map of musical density. Contours show where songs cluster.
    **Insight**: Peaks represent the "Standard Sound"—the most common combination of Melody and Chord complexity.
    """)
    fig16 = cv.plot_density_contour_topography(plot_df)
    if fig16: st.plotly_chart(fig16, use_container_width=True)

st.subheader("15. Compositional Focus Ternary Plot")
st.caption("""
**Visual Guide**: A triangular plot balancing three metrics.
**Insight**: Songs near a corner are "specialists" in that trait. Songs in the center are "generalists".
""")
fig15 = cv.plot_ternary_composition_focus(plot_df)
if fig15: st.plotly_chart(fig15, use_container_width=True)


# --- MODULE E: High-Dimensional Discovery ---
st.header("Module E: High-Dimensional Discovery")
st.markdown("""
**AI and Clustering:**  
Using machine learning (PCA and K-Means), we crush multidimensional data into visible 2D/3D space 
to find hidden clusters of similar songs that might not share a genre but share a "vibe."
""")

col_e1, col_e2 = st.columns(2)

with col_e1:
    st.subheader("17. Complexity Cube (3D)")
    st.caption("""
    **Visual Guide**: A 3D scatter plot. Click and drag to rotate.
    **Insight**: Reveals data structures that are invisible in 2D. Look for distinct clouds of floating points.
    """)
    fig17 = cv.plot_3d_complexity_cube(plot_df)
    if fig17: st.plotly_chart(fig17, use_container_width=True)

with col_e2:
    st.subheader("18. PCA Cluster Map")
    st.caption("""
    **Visual Guide**: Songs grouped by mathematical similarity, not human labels.
    **Insight**: The most powerful view. Songs in the same color cluster are "mathematical cousins" regardless of Genre.
    """)
    fig18 = cv.plot_pca_cluster_map(plot_df, metrics_list)
    if fig18: st.plotly_chart(fig18, use_container_width=True)

st.subheader("19. Animated Complexity Evolution")
st.caption("""
**Visual Guide**: **Press Play**. Watch how the song distribution shifts as we move from simple to complex songs.
**Insight**: See if higher complexity makes songs more erratic (high Novelty) or if they stay structured.
""")
fig19 = cv.plot_animated_complexity_bubble(plot_df)
if fig19: st.plotly_chart(fig19, use_container_width=True)


