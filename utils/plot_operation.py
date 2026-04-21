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
):
    unit = "t" if commodity_type == "carbon dioxide" else "MWh"

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