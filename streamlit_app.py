
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
search_title = st.sidebar.text_input("Search Title", placeholder="e.g. Bohemian Rhapsody")

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
valid_bpm = df['bpm'].dropna()
if not valid_bpm.empty:
    min_bpm = int(valid_bpm.min())
    max_bpm = int(valid_bpm.max())
    if min_bpm == max_bpm:
        max_bpm += 1
    bpm_range = st.sidebar.slider("BPM Range", min_value=min_bpm, max_value=max_bpm, value=(min_bpm, max_bpm))
else:
    bpm_range = None
    st.sidebar.info("BPM data unavailable")

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

if bpm_range:
    # Only filter if the user has actually adjusted the sliders
    # This prevents dropping rows with NaN BPMs when the filter is at default settings
    is_default_range = (bpm_range[0] == min_bpm) and (bpm_range[1] == max_bpm)
    if not is_default_range:
        filtered_df = filtered_df[
            (filtered_df['bpm'] >= bpm_range[0]) & 
            (filtered_df['bpm'] <= bpm_range[1])
        ]

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
st.markdown("Understanding keys, modes, and their relationships.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Hierarchical Tonal Sunburst")
    fig1 = cv.plot_sunburst_tonal_hierarchy(plot_df)
    if fig1: st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("2. Circle of Fifths Density")
    fig2 = cv.plot_polar_circle_of_fifths(plot_df)
    if fig2: st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("3. Modal Distribution")
    fig3 = cv.plot_modal_donut(plot_df)
    if fig3: st.plotly_chart(fig3, use_container_width=True)
    
with col4:
    st.subheader("4. Key Signature Complexity")
    fig4 = cv.plot_key_complexity_box(plot_df)
    if fig4: st.plotly_chart(fig4, use_container_width=True)


# --- MODULE B: Metric Signatures ---
st.header("Module B: Metric Signatures")
st.markdown("Dissecting specific song attributes.")

# Select a song for focused analysis
song_options = plot_df['title'].unique()
selected_song = st.selectbox("Select a Song for DNA Analysis", options=song_options, index=0 if len(song_options) > 0 else None)

col5, col6 = st.columns(2)

with col5:
    st.subheader("5. Song DNA Radar")
    if selected_song:
        fig5 = cv.plot_song_dna_radar(plot_df, selected_song, metrics_list)
        if fig5: st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("7. Tension vs Resolution")
    fig7 = cv.plot_tension_vs_resolution(plot_df)
    if fig7: st.plotly_chart(fig7, use_container_width=True)

st.subheader("6. Global Metric Distributions")
if selected_song:
    fig6 = cv.plot_global_metric_histograms(plot_df, selected_song, metrics_list)
    if fig6: st.plotly_chart(fig6, use_container_width=True)

st.subheader("8. Bass Line Independence (Top Artists)")
fig8 = cv.plot_bass_line_ridge(plot_df)
if fig8: st.plotly_chart(fig8, use_container_width=True)


# --- MODULE C: Comparative Musicology ---
st.header("Module C: Comparative Musicology")

col_c1, col_c2 = st.columns(2)
with col_c1:
    st.subheader("9. Song Face-Off")
    if len(song_options) >= 2:
        s1 = st.selectbox("Song 1", options=song_options, index=0, key='sf1')
        s2 = st.selectbox("Song 2", options=song_options, index=1, key='sf2')
        fig9 = cv.plot_face_off_dumbbell(plot_df, s1, s2, metrics_list)
        if fig9: st.plotly_chart(fig9, use_container_width=True)
    else:
        st.info("Need at least 2 songs for comparison.")

with col_c2:
    st.subheader("11. Metric Deviation (Uniqueness)")
    if selected_song:
        fig11 = cv.plot_diverging_metric_deviation(plot_df, selected_song, metrics_list)
        if fig11: st.plotly_chart(fig11, use_container_width=True)

st.subheader("10. Artist Complexity Evolution")
fig10 = cv.plot_artist_complexity_evolution(plot_df)
if fig10: st.plotly_chart(fig10, use_container_width=True)

st.subheader("12. The Flow of Music (Parallel Categories)")
fig12 = cv.plot_parallel_categories_flow(plot_df)
if fig12: st.plotly_chart(fig12, use_container_width=True)


# --- MODULE D: Correlation & Causality ---
st.header("Module D: Correlation & Causality")

st.subheader("13. Trade-Off Visualizer (Parallel Coordinates)")
fig13 = cv.plot_parallel_coordinates(plot_df, metrics_list)
if fig13: st.plotly_chart(fig13, use_container_width=True)

col_d1, col_d2 = st.columns(2)
with col_d1:
    st.subheader("14. Correlation Matrix")
    fig14 = cv.plot_correlation_heatmap(plot_df, metrics_list)
    if fig14: st.plotly_chart(fig14, use_container_width=True)
    
with col_d2:
    st.subheader("16. Topography of Genre (Density)")
    fig16 = cv.plot_density_contour_topography(plot_df)
    if fig16: st.plotly_chart(fig16, use_container_width=True)

st.subheader("15. Compositional Focus Ternary Plot")
fig15 = cv.plot_ternary_composition_focus(plot_df)
if fig15: st.plotly_chart(fig15, use_container_width=True)


# --- MODULE E: High-Dimensional Discovery ---
st.header("Module E: High-Dimensional Discovery")

col_e1, col_e2 = st.columns(2)

with col_e1:
    st.subheader("17. Complexity Cube (3D)")
    fig17 = cv.plot_3d_complexity_cube(plot_df)
    if fig17: st.plotly_chart(fig17, use_container_width=True)

with col_e2:
    st.subheader("18. PCA Cluster Map")
    fig18 = cv.plot_pca_cluster_map(plot_df, metrics_list)
    if fig18: st.plotly_chart(fig18, use_container_width=True)

st.subheader("19. Animated Complexity Evolution")
fig19 = cv.plot_animated_complexity_bubble(plot_df)
if fig19: st.plotly_chart(fig19, use_container_width=True)


