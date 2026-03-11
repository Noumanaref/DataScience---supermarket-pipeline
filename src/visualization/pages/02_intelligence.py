import streamlit as st
import pandas as pd
from src.visualization.components.interpretations import interpret_product_search

def show():
    if 'nexus_df' not in st.session_state:
        st.error("Data Context Lost.")
        return

    df = st.session_state['nexus_df']
    
    st.markdown("<h1>Identity Intelligence & Discovery</h1>", unsafe_allow_html=True)
    
    # Filters
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        city = st.selectbox("Market Territory", sorted(df['city'].unique()))
    with f_col2:
        category = st.selectbox("Asset Sector", ["All Sectors"] + sorted(df['category_normalized'].unique().tolist()))
    
    cdf = df[df['city'] == city]
    if category != "All Sectors":
        cdf = cdf[cdf['category_normalized'] == category]

    search_query = st.text_input("🔍 Search Brand or Product Identity", "").lower()

    if search_query:
        results = cdf[cdf['canonical_name'].str.contains(search_query, na=False)]
        if not results.empty:
            st.markdown(f"### Discovered {len(results['product_id'].unique())} unique product cohorts")
            
            for pid in results['product_id'].unique()[:10]:
                item = cdf[cdf['product_id'] == pid]
                st.markdown(f"""
                    <div class='nexus-card' style='padding: 20px; border-left: 5px solid #00FBFF;'>
                        <div style='display:flex; justify-content:space-between;'>
                            <h3 style='margin:0;'>{item['canonical_name'].iloc[0].title()}</h3>
                            <code style='color:#00FBFF;'>{pid}</code>
                        </div>
                        <p style='color:#888; font-size:0.8rem;'>{item['category_normalized'].iloc[0]} // {item['brand_clean'].iloc[0] if pd.notnull(item['brand_clean'].iloc[0]) else "Unknown Brand"}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(3)
                stores = [("AlFatah", "#3366cc"), ("Metro", "#109618"), ("ChaseUp", "#ff9900")]
                min_p = item['price_clean'].min()
                
                for i, (s_name, s_color) in enumerate(stores):
                    p_data = item[item['store_name'].str.contains(s_name, case=False, na=False)]
                    with cols[i]:
                        if not p_data.empty:
                            p = p_data['price_clean'].iloc[0]
                            is_best = p == min_p
                            st.markdown(f"""
                                <div style='text-align:center; padding:15px; background:rgba(255,255,255,0.02); border-radius:10px; border-bottom:3px solid {s_color};'>
                                    <p style='margin:0; color:#888;'>{s_name}</p>
                                    <h2 style='margin:10px 0;'>Rs. {p:,.0f}</h2>
                                    {"<span style='color:#109618; font-weight:700;'>★ BEST VALUE</span>" if is_best else ""}
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align:center; opacity:0.3;'>N/A</div>", unsafe_allow_html=True)
                
                with st.expander(f"🛡️ Intelligence Report: {item['canonical_name'].iloc[0]}", expanded=False):
                    st.markdown(interpret_product_search(item))
                
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("No entity matches found in this territory.")
    else:
        st.info("💡 Enter an asset name to begin price benchmarking.")
        st.dataframe(cdf[['canonical_name', 'store_name', 'price_clean', 'category_normalized']].head(20), use_container_width=True)

# Execute Page
show()
