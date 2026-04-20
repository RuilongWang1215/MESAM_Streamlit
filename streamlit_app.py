import streamlit as st

st.set_page_config(
    page_title="Swiss Municipality Energy System Optimization",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Header
# -------------------------
st.title("⚡Impact of consumer preferences on energy system optimization across Swiss municipalities")
st.caption("Interactive dashboard for exploring optimization results across municipalities and scenarios.")

st.markdown("---")

# -------------------------
# Main introduction
# -------------------------
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Dashboard Overview")
    st.write(
        """
        This dashboard visualizes optimization results across Swiss archetypal municipalities
        under multiple scenarios.

        Use the sidebar and page navigation to explore:
        """
    )

    st.markdown(
        """
        - **Overview**: compare total system costs across municipalities and scenarios
        - **Investment Decisions**: analyze technology investment choices 
        - **Operation Decisions**: inspect operation and dispatch results  
        """
    )

with col2:
    st.subheader("What you can explore")
    st.info(
        """
        Compare municipalities, examine scenario differences,
        and understand how consumer preference assumptions
        affect long-term system design.
        """
    )

st.markdown("---")

# -------------------------
# Scenario section
# -------------------------
st.subheader("Scenario Definitions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Baseline")
    st.write(
        "Optimization with a net-zero CO₂ emissions constraint in 2050, "
        "without consumer preference integration."
        
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Technical Potential")
    st.write(
        "Optimization with a net-zero CO₂ emissions constraint in 2050, "
        "where consumer preference modifies the technical potential of technologies."
    )

with col2:
    st.markdown("### Discount Rate")
    st.write(
        "Optimization with a net-zero CO₂ emissions constraint in 2050, "
        "where consumer preference modifies the discount rate of technologies."
    )

    st.markdown("### All")
    st.write(
        "Optimization with a net-zero CO₂ emissions constraint in 2050, "
        "where consumer preference modifies both technical potential and discount rate."
    )

st.markdown("---")

# -------------------------
# Footer note
# -------------------------
st.subheader("Navigation")
st.write(
    "Use the sidebar to select a municipality and switch between pages."
)