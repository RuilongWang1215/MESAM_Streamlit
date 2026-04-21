import streamlit as st
from components.sidebar import render_sidebar
from config import scenario_dict
from utils.data_loader import get_operation_level, get_flow_types, load_operation_data, get_sub_type
import datetime as dt
import pandas as pd
from utils.processing import filter_flow_time
from utils.plot_investment import color_picker
from utils.plot_operation import plot_operation_plotly 
from utils.processing import operation_data_preprocessing, prepare_operation_plot_data


sidebar_state = render_sidebar()
municipality = sidebar_state["municipality"]
st.title(f"Municipality: {municipality}")

#====First part: show the aggregated investment decision data for the selected municipality and visualization===========
st.write(
    "This page presents the operational flow balance for the selected municipality. "
    "You can explore different flow types, including electricity, heat, and CO₂, "
    "as well as balances at different aggregation levels, such as municipality, district, "
    "and building archetype. "
    "All values are reported in MWh. A positive balance indicates a surplus, "
    "while a negative balance indicates a demand."
)

scenario = st.selectbox("Scenario", scenario_dict.values())# get scenario_key from value 
scenario_key = None
for key, value in scenario_dict.items():
    scenario_key = key if value == scenario else scenario_key

levels = get_operation_level(municipality, scenario_key)
if levels:
    node_level = st.selectbox("Node level", levels, index=1)

flow_types = get_flow_types(municipality, scenario_key, node_level)
if flow_types:
    flow_type = st.selectbox("Flow type", flow_types, index=1)

if node_level in ['building', 'district'] and flow_type:
    sub_types = get_sub_type(municipality, scenario_key, flow_type, node_level)
    if sub_types:
        sub_type = st.selectbox("Sub type", sub_types)

if scenario_key and node_level and flow_type:
    df = load_operation_data(municipality, scenario_key, node_level, flow_type, sub_type if 'sub_type' in locals() else None)
    if df.empty:
        st.warning("No data available for the selected combination.")
    else: 
        col1, col2 = st.columns(2)
        with col1:
            years = sorted(pd.to_datetime(df["time"]).dt.year.unique())
            year = st.selectbox("Year", years, index=0)
        with col2:
            season = st.selectbox("Season", ["spring", "summer", "autumn", "winter"], index=0)
        filtered_df = filter_flow_time(df, year, season)
        #st.dataframe(filtered_df)
        
        df_processed = operation_data_preprocessing(filtered_df)
        plot_df = prepare_operation_plot_data(df_processed)

        fig = plot_operation_plotly(
            layer=node_level,
            commodity_type=flow_type,
            plot_df=plot_df,
            tag=f"{node_level} - {flow_type}",
            color_func=color_picker,
        )

        st.plotly_chart(fig, use_container_width=True)
