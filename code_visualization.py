
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# --- Helper Functions ---

def get_circle_of_fifths_angle(key_tonic):
    """
    Maps a Key Tonic to an angle on the Circle of Fifths.
    C = 0, G = 30, D = 60 ... F = 330
    """
    if not key_tonic or not isinstance(key_tonic, str):
        return None
    
    circle_order = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F']
    enharmonics = {'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb', 'Cb': 'B'}
    
    key = key_tonic.replace(' Major', '').replace(' Minor', '').strip()
    key = enharmonics.get(key, key)
    
    try:
        index = circle_order.index(key)
        return index * 30
    except ValueError:
        return None

def apply_chart_style(fig, title=None):
    """Applies a consistent simple/modern LIGHT style to all plots."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        modebar=dict(bgcolor='rgba(0,0,0,0)', color='#64748b'),
        font=dict(family="Inter, sans-serif"),
        title=dict(text=title, font=dict(size=20, weight='bold')) if title else None,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', linecolor='rgba(128, 128, 128, 0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', linecolor='rgba(128, 128, 128, 0.2)')
    )
    return fig

# --- Module A: The Tonal Landscape ---

def plot_sunburst_tonal_hierarchy(df):
    if 'mode' not in df.columns or 'key_tonic' not in df.columns:
        return None
    plot_df = df.dropna(subset=['mode', 'key_tonic'])
    
    # Modern Palette: Major (Warm/Orange), Minor (Cool/Indigo) - slightly more pastel for light mode
    color_map = {'Major': '#f59e0b', 'Minor': '#6366f1', 'Unknown': '#94a3b8'}
    
    fig = px.sunburst(
        plot_df,
        path=['mode', 'key_tonic'],
        color='mode',
        color_discrete_map=color_map
    )
    return apply_chart_style(fig, "Hierarchical Tonal Sunburst")

def plot_polar_circle_of_fifths(df):
    if 'key_tonic' not in df.columns:
        return None
    df = df.copy()
    df['theta'] = df['key_tonic'].apply(get_circle_of_fifths_angle)
    df = df.dropna(subset=['theta'])
    agg_df = df.groupby(['key_tonic', 'theta', 'mode']).size().reset_index(name='count')
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=agg_df['count'],
        theta=agg_df['theta'],
        mode='markers',
        marker=dict(
            size=agg_df['count'] * 3, 
            color=agg_df['mode'].map({'Major': '#f59e0b', 'Minor': '#6366f1', 'Unknown': '#94a3b8'}),
            line=dict(color='white', width=1),
            opacity=0.8
        ),
        text=agg_df['key_tonic'],
        hovertemplate='<b>%{text}</b><br>Count: %{r}<extra></extra>'
    ))
    
    fig = apply_chart_style(fig, "Circle of Fifths Density")
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showline=False, gridcolor='#e2e8f0'),
            angularaxis=dict(
                tickmode='array',
                tickvals=[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
                ticktext=['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F'],
                gridcolor='#e2e8f0'
            ),
            bgcolor='rgba(255,255,255,0.5)'
        )
    )
    return fig

def plot_modal_donut(df):
    if 'mode' not in df.columns:
        return None
    counts = df['mode'].value_counts().reset_index()
    counts.columns = ['mode', 'count']
    
    color_map = {'Major': '#f59e0b', 'Minor': '#6366f1', 'Unknown': '#94a3b8'}
    
    fig = px.pie(
        counts, values='count', names='mode',
        hole=0.6,
        color='mode', color_discrete_map=color_map
    )
    fig.update_traces(textinfo='percent', hoverinfo='label+value', marker=dict(line=dict(color='#ffffff', width=2)))
    fig.add_annotation(text=f"{len(df)}<br>Songs", showarrow=False, font=dict(size=14, color='#1e293b'))
    return apply_chart_style(fig, "Modal Distribution")

def plot_key_complexity_box(df):
    if 'key_tonic' not in df.columns or 'chord_complexity' not in df.columns:
        return None
    circle_order = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F']
    
    fig = px.box(
        df, x='key_tonic', y='chord_complexity',
        points="all",
        category_orders={"key_tonic": circle_order},
        color='mode',
        color_discrete_map={'Major': '#f59e0b', 'Minor': '#6366f1'}
    )
    fig.update_traces(marker=dict(size=3, opacity=0.6))
    return apply_chart_style(fig, "Key Signature Complexity")

# --- Module B: Metric Signatures ---

def plot_song_dna_radar(df, song_title, metrics):
    song_row = df[df['title'] == song_title]
    if song_row.empty: return None
        
    avg_metrics = df[metrics].mean().tolist()
    song_metrics = song_row.iloc[0][metrics].tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=avg_metrics, theta=metrics, fill='toself', name='Average',
        line=dict(color='#94a3b8', dash='dash', width=1),
        marker=dict(size=0),
        fillcolor='rgba(148, 163, 184, 0.2)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=song_metrics, theta=metrics, fill='toself', name=song_title,
        line=dict(color='#0ea5e9', width=2), # Sky-500
        fillcolor='rgba(14, 165, 233, 0.2)'
    ))
    
    fig = apply_chart_style(fig, f"DNA: {song_title}")
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#e2e8f0', showticklabels=False), bgcolor='rgba(0,0,0,0)'))
    return fig

def plot_global_metric_histograms(df, song_title, metrics):
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=len(metrics), subplot_titles=[m.replace('_', ' ').title() for m in metrics])
    song_row = df[df['title'] == song_title]
    
    for i, metric in enumerate(metrics):
        fig.add_trace(
            go.Histogram(x=df[metric], name=metric, nbinsx=15, marker_color='#94a3b8'),
            row=1, col=i+1
        )
        if not song_row.empty:
            val = song_row.iloc[0][metric]
            fig.add_vline(x=val, line_width=2, line_color="#0ea5e9", row=1, col=i+1)
            
    fig = apply_chart_style(fig, "Global Metric Distributions")
    fig.update_layout(showlegend=False, bargap=0.1)
    return fig

def plot_tension_vs_resolution(df):
    if 'chord_complexity' not in df.columns or 'chord_melody_tension' not in df.columns: return None
    fig = px.scatter(
        df, x='chord_complexity', y='chord_melody_tension',
        color='mode', color_discrete_map={'Major': '#f59e0b', 'Minor': '#6366f1'},
        hover_data=['title', 'artist'], opacity=0.8
    )
    return apply_chart_style(fig, "Tension vs. Resolution")

def plot_bass_line_ridge(df):
    if 'chord_bass_melody' not in df.columns or 'artist' not in df.columns: return None
    top_artists = df['artist'].value_counts().nlargest(10).index.tolist()
    filtered = df[df['artist'].isin(top_artists)]
    
    fig = go.Figure()
    for i, artist in enumerate(top_artists):
        artist_data = filtered[filtered['artist'] == artist]['chord_bass_melody']
        fig.add_trace(go.Violin(
            x=artist_data, name=artist, side='positive', orientation='h', width=3, points=False,
            line_color=px.colors.qualitative.Prism[i % len(px.colors.qualitative.Prism)]
        ))
    
    fig = apply_chart_style(fig, "Bass Line Independence")
    fig.update_layout(violinmode='overlay', yaxis_showgrid=False)
    return fig

# --- Module C: Comparative Musicology ---

def plot_face_off_dumbbell(df, song1, song2, metrics):
    s1 = df[df['title'] == song1][metrics].iloc[0]
    s2 = df[df['title'] == song2][metrics].iloc[0]
    
    fig = go.Figure()
    for metric in metrics:
        fig.add_trace(go.Scatter(
            x=[s1[metric], s2[metric]], y=[metric, metric],
            mode='lines', line=dict(color='#cbd5e1', width=2), showlegend=False
        ))
    
    fig.add_trace(go.Scatter(
        x=s1.values, y=metrics, mode='markers', name=song1,
        marker=dict(color='#0ea5e9', size=12, symbol='circle')
    ))
    fig.add_trace(go.Scatter(
        x=s2.values, y=metrics, mode='markers', name=song2,
        marker=dict(color='#ec4899', size=12, symbol='circle')
    ))
    
    return apply_chart_style(fig, f"Compare: {song1} vs {song2}")

def plot_artist_complexity_evolution(df):
    if 'chord_complexity' not in df.columns: return None
    agg = df.groupby('artist').agg({
        'chord_complexity': 'mean', 'melodic_complexity': 'mean', 'title': 'count'
    }).reset_index()
    agg = agg[agg['title'] > 1]
    
    fig = px.scatter(
        agg, x='chord_complexity', y='melodic_complexity', size='title',
        text='artist', hover_name='artist',
        color_discrete_sequence=['#64748b']
    )
    fig.update_traces(textposition='top center', marker=dict(opacity=0.7, color='#64748b'))
    return apply_chart_style(fig, "Artist Complexity Evolution")

def plot_diverging_metric_deviation(df, song_title, metrics):
    df_z = df[metrics].apply(lambda x: (x - x.mean()) / x.std())
    song_z = df_z.loc[df['title'] == song_title].iloc[0]
    
    colors = ['#ec4899' if x >= 0 else '#0ea5e9' for x in song_z.values]
    
    fig = go.Figure(go.Bar(
        x=song_z.values, y=metrics, orientation='h',
        marker_color=colors
    ))
    return apply_chart_style(fig, f"Metric Deviation: {song_title}")

def plot_parallel_categories_flow(df):
    required = ['mode', 'key_tonic', 'complexity_tier']
    if any(col not in df.columns for col in required): return None
    fig = px.parallel_categories(
        df, dimensions=['mode', 'key_tonic', 'complexity_tier'],
        color='chord_complexity' if 'chord_complexity' in df.columns else None,
        color_continuous_scale=px.colors.sequential.Bluered
    )
    return apply_chart_style(fig, "Structural Flow")

# --- Module D: Correlation & Causality ---

def plot_parallel_coordinates(df, metrics):
    plot_df = df.copy()
    plot_df['key_code'] = plot_df['key_tonic'].astype('category').cat.codes
    dims = metrics + ['key_code']
    
    fig = px.parallel_coordinates(
        plot_df, dimensions=dims, color='chord_complexity',
        color_continuous_scale=px.colors.diverging.Spectral
    )
    return apply_chart_style(fig, "Metric Trade-Offs")

def plot_correlation_heatmap(df, metrics):
    corr = df[metrics].corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        color_continuous_scale='RdBu_r', zmin=-1, zmax=1
    )
    return apply_chart_style(fig, "Correlation Matrix")

def plot_ternary_composition_focus(df):
    if 'melodic_complexity' not in df.columns: return None
    fig = px.scatter_ternary(
        df, a='melodic_complexity', b='chord_complexity', c='chord_progression_novelty',
        hover_name='title', color='genre', color_discrete_sequence=px.colors.qualitative.Prism
    )
    return apply_chart_style(fig, "Compositional Focus")

def plot_density_contour_topography(df):
    if 'chord_complexity' not in df.columns: return None
    fig = px.density_contour(
        df, x='chord_complexity', y='melodic_complexity',
        marginal_x="histogram", marginal_y="histogram"
    )
    return apply_chart_style(fig, "Genre Topography")

# --- Module E: High-Dimensional Discovery ---

def plot_3d_complexity_cube(df):
    if 'chord_complexity' not in df.columns: return None
    fig = px.scatter_3d(
        df, x='chord_complexity', y='melodic_complexity', z='chord_melody_tension',
        color='mode', color_discrete_map={'Major': '#f59e0b', 'Minor': '#6366f1'},
        hover_data=['title', 'artist'], opacity=0.8
    )
    return apply_chart_style(fig, "Complexity Cube (3D)")

def plot_pca_cluster_map(df, metrics):
    data = df[metrics].fillna(df[metrics].mean())
    scaler = StandardScaler()
    scaled = scaler.fit_transform(data)
    
    pca = PCA(n_components=2)
    components = pca.fit_transform(scaled)
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(scaled)
    
    res = df.copy()
    res['PC1'], res['PC2'] = components[:, 0], components[:, 1]
    res['Cluster'] = clusters.astype(str)
    
    fig = px.scatter(
        res, x='PC1', y='PC2', color='Cluster',
        hover_data=['title', 'artist'],
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    return apply_chart_style(fig, "PCA Cluster Map")

def plot_animated_complexity_bubble(df):
    if 'chord_complexity' not in df.columns: return None
    df_anim = df.copy()
    df_anim['complexity_bin'] = pd.cut(df_anim['chord_complexity'], bins=range(0, 110, 10), labels=[str(i) for i in range(0, 100, 10)])
    df_anim = df_anim.sort_values('complexity_bin')
    
    fig = px.scatter(
        df_anim, x='chord_melody_tension', y='chord_progression_novelty',
        animation_frame='complexity_bin', animation_group='title',
        color='mode', color_discrete_map={'Major': '#f59e0b', 'Minor': '#6366f1'},
        hover_name='title', range_x=[0, 100], range_y=[0, 100]
    )
    return apply_chart_style(fig, "Evolution (Animated)")

def plot_trend_probability_heatmap(df):
    if 'trend_probability' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Trend Probability metric not available", showarrow=False, font=dict(color="#1e293b"))
        return apply_chart_style(fig, "Trend Probability (N/A)")
    
    df['comp_bin'] = pd.cut(df['chord_complexity'], bins=10)
    df['mel_bin'] = pd.cut(df['melodic_complexity'], bins=10)
    pivot = df.pivot_table(index='mel_bin', columns='comp_bin', values='trend_probability', aggfunc='mean')
    
    fig = px.imshow(pivot, origin='lower', color_continuous_scale="Purples")
    return apply_chart_style(fig, "Trend Probability Heatmap")
