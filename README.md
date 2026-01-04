# 🎵 Music Hook Theory Analytics
### Decrypting the Structural DNA of Popular Music

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## 📋 Executive Summary
**Music Hook Theory Analytics** is a full-stack data science project that explores the hidden mathematical relationships in popular music. By scraping and analyzing data from HookTheory, this project quantifies abstract musical concepts—such as "tension," "complexity," and "novelty"—to visualize what makes a hit song work.

This repository demonstrates an end-to-end **Data Analyst** workflow: from **ETL** (extracting data via custom scraping) to **Feature Engineering** (calculating music theory metrics) and **Interactive Visualization** (a deployed Streamlit dashboard).

---

## 🚀 Key Theoretical Contributions
To translate art into data, I engineered several novel metrics:
- **🌀 Tonal Tension (Spiral Array)**: Implemented a simplified Spiral Array model to calculate the mathematical "distance" (tensile strain) of a chord from its tonic center.
- **🧬 Song DNA Radar**: A multi-dimensional fingerprint for every song, aggregating complexity, tension, and novelty scores.
- **📊 Complexity Clustering**: Utilized **PCA (Principal Component Analysis)** and **K-Means Clustering** to group artists and genres based on compositional sophistication rather than just metadata tags.

---

## 🛠️ Technical Architecture

### 1. Data Pipeline (ETL)
*   **Extraction**: Custom-built web scraper (`hook_theory_api.py`) using `BeautifulSoup` and `requests` to harvest data from HookTheory's public pages.
*   **Transformation**:
    *   Cleaning inconsistent key signatures and normalizing unicode music symbols.
    *   Flattening nested JSON chord progressions into a relational database structure (Songs Table vs. Events Table).
*   **Loading**: processed data is stored in structured CSVs for dashboard consumption.

### 2. Analytical Engine
*   **Library**: `pandas`, `numpy`, `scikit-learn`
*   **Operations**:
    *   Statistical distributions of chord complexity.
    *   Correlation matrices to find relationships between "Melodic Complexity" and "Chord Novelty".
    *   3D Complexity Cubes for high-dimensional outlier detection.

### 3. Visualization Layer
*   **Framework**: `Streamlit` + `Plotly Express` / `Graph Objects`.
*   **Design Philosophy**: A "Day Light" aesthetic using a consistent color palette (Warm Amber for Major, Cool Indigo for Minor) to ensure accessibility and professional presentation.

---

## 📂 Repository Structure

```text
├── 📜 streamlit_app.py            # Main Dashboard entry point (The "View")
├── 📜 code_visualization.py       # Plotly visualization library (The "Presentation Logic")
├── 📜 hook_theory_api.py          # ETL Script & Scraper (The "Controller/Model")
├── 📜 dataframe_functions.py      # Data cleaning and utility functions
├── 📜 search_music_info.py        # NLP regex for text mining metadata
├── 📊 hooktheory_songs.csv       # Processed Dataset (Songs Metadata)
└── 📊 hooktheory_chords.csv      # Processed Dataset (Chord Events)
```

---

## 📊 Dashboard Preview

The dashboard maps music theory concepts to interactive data visuals:

| Module | Purpose | Visualization Type |
| :--- | :--- | :--- |
| **The Tonal Landscape** | Visualize the distribution of Keys and Modes | Sunburst Charts, Polar Plots |
| **Metric Signatures** | Deep dive into a single song's metrics | Radar Charts, Histograms |
| **Comparative Musicology** | Head-to-head song comparison | Dumbbell Charts, Diverging Bars |
| **High-Dimensional Discovery** | Finding clusters in complex data | 3D Scatter Plots, PCA Clusters |

---

## 💻 Installation & Usage

1.  **Clone the repository**
    ```bash
    git clone https://github.com/LuiisClaudio/music-hook-theory.git
    cd music-hook-theory
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the ETL Pipeline (Optional)**
    *Note: The repo comes with pre-populated data. Run this only to fetch new songs.*
    ```bash
    python hook_theory_api.py
    ```

4.  **Launch the Dashboard**
    ```bash
    streamlit run streamlit_app.py
    ```

---

## 🔮 Future Roadmap
- [ ] **Sentiment Analysis**: Correlate lyrical sentiment with major/minor tonality shifts.
- [ ] **Audio Feature Integration**: Merge with Spotify API to compare "Acousticness" vs. "Theoretical Complexity".
- [ ] **Predictive Modeling**: Train a Random Forest classifier to predict "Genre" based purely on chord progression metrics.

---

## 👤 Author
**Luis Claudio**
*Data Analyst | Portfolio Project*

*Designed to demonstrate proficiency in Python, Data Visualization, and converting unstructured data into actionable insights.*
