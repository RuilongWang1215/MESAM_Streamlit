import streamlit as st
import pandas as pd
import os
from components.sidebar import render_sidebar
from utils.data_loader import load_aggregated_investment_data, load_re_potential
from utils.processing import (
    prepare_investment_stacked_data,
    prepare_stacked_pivot_table,
    get_display_technology_name,
    compute_global_capacity_max,
)
from utils.plot_investment import plot_stacked_capacity_single_plotly
from config import scenario_dict
from utils.plot_investment import color_picker

def render_technology_type_grid(
    df_raw,
    technology_type,
    scenario_order,
    kind="bar",
    value_mode="absolute",
    color_func=color_picker 
):
    
    df_prepared = prepare_investment_stacked_data(df_raw)
    technology_label = get_display_technology_name(technology_type)
    if df_prepared[df_prepared["technology_type"] == technology_type].empty:
        return False
    global_ymax = None
    if value_mode == "absolute":
        global_ymax = compute_global_capacity_max(df_prepared, technology_type)

    st.subheader(technology_label)
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    slots = [row1_col1, row1_col2, row2_col1, row2_col2]

    for i, scenario in enumerate(scenario_order[:4]):
        pivot_table = prepare_stacked_pivot_table(
            df=df_prepared,
            scenario=scenario,
            technology_type=technology_type,
            value_mode=value_mode
        )
        
        fig = plot_stacked_capacity_single_plotly(
            pivot_table=pivot_table,
            scenario=scenario,
            technology_label=technology_label,
            kind=kind,
            value_mode=value_mode,
            color_func=color_func,
            y_max=global_ymax,
        )

        with slots[i]:
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No data for {technology_label} - {scenario_dict.get(scenario, scenario)}")
    return True

def render_re_potential_cards(potential_table):
    if potential_table.empty:
        st.warning("No renewable potential data found for this municipality.")
        return

    tech_mapping = {
        "GPV": ("☀️", "Ground PV"),
        "RTPV": ("🏠☀️", "Rooftop PV"),
        "WT": ("🌀", "Wind Turbine"),
    }

    def format_tech(col_name):
        tech_code = col_name.split("_")[0]
        return tech_mapping.get(tech_code, ("⚡", tech_code))

    potential_cols = [c for c in potential_table.columns if c != "scenario"]

    for i in range(0, len(potential_table), 2):
        cols = st.columns(2)

        for j, container in enumerate(cols):
            if i + j >= len(potential_table):
                continue

            row = potential_table.iloc[i + j]

            with container:
                st.markdown(f"**{row['scenario']}**")

                for col in potential_cols:
                    value = row[col]
                    if pd.isna(value):
                        continue

                    icon, tech_name = format_tech(col)
                    st.write(f"{icon} {tech_name}: {value:,.2f} MW")
                
sidebar_state = render_sidebar()
municipality = sidebar_state["municipality"]
st.title(f"Municipality: {municipality}")
#=======Renewable potential ============================
st.subheader("Renewable Potential")
potential_table = load_re_potential(municipality)
if potential_table.empty:
    st.warning("No renewable potential data found for this municipality.")
else:
    render_re_potential_cards(potential_table)
st.markdown("---")
#====First part: show the aggregated investment decision data for the selected municipality and visualization===========
st.subheader("Aggregated Investment Decision Data")
st.write(
    "This section shows the aggregated investment decision data for the selected municipality across all districts."
    "Only new investments after 2026 are included. And the capacity at each time step is the cumulative capacity up to that time step, which means it includes the capacity from previous time steps plus any new investments at that time step."
)
scenario_order = list(scenario_dict.keys())
data = load_aggregated_investment_data(municipality)
if data.empty:
    st.warning("No investment decision data found for this municipality.")
else:
    kind = st.selectbox("Plot type", ["bar", "area"])
    value_mode = st.selectbox("Value mode", ["absolute", "percentage"])

    plot = render_technology_type_grid(
        df_raw=data,
        technology_type="RE",
        scenario_order=scenario_order,
        kind=kind,
        value_mode=value_mode
    )
    st.markdown("---")
    
    # battery
    plot = render_technology_type_grid(
        df_raw=data,
        technology_type="Battery",
        scenario_order=scenario_order,
        kind=kind,
        value_mode=value_mode
    )
    if plot: 
        st.markdown("---")

    # space heating and hot water
    plot = render_technology_type_grid(
        df_raw=data,
        technology_type="SH_HW",
        scenario_order=scenario_order,
        kind=kind,
        value_mode=value_mode
    )
    if plot:
        st.markdown("---")

    # heat storage
    plot = render_technology_type_grid(
        df_raw=data,
        technology_type="Heat_storage",
        scenario_order=scenario_order,
        kind=kind,
        value_mode=value_mode
    )
    if plot:
        st.markdown("---")

    # retrofit
    plot = render_technology_type_grid(
        df_raw=data,
        technology_type="retrofit",
        scenario_order=scenario_order,
        kind=kind,
        value_mode=value_mode
    )
    if plot:
        st.markdown("---")

    # hydrogen related technologies
    plot = render_technology_type_grid(
        df_raw=data,
        technology_type="Hydrogen",
        scenario_order=scenario_order,
        kind=kind,
        value_mode=value_mode
    )
    if plot:
        st.markdown("---")


