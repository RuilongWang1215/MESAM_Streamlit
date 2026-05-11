import pandas as pd
import plotly.express as px
from config import region_color_dict, region_dict
import plotly.graph_objects as go

#===========Function to visualize cost comparison across municipalities and scenarios===========
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


def _to_plotly_color(color):
    """Convert seaborn RGB tuple to plotly rgb string."""
    if isinstance(color, tuple):
        return f"rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})"
    return color


def _prepare_region_column(data: pd.DataFrame, region_dict: dict):
    if "region" in data.columns:
        data["region"] = data["region"]
    elif "NUTS2" in data.columns:
        data["region"] = data["NUTS2"].map(region_dict).fillna(data["NUTS2"])
    else:
        raise ValueError("comparison_df must contain either 'region' or 'NUTS2' column.")
    return data


def _add_custom_legends(fig, regions, scenarios, plotly_color_map, scenario_symbol_map):
    # Region legend: only color matters
    for region in regions:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                name=region,
                legendgroup=f"region_{region}",
                legendgrouptitle_text="Region" if region == regions[0] else None,
                marker=dict(
                    size=10,
                    color=plotly_color_map.get(region, "gray"),
                    symbol="circle",
                    line=dict(width=0.5, color="white")
                ),
                showlegend=True,
                hoverinfo="skip"
            )
        )

    # Scenario legend: only shape matters
    for scenario in scenarios:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                name=scenario,
                legendgroup=f"scenario_{scenario}",
                legendgrouptitle_text="Scenario" if scenario == scenarios[0] else None,
                marker=dict(
                    size=10,
                    color="black",
                    symbol=scenario_symbol_map.get(scenario, "circle"),
                    line=dict(width=0.5, color="white")
                ),
                showlegend=True,
                hoverinfo="skip"
            )
        )


def plot_cost_change_pct_vs_base(
    comparison_df: pd.DataFrame,
    scenario_order=None
):
    data = comparison_df.copy()

    required_cols = ["municipality", "scenario", "cost_change_pct"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    data = data[data["scenario"] != "base"].copy()
    data = _prepare_region_column(data, region_dict)

    if scenario_order is None:
        scenario_order = data["scenario"].dropna().unique().tolist()

    data["scenario"] = pd.Categorical(
        data["scenario"],
        categories=scenario_order,
        ordered=True
    )

    municipality_order = (
        data.groupby("municipality")["cost_change_pct"]
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

    plotly_color_map = {
        region: _to_plotly_color(color)
        for region, color in region_color_dict.items()
    }

    scenario_symbol_map = {
        scenario: symbol for scenario, symbol in zip(
            scenario_order,
            ["circle", "square", "diamond", "x", "triangle-up", "cross", "star"]
        )
    }

    fig = go.Figure()

    # real data traces: no legend
    for scenario in scenario_order:
        for region in sorted(data["region"].dropna().unique()):
            subset = data[(data["scenario"] == scenario) & (data["region"] == region)].copy()
            if subset.empty:
                continue

            fig.add_trace(
                go.Scatter(
                    x=subset["municipality"],
                    y=subset["cost_change_pct"],
                    mode="markers",
                    marker=dict(
                        size=10,
                        color=plotly_color_map.get(region, "gray"),
                        symbol=scenario_symbol_map.get(scenario, "circle"),
                        line=dict(width=0.5, color="white"),
                        opacity=0.9
                    ),
                    name=f"{region} | {scenario}",
                    showlegend=False,
                    customdata=subset[["municipality", "region", "scenario"]].values,
                    hovertemplate=(
                        "Municipality: %{customdata[0]}<br>"
                        "Region: %{customdata[1]}<br>"
                        "Scenario: %{customdata[2]}<br>"
                        "Cost change vs base: %{y:.2f}%<extra></extra>"
                    )
                )
            )

    regions = sorted(data["region"].dropna().unique().tolist())
    _add_custom_legends(fig, regions, scenario_order, plotly_color_map, scenario_symbol_map)

    fig.update_layout(
        template="plotly_white",
        title="Cost Change Relative to Base Scenario (%)",
        xaxis_title="Municipality",
        yaxis_title="Cost Change vs Base (%)",
        height=650,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=220)
    )

    fig.update_xaxes(
        categoryorder="array",
        categoryarray=municipality_order,
        tickangle=-45,
        showgrid=False
    )
    fig.update_yaxes(showgrid=True, zeroline=True, zerolinewidth=1)

    return fig


def plot_cost_change_abs_vs_base(
    comparison_df: pd.DataFrame,
    scenario_order=None
):
    data = comparison_df.copy()

    required_cols = ["municipality", "scenario", "cost_change"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    data = data[data["scenario"] != "base"].copy()
    data = _prepare_region_column(data, region_dict)

    if scenario_order is None:
        scenario_order = data["scenario"].dropna().unique().tolist()

    data["scenario"] = pd.Categorical(
        data["scenario"],
        categories=scenario_order,
        ordered=True
    )

    municipality_order = (
        data.groupby("municipality")["cost_change"]
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

    plotly_color_map = {
        region: _to_plotly_color(color)
        for region, color in region_color_dict.items()
    }

    scenario_symbol_map = {
        scenario: symbol for scenario, symbol in zip(
            scenario_order,
            ["circle", "square", "diamond", "x", "triangle-up", "cross", "star"]
        )
    }

    fig = go.Figure()

    # real data traces: no legend
    for scenario in scenario_order:
        for region in sorted(data["region"].dropna().unique()):
            subset = data[(data["scenario"] == scenario) & (data["region"] == region)].copy()
            if subset.empty:
                continue

            has_base = "base_cost" in subset.columns
            has_total = "total_costs" in subset.columns

            custom_cols = ["municipality", "region", "scenario"]
            if has_base:
                custom_cols.append("base_cost")
            if has_total:
                custom_cols.append("total_costs")

            fig.add_trace(
                go.Scatter(
                    x=subset["municipality"],
                    y=subset["cost_change"],
                    mode="markers",
                    marker=dict(
                        size=10,
                        color=plotly_color_map.get(region, "gray"),
                        symbol=scenario_symbol_map.get(scenario, "circle"),
                        line=dict(width=0.5, color="white"),
                        opacity=0.9
                    ),
                    name=f"{region} | {scenario}",
                    showlegend=False,
                    customdata=subset[custom_cols].values,
                    hovertemplate=(
                        "Municipality: %{customdata[0]}<br>"
                        "Region: %{customdata[1]}<br>"
                        "Scenario: %{customdata[2]}<br>"
                        + ("Base cost: %{customdata[3]:.2f}<br>" if has_base else "")
                        + ("Scenario cost: %{customdata[4]:.2f}<br>" if has_base and has_total else "")
                        + ("Scenario cost: %{customdata[3]:.2f}<br>" if (not has_base and has_total) else "")
                        + "Absolute cost change: %{y:.2f}<extra></extra>"
                    )
                )
            )

    regions = sorted(data["region"].dropna().unique().tolist())
    _add_custom_legends(fig, regions, scenario_order, plotly_color_map, scenario_symbol_map)

    fig.update_layout(
        template="plotly_white",
        title="Absolute Cost Change Relative to Base Scenario",
        xaxis_title="Municipality",
        yaxis_title="Cost Change vs Base (MCHF)",
        height=650,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=220)
    )

    fig.update_xaxes(
        categoryorder="array",
        categoryarray=municipality_order,
        tickangle=-45,
        showgrid=False
    )
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

#==================Function to visualize investment decision comparison across municipality and scenarios=====
