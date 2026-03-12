import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from src.visualization.components.interpretations import interpret_correlation_strength

from src.config.settings import DATA_DIR
from src.visualization.components.loader import load_nexus_data

def show():
    if 'nexus_df' not in st.session_state:
        df = load_nexus_data(DATA_DIR)
        if df is not None:
            st.session_state['nexus_df'] = df
        else:
            st.error("Data Context Lost.")
            return

    selected_city = st.session_state.get('selected_city', 'Lahore')
    df = st.session_state['nexus_df']
    df_city = df[df['city'] == selected_city] # Context for city-specific dispersion
    
    st.markdown(f"<h1>Advanced Analytics Suite: {selected_city}</h1>", unsafe_allow_html=True)
    
    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.subheader("Price Dispersion Analysis")
    st.write(f"Visualizing price volatility across matched product cohorts in {selected_city}.")
    
    # Filter for products in multiple stores for variance analysis
    multi_store = df_city.groupby('product_id')['store_name'].nunique().reset_index()
    valid_ids = multi_store[multi_store['store_name'] > 1]['product_id']
    vdf = df_city[df_city['product_id'].isin(valid_ids)]

    fig_disp = px.strip(vdf.sample(min(2000, len(vdf))), x='store_name', y='price_clean', color='store_name',
                       template="plotly_dark", stripmode="overlay", title="Price Point Distribution (Sampled)")
    fig_disp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_disp, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Correlation Section
    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.subheader("Retailer Pricing Correlation")
    
    city = st.selectbox("Market Target for Correlation", sorted(df['city'].unique()))
    c_df = df[df['city'] == city]
    
    pivot_df = c_df.pivot_table(index='product_id', columns='store_name', values='price_clean').dropna()
    
    if len(pivot_df) > 5:
        corr_matrix = pivot_df.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', 
                            template="plotly_dark", title=f"Price Sync Correlation: {city}")
        st.plotly_chart(fig_corr, use_container_width=True)
        
        avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
        strength = interpret_correlation_strength(avg_corr)
        
        with st.expander("🔍 Strategic Pricing Correlation", expanded=True):
            st.markdown(f"""
                **WHAT:** This matrix shows how closely stores mirror each other's pricing. A score of 1.0 is perfect sync.
                
                **KEY FINDING:** The average market correlation is **{avg_corr:.2f}** ({strength}).
                
                **WHY:** High correlation suggests retailers are using **Automated Price Monitoring** and reacting instantly to competitor changes.
                
                **SO WHAT:** High sync means "Store Choice" matters less for these products than "National Trends."
                
                **ACTION:** If correlation is low, shopping around is MANDATORY. If high, stick to your primary convenience store.
            """)
    else:
        st.warning("Insufficient matched data for this city to calculate meaningful correlation.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Automated Reporting
    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.subheader("Automated Intelligence Reports")
    st.write("Generate and download comprehensive market snapshots.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Market Disparity Report"):
            report_df = df.groupby(['city', 'category_normalized']).agg({
                'price_clean': ['mean', 'min', 'max', 'std'],
                'product_id': 'nunique'
            })
            csv = report_df.to_csv().encode('utf-8')
            st.download_button(
                "📥 Download Disparity Report (CSV)",
                data=csv,
                file_name=f"disparity_report_{city.lower()}.csv",
                mime='text/csv'
            )
    
    with col2:
        if st.button("Generate Retailer Benchmarking CSV"):
            bench_df = df.groupby('store_name')['price_clean'].describe()
            st.download_button(
                "📥 Download Benchmarking Suite (CSV)",
                data=bench_df.to_csv().encode('utf-8'),
                file_name="retailer_benchmark.csv",
                mime='text/csv'
            )
    st.markdown("</div>", unsafe_allow_html=True)

# Execute Page
show()
