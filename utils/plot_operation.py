import plotly.graph_objects as go
import pandas as pd
import streamlit as st
def _to_plotly_color(color):
    if isinstance(color, tuple):
        return f"rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})"
    return color


def plot_operation_plotly(
    layer: str,
    commodity_type: str,
    plot_df: pd.DataFrame,
    tag: str,
    color_func=None,
    electrolyzer=False,
):
    unit = "t" if commodity_type == "carbon dioxide" else "MWh"
    # if electrolyzer is False and the node name contains electrolyzer, rename it to "curtailment"
    if not electrolyzer:
        plot_df["node_name"] = plot_df["node_name"].apply(
            lambda x: "curtailment" if "electrolyzer" in x.lower() else x)
    if plot_df.empty:
        return go.Figure()

    # keep original time order
    time_order = (
        plot_df[["time", "time_label"]]
        .drop_duplicates()
        .sort_values("time")
    )

    node_order = plot_df["node_name"].drop_duplicates().tolist()
    district_elec_nodes = [node for node in node_order if node.startswith("elec_line") and "_b" not in node]
    fig = go.Figure()

    for node in node_order:
        sub_df = plot_df[plot_df["node_name"] == node].copy()
        sub_df = time_order.merge(sub_df, on=["time", "time_label"], how="left").fillna(
            {"node_name": node, "value": 0}
        )

        if node in district_elec_nodes:
            node_index = district_elec_nodes.index(node)
        else:
            node_index = 0
        color = color_func(node, layer, node_index) if color_func is not None else None    
        color = _to_plotly_color(color) if color is not None else None

        fig.add_trace(
            go.Bar(
                x=sub_df["time_label"],
                y=sub_df["value"],
                name=node,
                marker_color=color,
                hovertemplate=(
                    "Time: %{x}<br>"
                    f"Value: %{{y:.2f}} {unit}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=f"Operation of Different Technologies Over Time - {tag}",
        xaxis_title="Weekday and Hour",
        yaxis_title=f"Operation ({unit})",
        barmode="relative",
        template="plotly_white",
        height=550,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.35,
            xanchor="center",
            x=0.5,
            font=dict(size=9),
            title_font=dict(size=10),
        ),
        margin=dict(l=40, r=20, t=70, b=140),
    )

    fig.update_xaxes(tickangle=90)
    fig.update_yaxes(showgrid=True, zeroline=True, zerolinewidth=1)
    # add vertucal grid lines for each day (every 24 hours)
    for i in range(1, len(plot_df["time_label"].unique()) // 24):
        fig.add_vline(x=i * 24 - 0.5, line_width=1, line_dash="dash", line_color="lightgray")
    return fig

def visualize_independent_index(independent_index_df):
    df = independent_index_df.copy()

    # 先用于排序
    df["year_month_dt"] = pd.to_datetime(df["year-month"])

    # 再转成字符串，作为等距的 category x-axis
    df["year_month_str"] = df["year_month_dt"].dt.strftime("%Y-%m")

    # 保证顺序正确
    category_order = (
        df[["year_month_dt", "year_month_str"]]
        .drop_duplicates()
        .sort_values("year_month_dt")["year_month_str"]
        .tolist()
    )

    df = df.sort_values(["year_month_dt", "scenario"])

    fig_index = go.Figure()

    scenarios = df["scenario"].unique()

    for scenario in scenarios:
        sub_df = df[df["scenario"] == scenario]

        fig_index.add_trace(
            go.Scatter(
                x=sub_df["year_month_str"],
                y=sub_df["independent_index"],
                name=scenario,
                hovertemplate=(
                    "Scenario: " + str(scenario) + "<br>"
                    "Year-Month: %{x}<br>"
                    "Independent Index: %{y:.2f}<extra></extra>"
                ),
            )
        )

    fig_index.update_layout(
        title="Independent Index Over Time",
        xaxis_title="Year-Month",
        yaxis_title="Independent Index",
        template="plotly_white",
        height=500,
        barmode="group",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=9),
            title_font=dict(size=10),
        ),
        margin=dict(l=40, r=20, t=70, b=120),
        bargap=0.15,      
        bargroupgap=0.05  
    )

    fig_index.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=category_order,
        tickangle=45
    )

    fig_index.update_yaxes(
        showgrid=True,
        zeroline=True,
        zerolinewidth=1
    )

    st.plotly_chart(fig_index, use_container_width=True)