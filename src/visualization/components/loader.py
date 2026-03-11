import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data
def load_nexus_data(data_dir: Path):
    path = data_dir / "matched" / "matched_products.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    # Basic cleanup if needed
    if 'canonical_name' not in df.columns:
        return None
    return df
