import pandas as pd
import plotly.express as px

def plot_cost_comparison_by_municipality(all_data: pd.DataFrame):
    data = all_data.copy()

    required_cols = ["municipality", "scenario", "total_costs"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # optional: sort municipalities by average cost
    municipality_order = (
        data.groupby("municipality")["total_costs"]
        .mean()
        .sort_values()
        .index
        .tolist()
    )

    data["municipality"] = pd.Categorical(
        data["municipality"],
        categories=municipality_order,
        ordered=True
    )

    fig = px.bar(
        data,
        x="municipality",
        y="total_costs",
        color="scenario",
        barmode="group",
        category_orders={"municipality": municipality_order},
        hover_data={
            "municipality": True,
            "scenario": True,
            "total_costs": ":.2f"
        },
        title="Total Cost Comparison Across Municipalities and Scenarios"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Municipality",
        yaxis_title="Total Costs (MCHF)",
        legend_title="Scenario",
        height=600
    )

    fig.update_xaxes(tickangle=-45, showgrid=False)
    fig.update_yaxes(showgrid=True)

    return fig



def plot_cost_change_pct_vs_base(comparison_df: pd.DataFrame):
    data = comparison_df.copy()

    required_cols = ["municipality", "scenario", "cost_change_pct"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # exclude base itself
    data = data[data["scenario"] != "base"].copy()

    municipality_order = (
        data.groupby("municipality")["cost_change_pct"]
        .mean()
        .sort_values()
        .index
        .tolist()
    )

    fig = px.bar(
        data,
        x="municipality",
        y="cost_change_pct",
        color="scenario",
        barmode="group",
        category_orders={"municipality": municipality_order},
        hover_data={
            "municipality": True,
            "scenario": True,
            "cost_change_pct": ":.2f",
        },
        title="Cost Change Relative to Base Scenario (%)"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Municipality",
        yaxis_title="Cost Change vs Base (%)",
        legend_title="Scenario",
        height=600
    )

    fig.update_xaxes(tickangle=-45, showgrid=False)
    fig.update_yaxes(showgrid=True, zeroline=True, zerolinewidth=1)

    return fig

def plot_cost_change_abs_vs_base(comparison_df: pd.DataFrame):
    data = comparison_df.copy()

    required_cols = ["municipality", "scenario", "cost_change"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    data = data[data["scenario"] != "base"].copy()

    municipality_order = (
        data.groupby("municipality")["cost_change"]
        .mean()
        .sort_values()
        .index
        .tolist()
    )

    fig = px.bar(
        data,
        x="municipality",
        y="cost_change",
        color="scenario",
        barmode="group",
        category_orders={"municipality": municipality_order},
        hover_data={
            "municipality": True,
            "scenario": True,
            "cost_change": ":.2f",
            "base_cost": ":.2f",
            "total_costs": ":.2f",
        },
        title="Absolute Cost Change Relative to Base Scenario"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Municipality",
        yaxis_title="Cost Change vs Base",
        legend_title="Scenario",
        height=600
    )

    fig.update_xaxes(tickangle=-45, showgrid=False)
    fig.update_yaxes(showgrid=True, zeroline=True, zerolinewidth=1)

    return fig

def plot_cost_change_heatmap_vs_base(comparison_df: pd.DataFrame):
    data = comparison_df.copy()
    data = data[data["scenario"] != "base"].copy()

    pivot_df = data.pivot(
        index="municipality",
        columns="scenario",
        values="cost_change_pct"
    )

    municipality_order = pivot_df.mean(axis=1).sort_values().index.tolist()
    pivot_df = pivot_df.loc[municipality_order]

    fig = px.imshow(
        pivot_df,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        origin="lower",
        title="Cost Change Relative to Base Scenario (%)"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Scenario",
        yaxis_title="Municipality",
        height=700,
        coloraxis_colorbar_title="% Change"
    )

    return fig