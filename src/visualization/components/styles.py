import streamlit as st

def apply_nexus_styles():
    st.markdown("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500&family=Space+Grotesk:wght@300;500;700&display=swap" rel="stylesheet">
        
        <style>
        /* Global Background mesh */
        .stApp {
            background: radial-gradient(circle at 20% 30%, rgba(5, 10, 20, 1) 0%, rgba(2, 4, 8, 1) 100%);
            color: #E0E0E0;
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar Glassmorphism */
        [data-testid="stSidebar"] {
            background-color: rgba(5, 7, 12, 0.7) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(0, 251, 255, 0.1);
        }

        /* Typography */
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -1.5px;
            background: linear-gradient(135deg, #FFFFFF 0%, #00FBFF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px !important;
        }
        
        /* Metric Cards */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 15px !important;
            backdrop-filter: blur(5px);
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            border: 1px solid rgba(0, 251, 255, 0.3);
            box-shadow: 0 0 20px rgba(0, 251, 255, 0.1);
        }
        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            color: #00FBFF !important;
        }
        
        /* Premium Cards */
        .nexus-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] { gap: 15px; }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: rgba(255,255,255,0.02);
            border-radius: 8px 8px 0 0;
            padding: 0 20px;
            color: #888;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(0, 251, 255, 0.1) !important;
            color: #00FBFF !important;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #00FBFF 0%, #00A3A6 100%);
            color: #05070A !important;
            font-weight: 700;
            border-radius: 10px;
            border: none;
            padding: 0.6rem 2rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
    """, unsafe_allow_html=True)
