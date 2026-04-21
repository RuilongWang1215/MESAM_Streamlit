import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from config import scenario_dict

def color_picker(node_name: str)-> str:
    housing_type_dict = {
        "MFH_until_2004": 'brown',
        "MFH_2005-2014": 'salmon',
        "MFH_from_2015": 'sandybrown',
        "SFH_until_2004": 'steelblue',
        "SFH_2005-2014": 'deepskyblue',
        "SFH_from_2015": 'skyblue',
    }
    default_colors = sns.color_palette("tab20", n_colors=16)
    HW_colors = sns.color_palette("tab20b", n_colors=8)
    technology_color_dict = {
        "BLVL_HotWaterTank": default_colors[0],
        "DLVL_HotWaterTank": "teal",
        "DLVL_NMC": default_colors[9],
        "BLVL_VanadiumRedox": default_colors[10],
        "SH_HPAS": default_colors[2],
        "SH_HPGS": default_colors[3],
        "DH_HP_Water": "cyan",
        "SH_GasBoiler": default_colors[5],
        "SH_PelletBoiler": default_colors[6],
        "SH_WoodBoiler": default_colors[7],
        "SH_OilBoiler": default_colors[8],
        "RE_RTPV": "yellowgreen",
        "RE_GPV": "gold",
        "RE_WT": "limegreen",
        "DLVL_Li-ion": default_colors[12],
        "DLVL_NaS": default_colors[13],
        "SH_roof_retrofit": "thistle",
        "SH_wall_retrofit": default_colors[15],
        "SH_window_retrofit": default_colors[11],
        "SH_HydrogenBoiler": HW_colors[5],
        "HW_ElectricBoiler": HW_colors[0],
        "HW_HPAS": HW_colors[1],
        "HW_HPGS": HW_colors[2],
        "HW_GasBoiler": HW_colors[3],
        "HW_OilBoiler": HW_colors[4],
    }
    if any(k==node_name for k in ["elec_line", "DH_line"]):
        return "grey"
    if node_name == "demand":
        return "red"
    elif any(k in node_name for k in housing_type_dict.keys()):
        for key, color in housing_type_dict.items():
            if key in node_name:
                return color
    elif "import" in node_name:
        return "darkgoldenrod"
    elif "export" in node_name:
        return "crimson"
    else:
        for key, color in technology_color_dict.items():
            if key in node_name:
                return color
        return "grey"
    
def plot_stacked_capacity_single(
    pivot_table,
    scenario,
    technology_label,
    kind="bar",
    value_mode="absolute",
    color_func=None,
    figsize=(6, 4),
    y_max=None,
):
    if pivot_table is None or pivot_table.empty:
        return None

    if value_mode == "percentage" and pivot_table.shape[1] <= 1:
        return None

    fig, ax = plt.subplots(figsize=figsize)

    colors = None
    if color_func is not None:
        colors = [color_func(col) for col in pivot_table.columns]

    pivot_table.plot(
        kind=kind,
        stacked=True,
        ax=ax,
        color=colors,
        alpha=0.8
    )

    ax.set_title(f"{technology_label} - {scenario}", fontsize=11)
    ax.set_xlabel("Time")

    if value_mode == "absolute":
        ax.set_ylabel("Invested Capacity (MW)")
        ylim = y_max * 1.05 if y_max is not None and y_max > 0 else max(pivot_table.sum(axis=1).max() * 1.05, 1)
        ax.set_ylim(0, ylim)
        step = max(1, int(ylim // 5))
        ax.set_yticks(range(0, int(ylim) + 1, step))
    else:
        ax.set_ylabel("Invested Capacity Percentage (%)")
        ax.set_ylim(0, 100)
        ax.set_yticks(range(0, 101, 10))

    if kind == "bar":
        ax.set_xticks(range(len(pivot_table.index)))
        ax.set_xticklabels(pivot_table.index, rotation=0)
    else:
        ax.set_xticks(pivot_table.index)
        ax.set_xticklabels(pivot_table.index, rotation=0)

    ax.grid(True, axis="y", linestyle="--", linewidth=1)
    ax.legend(title="Technology", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()

    return fig

def plot_stacked_capacity_single_plotly(
    pivot_table,
    scenario,
    technology_label,
    kind="bar",
    value_mode="absolute",
    color_func=None,
    y_max=None,
):
    if pivot_table is None or pivot_table.empty:
        return None

    fig = go.Figure()

    for col in pivot_table.columns:
        color = color_func(col) if color_func is not None else None

        if isinstance(color, tuple):
            color = f"rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})"

        if kind == "bar":
            fig.add_trace(
                go.Bar(
                    x=pivot_table.index,
                    y=pivot_table[col],
                    name=col,
                    marker_color=color,
                    hovertemplate=(
                        f"Technology: {col}<br>"
                        "Time: %{x}<br>"
                        "Value: %{y:.2f}<extra></extra>"
                    ),
                    showlegend=True
                )
            )
        elif kind == "area":
            fig.add_trace(
                go.Scatter(
                    x=pivot_table.index,
                    y=pivot_table[col],
                    mode="lines",
                    name=col,
                    stackgroup="one",
                    line=dict(width=0.5),
                    fillcolor=color,
                    hovertemplate=(
                        f"Technology: {col}<br>"
                        "Time: %{x}<br>"
                        "Value: %{y:.2f}<extra></extra>"
                    ),
                    showlegend=True
                )
            )
        else:
            raise ValueError("kind must be either 'bar' or 'area'.")

    if value_mode == "absolute":
        y_title = "Invested Capacity (MW)"
        y_range = [0, y_max * 1.05] if y_max is not None and y_max > 0 else None
    else:
        y_title = "Invested Capacity Percentage (%)"
        y_range = [0, 100]

    fig.update_layout(
        title=f"{scenario_dict.get(scenario, scenario)}",
        xaxis_title="Time",
        yaxis_title=y_title,
        barmode="stack",
        template="plotly_white",
        height=420,
        legend_title="Technology",
        yaxis=dict(range=y_range),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            font=dict(size=9),
            title_font=dict(size=10)
        )
    )

    fig.update_xaxes(type="category")
    fig.update_yaxes(showgrid=True, zeroline=True)

    return fig