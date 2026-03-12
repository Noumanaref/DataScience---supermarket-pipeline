import streamlit as st
import plotly.express as px
from src.visualization.components.interpretations import interpret_ldi, calculate_real_ldi

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
    
    st.markdown(f"<h1>Retailer Intelligence: {selected_city}</h1>", unsafe_allow_html=True)
    cdf = df[df['city'] == selected_city]

    # LDI Proxy: Local Dominance Index
    st.subheader(f"LDI & Category Dominance: {selected_city}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
        # Real LDI calculation
        real_ldi = calculate_real_ldi(cdf)
        fig_ldi = px.bar(real_ldi, x='store_name', y='LDI_Score', color='store_name',
                        template="plotly_dark", title="True LDI (Price Leadership %)")
        fig_ldi.update_layout(yaxis_tickformat='.1%')
        st.plotly_chart(fig_ldi, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("🎯 True LDI: Price Leadership Analysis", expanded=True):
            st.markdown(interpret_ldi(real_ldi, is_real_ldi=True))

    with col2:
        st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
        # Unique products per store
        unique_counts = cdf.groupby('store_name')['product_id'].nunique().reset_index(name='Unique Products')
        fig_sku = px.bar(unique_counts, x='store_name', y='Unique Products', color='store_name',
                        template="plotly_dark", title="Market Breadth (SKU Count)")
        st.plotly_chart(fig_sku, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("📦 Market Breadth Analysis", expanded=False):
            st.markdown(interpret_ldi(unique_counts, is_real_ldi=False))

    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.subheader("Category Performance Comparison")
    cat_perf = cdf.groupby(['category_normalized', 'store_name'])['price_clean'].mean().reset_index()
    fig_heat = px.density_heatmap(cat_perf, x="store_name", y="category_normalized", z="price_clean",
                                 color_continuous_scale="Viridis",
                                 title="Pricing Density Heatmap by Category")
    fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Execute Page
show()
