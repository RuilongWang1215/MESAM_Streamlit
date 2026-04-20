import streamlit as st

st.set_page_config(
    page_title="Swiss Municipality Energy System Optimization",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Swiss Municipality Energy System Optimization Dashboard")
st.markdown(
    """
    This dashboard visualizes optimization results across Swiss archetypal municipalities and scenarios.

    Use the sidebar and page navigation to explore:
    - Overview comparison across municipalities
    - Municipality-specific investment decisions
    - Municipality-specific operation decisions
    """
)