from turtle import st
from config import scenario_dict
import pandas as pd
import os 
def add_tech_label(df):
    df = df.copy()

    def classify_technology(name):
        if ("SH" in name or "HW" in name or "DH" in name) and ("retrofit" not in name):
            return "SH_HW"
        elif "retrofit" in name:
            return "retrofit"
        elif "H2" in name:
            return "Hydrogen"
        elif 'HotWaterTank' in name:
            return "Heat_storage"
        elif any(k in name for k in ["Li-ion", "NaS", "NaNiCl", "VRF"]):
            return "Battery"
        else:
            return "RE"

    df["technology_type"] = df["name"].apply(classify_technology)
    return df


def prepare_investment_stacked_data(df):
    scenario_cols = [
        col for col in df.columns
        if col.startswith("scen_") and col.endswith("_invested_available_unit")
    ]

    if not scenario_cols:
        raise ValueError("No scenario investment columns found.")

    all_scenarios = []

    for scen_col in scenario_cols:
        scenario = scen_col.replace("scen_", "").replace("_invested_available_unit", "")

        sub_df = df[["name", "time", scen_col, "scale per unit (MW)"]].copy()

        sub_df["capacity_MW"] = sub_df.apply(
            lambda row: row[scen_col]
            if pd.isna(row["scale per unit (MW)"]) or row["scale per unit (MW)"] == 0
            else row[scen_col] * row["scale per unit (MW)"],
            axis=1,
        )

        sub_df["name"] = sub_df["name"].apply(
            lambda x: x.split("_s_")[0] if "_s_" in x else x
        )

        sub_df = sub_df.drop(columns=[scen_col, "scale per unit (MW)"])
        sub_df = sub_df.groupby(["name", "time"], as_index=False)["capacity_MW"].sum()
        sub_df["scenario"] = scenario

        all_scenarios.append(sub_df)

    df_all = pd.concat(all_scenarios, ignore_index=True)
    df_all = add_tech_label(df_all)

    return df_all


def prepare_stacked_pivot_table(df, scenario, technology_type, value_mode="absolute"):
    sub_df = df[
        (df["scenario"] == scenario) &
        (df["technology_type"] == technology_type)
    ].copy()

    pivot_table = (
        sub_df.pivot_table(
            index="time",
            columns="name",
            values="capacity_MW",
            aggfunc="sum"
        )
        .fillna(0)
        .sort_index()
    )

    pivot_table = pivot_table.loc[:, (pivot_table != 0).any(axis=0)]

    if pivot_table.shape[1] == 0:
        return pivot_table

    if value_mode == "percentage":
        row_sum = pivot_table.sum(axis=1)
        pivot_table = pivot_table.div(row_sum.replace(0, pd.NA), axis=0) * 100

    return pivot_table


def get_display_technology_name(technology_type):
    mapping = {
        "RE": "Renewable Energy Technologies",
        "SH_HW": "Space Heating and Hot Water",
        "retrofit": "Retrofit",
        "Hydrogen": "Hydrogen Related Technologies",
        "Heat_storage": "Heat Storage",
        "Battery": "Battery Storage",
    }
    return mapping.get(technology_type, technology_type)


def compute_global_capacity_max(df, technology_type):
    global_capacity_max = 0

    for scenario in df["scenario"].unique():
        pivot_table = prepare_stacked_pivot_table(
            df=df,
            scenario=scenario,
            technology_type=technology_type,
            value_mode="absolute"
        )

        if pivot_table.shape[1] == 0:
            continue

        local_max = pivot_table.sum(axis=1).max()
        global_capacity_max = max(global_capacity_max, local_max)

    return global_capacity_max

def flow_type_mapping(flow_type):
    mapping = {
        "elec": "electricity",
        "CO2": "carbon dioxide",
        "HW": "hot water",
        "SH": "space heating",
    }
    return mapping.get(flow_type, flow_type)

def filter_flow_time(data, year, season):
    season_month_mapping = {
        "spring": 4,
        "summer": 7,
        "autumn": 10,
        "winter": 1
    }
    # convert data['time'] to datetime if it's not already
    # filter by year and season month
    data['time'] = pd.to_datetime(data['time'], errors='coerce')
    data = data[data['time'].dt.year == year]
    data = data[data['time'].dt.month == season_month_mapping[season]]
    return data

def operation_data_preprocessing(operation_data: pd.DataFrame) -> pd.DataFrame:
    operation_data = operation_data.copy()
    operation_data["time"] = pd.to_datetime(operation_data["time"])

    # keep numeric columns only, except time
    numeric_cols = [col for col in operation_data.columns if col != "time"]

    operation_data[numeric_cols] = operation_data[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    ).fillna(0)

    # replace very small values with 0
    operation_data[numeric_cols] = operation_data[numeric_cols].mask(
        operation_data[numeric_cols].abs() < 1e-5, 0
    )

    # merge import/export into net flow
    import_cols = [col for col in operation_data.columns if "import" in col]
    for imp_col in import_cols:
        exp_col = imp_col.replace("import", "export")
        if exp_col in operation_data.columns:
            net_flow = operation_data[imp_col] + operation_data[exp_col]
            operation_data[imp_col] = net_flow.clip(lower=0)   # positive import
            operation_data[exp_col] = net_flow.clip(upper=0)   # negative export

    # drop columns whose total absolute value is zero
    numeric_cols = [col for col in operation_data.columns if col != "time"]
    nonzero_numeric_cols = [
        col for col in numeric_cols
        if operation_data[col].abs().sum() != 0
    ]

    operation_data = operation_data[["time", *nonzero_numeric_cols]]

    return operation_data

def prepare_operation_plot_data(operation_data: pd.DataFrame) -> pd.DataFrame:
    plot_data = operation_data.copy()
    plot_data["time"] = pd.to_datetime(plot_data["time"])

    value_cols = [col for col in plot_data.columns if col != "time"]

    long_df = plot_data.melt(
        id_vars=["time"],
        value_vars=value_cols,
        var_name="node_name",
        value_name="value"
    )

    # drop exact zeros to reduce clutter
    long_df = long_df[long_df["value"] != 0].copy()

    long_df["direction"] = long_df["value"].apply(
        lambda x: "positive" if x >= 0 else "negative"
    )

    # example: Mon 13:00
    long_df["time_label"] = long_df["time"].dt.strftime("%a %H:%M")

    return long_df

def calculate_independent_index(
    municipality,
    scenario_key):
    weight_factors = {
        "HW_GasBoiler": 0.79,
        "SH_GasBoiler": 0.94,
        "SH_HydrogenBoiler": 0.88,
        "SH_WoodBoiler": 0.72,
        "SH_OilBoiler": 0.90,
        "HW_OilBoiler": 0.75,
        "elec_import_unit": 1.00,
    }

    import_sum_path = os.path.join(
        "data",
        municipality,
        "operation",
        scenario_key,
        "energy_import_flow_municipality_level_data.xlsx",
    )

    if not os.path.exists(import_sum_path):
        return pd.DataFrame(columns=["year-month", "independent_index", "scenario"])

    time_series_df = pd.read_excel(import_sum_path)

    if "time" not in time_series_df.columns or "total_demand_MW" not in time_series_df.columns:
        raise ValueError("Input file must contain 'time' and 'total_demand_MW' columns.")

    time_series_df["time"] = pd.to_datetime(time_series_df["time"], errors="coerce")
    time_series_df = time_series_df.dropna(subset=["time"]).copy()

    time_series_df["total_demand_MW"] = pd.to_numeric(
        time_series_df["total_demand_MW"],
        errors="coerce",
    ).fillna(0)

    import_cols = [
        col for col in time_series_df.columns
        if col not in ["time", "total_demand_MW"]
    ]

    for col in import_cols:
        time_series_df[col] = pd.to_numeric(
            time_series_df[col],
            errors="coerce",
        ).fillna(0)

    # Calculate weighted import for each time step
    time_series_df["weighted_import"] = sum(
        time_series_df[col] * weight_factors.get(col, 1)
        for col in import_cols
    )

    # Keep the column name as "year-month", but use quarterly labels
    time_series_df["year-month"] = (
        time_series_df["time"].dt.year.astype(str)
        + "-Q"
        + time_series_df["time"].dt.quarter.astype(str)
    )

    # Aggregate first, then calculate independent index
    result_df = (
        time_series_df
        .groupby("year-month", as_index=False)
        .agg(
            total_demand_MW=("total_demand_MW", "sum"),
            weighted_import=("weighted_import", "sum"),
        )
    )

    result_df["independent_index"] = result_df.apply(
        lambda row: 1
        if row["total_demand_MW"] == 0
        else 1 - row["weighted_import"] / row["total_demand_MW"],
        axis=1,
    )

    result_df["independent_index"] = result_df["independent_index"].clip(
        lower=0,
        upper=1,
    )

    result_df["scenario"] = scenario_dict.get(scenario_key, scenario_key)

    return result_df[["year-month", "independent_index", "scenario"]]
