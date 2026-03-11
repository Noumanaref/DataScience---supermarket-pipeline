import streamlit as st
import plotly.express as px
from src.visualization.components.interpretations import interpret_ldi

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

    df = st.session_state['nexus_df']
    st.markdown("<h1>Retailer Intelligence</h1>", unsafe_allow_html=True)
    
    city = st.sidebar.selectbox("Scope Territory", sorted(df['city'].unique()), key="retailer_city")
    cdf = df[df['city'] == city]

    # LDI Proxy: Local Dominance Index
    st.subheader(f"LDI & Category Dominance: {city}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
        # Unique products per store
        unique_counts = cdf.groupby('store_name')['product_id'].nunique().reset_index(name='Unique Products')
        fig = px.bar(unique_counts, x='store_name', y='Unique Products', color='store_name',
                    template="plotly_dark", title="Market Breadth (SKU Count)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("🎯 LDI: Market Leadership Analysis", expanded=True):
            st.markdown(interpret_ldi(unique_counts))

    with col2:
        st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
        avg_price = cdf.groupby('store_name')['price_clean'].mean().reset_index(name='Avg Price')
        fig_pie = px.pie(avg_price, values='Avg Price', names='store_name', 
                        template="plotly_dark", title="Mean Pricing Tier")
        fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

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
