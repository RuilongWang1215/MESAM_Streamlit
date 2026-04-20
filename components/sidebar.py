import streamlit as st
from utils.data_loader import get_municipality_list


def render_sidebar():
    st.sidebar.title("Navigation")
    st.sidebar.markdown("Explore the optimization results.")

    municipality_list = get_municipality_list()

    selected_municipality = st.sidebar.selectbox(
        "Select municipality",
        municipality_list if municipality_list else ["No data available"]
    )

    return {
        "municipality": selected_municipality
    }