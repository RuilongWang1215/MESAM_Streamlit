import streamlit as st
from utils.data_loader import load_all_summary_data

st.title("Overview")

df_summary = load_all_summary_data()

if df_summary.empty:
    st.warning("No summary data found.")
    st.stop()

st.subheader("Cross-Municipality Cost Comparison")

st.dataframe(df_summary, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Municipalities", "...")
with col2:
    st.metric("Scenarios", "...")
with col3:
    st.metric("Total Cost", "...")

st.subheader("Comparison Plots")
st.info("Placeholder for cross-municipality and cross-scenario cost comparison plots.")