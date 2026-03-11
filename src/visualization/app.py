import streamlit as st
from pathlib import Path
import sys
import os

# --- PATH INJECTION BOOTSTRAP ---
# Robust path resolution to fix ModuleNotFoundError
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]  # Resolves to d:\supermarket-pipeline
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.visualization.components.styles import apply_nexus_styles
from src.visualization.components.loader import load_nexus_data
from src.config.settings import DATA_DIR

# --- NEXUS ARCHITECTURE BOOTSTRAP ---
st.set_page_config(
    page_title="Nexus Enterprise | Supermarket Intelligence",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_nexus_styles()

# Global Data Cache
df = load_nexus_data(DATA_DIR)
if df is None:
    st.error("📉 Nexus Offline: Data Match Engine required. Run matching pipeline.")
    st.stop()

# --- MULTI-PAGE NAVIGATION ---
# Note: Streamlit Page paths are relative to the file where st.navigation is called
pages = {
    "Operational": [
        st.Page("pages/01_overview.py", title="Executive Dashboard", icon="📊", default=True),
        st.Page("pages/02_intelligence.py", title="Product Intelligence", icon="🔎"),
    ],
    "Analytical": [
        st.Page("pages/03_retailers.py", title="Retailer Performance", icon="🏢"),
        st.Page("pages/04_geography.py", title="Geographic Benchmarking", icon="🗺️"),
        st.Page("pages/05_analytics.py", title="Advanced Data Science", icon="🧪"),
    ]
}

pg = st.navigation(pages)

# Inject data into session state for pages
st.session_state['nexus_df'] = df

pg.run()
