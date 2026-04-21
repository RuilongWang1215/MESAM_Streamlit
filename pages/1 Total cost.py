import streamlit as st
from utils.data_loader import load_all_summary_data, prepare_cost_comparison_vs_base
from utils.plot_cost import (
    plot_cost_comparison_by_municipality,
    plot_cost_change_pct_vs_base,
    plot_cost_change_abs_vs_base,
    plot_cost_change_heatmap_vs_base,
)
# -------------------------
st.title("Total Cost Comparison Across Municipalities and Scenarios")

# load summary data for all municipalities and scenarios
df_summary = load_all_summary_data()
if df_summary.empty:
    st.warning("No summary data found.")


st.subheader("System Summary")

col1, col2 = st.columns(2)
with col1:
    st.metric("Municipalities", df_summary["municipality"].nunique())
with col2:
    st.metric("Scenarios", df_summary["scenario"].nunique())
    
#-------Comparison plots----------------
st.markdown("---")
st.subheader("Comparison of Total Costs Across Municipalities and Scenarios")
# comparison of absolute costs across municipalities and scenarios
st.write("Compare total system costs across municipalities and scenarios. Use the filters to select specific scenarios for comparison."
         "The unit of the cost is in MCHF (Million Swiss Francs)."
         )

all_scenarios = sorted(df_summary["scenario"].dropna().unique())
selected_scenarios = st.multiselect(
    "Select scenarios",
    all_scenarios,
    default=all_scenarios
)

filtered_data = df_summary[df_summary["scenario"].isin(selected_scenarios)]

fig = plot_cost_comparison_by_municipality(filtered_data)
st.plotly_chart(fig, width='content')
st.subheader("Comparison Table - Total Costs")
st.dataframe(df_summary, width='content')

#--------------Comparison of cost change--------------------------
st.markdown("---")
comparison_df = prepare_cost_comparison_vs_base(df_summary)
st.subheader("Cost Change Relative to Base")
st.write(
    "Compare how total costs change relative to the base scenario across municipalities and scenarios."
    " Use the tabs to switch between percentage change, absolute change, and heatmap views."
    " The unit of the cost change is in MCHF (Million Swiss Francs) for absolute change and in percentage for percentage change."
)
tab1, tab2, tab3 = st.tabs([
    "Percentage Change",
    "Absolute Change",
    "Heatmap"
])

with tab1:
    fig_pct = plot_cost_change_pct_vs_base(comparison_df)
    st.plotly_chart(fig_pct, width='content')

with tab2:
    fig_abs = plot_cost_change_abs_vs_base(comparison_df)
    st.plotly_chart(fig_abs, width='content')

with tab3:
    fig_heatmap = plot_cost_change_heatmap_vs_base(comparison_df)
    st.plotly_chart(fig_heatmap, width='content')
st.subheader("Comparison Table - Cost Changes")
st.dataframe(comparison_df, width='content')