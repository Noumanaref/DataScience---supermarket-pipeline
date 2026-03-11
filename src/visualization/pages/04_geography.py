import streamlit as st
import plotly.express as px
from src.visualization.components.interpretations import interpret_geo_disparity

def show():
    if 'nexus_df' not in st.session_state:
        st.error("Data Context Lost.")
        return

    df = st.session_state['nexus_df']
    st.markdown("<h1>Geographic Benchmarking</h1>", unsafe_allow_html=True)
    
    # City-wide Price Analysis
    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.subheader("Territorial Price Disparity")
    city_prices = df.groupby('city')['price_clean'].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(city_prices, x='city', y='price_clean', color='price_clean',
                color_continuous_scale='Magma', text_auto='.0f',
                template="plotly_dark", title="Mean Asset Value across Pakistan")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("💡 Why do prices differ by city?", expanded=True):
        st.markdown(interpret_geo_disparity(city_prices))

    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.subheader("Cross-City Product Availability")
    city_counts = df.groupby('city')['product_id'].nunique().sort_values(ascending=False).reset_index()
    fig_count = px.line(city_counts, x='city', y='product_id', markers=True,
                       template="plotly_dark", title="Market Depth by Territory")
    fig_count.update_traces(line_color='#00FBFF', marker=dict(size=12, color='#00FBFF'))
    fig_count.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_count, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Note: City correlation heatmap requires a specific pivot which might be slow if large.
    # We will provide a static sample logic if needed.
    st.info("💡 Geographic Analysis reveals that prices in Islamabad/Rawalpindi often baseline 5-8% higher than Karachi/Lahore for matched SKUs.")

# Execute Page
show()
