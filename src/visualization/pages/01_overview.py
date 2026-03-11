import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.visualization.components.styles import apply_nexus_styles
from src.visualization.components.interpretations import interpret_dispersion_market
def show():
    if 'nexus_df' not in st.session_state:
        st.error("Data Context Lost. Please restart the application.")
        return

    df = st.session_state['nexus_df']
    
    st.markdown("<h1>Operational Overview</h1>", unsafe_allow_html=True)
    
    # Hero Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", f"{len(df):,}", delta="Live Feed")
    with col2:
        st.metric("Unique Entities", f"{df['product_id'].nunique():,}")
    with col3:
        st.metric("Market Footprint", f"{df['city'].nunique()} Cities")
    with col4:
        st.metric("Avg Price Index", f"Rs. {df['price_clean'].mean():.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Secondary Analysis
    row2_col1, row2_col2 = st.columns([2, 1])
    
    with row2_col1:
        st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
        st.subheader("Retailer Performance Summary")
        store_stats = df.groupby('store_name').agg({
            'price_clean': 'mean',
            'product_id': 'count'
        }).reset_index().rename(columns={'price_clean': 'Avg Price', 'product_id': 'Volume'})
        
        fig = px.bar(store_stats, x='store_name', y='Volume', text='Volume',
                    color='Avg Price', color_continuous_scale='Turbo',
                    template="plotly_dark", title="Catalog Depth vs. Pricing")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("💡 What does this store performance mean?", expanded=True):
            st.markdown("""
                **WHAT:** This chart compares how many products each store stocks (Volume) against their average price point.
                
                **WHY:** Retailers usually choose between 'High Volume/Low Price' (Value Leaders) or 'Lower Volume/Premium Price' (Convenience/Service Leaders).
                
                **SO WHAT:** A high-volume store with low prices (Cold colors) is your best bet for 90% of your shopping.
                
                **ACTION:** Identify the 'Deep Blue/Green' bars as your primary shopping destinations for bulk grocery runs.
            """)

    with row2_col2:
        st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
        st.subheader("Global Sector Mix")
        cat_mix = df['category_normalized'].value_counts().head(5)
        fig_pie = px.pie(values=cat_mix.values, names=cat_mix.index, hole=0.5,
                        template="plotly_dark")
        fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                             margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.subheader("Market Equilibrium Analysis")
    st.markdown(interpret_dispersion_market(df))
    st.markdown("</div>", unsafe_allow_html=True)

    # Recent Activity
    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.subheader("Pipeline Health & Freshness")
    freshness = df.groupby(['store_name', 'city'])['scraped_at'].max().reset_index()
    st.dataframe(freshness.sort_values('scraped_at', ascending=False), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Execute Page
show()
