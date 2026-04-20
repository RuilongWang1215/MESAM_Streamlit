from pathlib import Path
import pandas as pd
from config import DATA_DIR, scenario_dict, NUTS2_dict


def get_municipality_list():
    return sorted([p.name for p in DATA_DIR.iterdir() if p.is_dir()])


def get_scenarios_for_municipality(municipality):
    municipality_path = DATA_DIR / municipality / "operation"
    if not municipality_path.exists():
        return []
    return sorted([p.name for p in municipality_path.iterdir() if p.is_dir()])


def load_summary_data(municipality):
    file_path = DATA_DIR / municipality / "cost" / "cost_report.xlsx"
    if file_path.exists():
        return pd.read_excel(file_path)
    return pd.DataFrame()


def load_investment_data(municipality, scenario):
    file_path = DATA_DIR / municipality / "investment_decision" / "aggregated_investment_decision.xlsx"
    if file_path.exists():
        return pd.read_excel(file_path)
    return pd.DataFrame()


def load_operation_data(municipality, scenario):
    pass
    return pd.DataFrame()


import pandas as pd

def load_all_summary_data():
    rows = []

    for municipality in get_municipality_list():
        df = load_summary_data(municipality)
        if df is not None and not df.empty:
            df = df.copy()
            df["municipality"] = municipality
            rows.append(df)

    if not rows:
        return pd.DataFrame()

    all_data = pd.concat(rows, ignore_index=True)

    # map scenario names
    if "scenario" in all_data.columns:
        all_data["scenario"] = (
            all_data["scenario"]
            .map(scenario_dict)
            .fillna(all_data["scenario"])
        )

    # add NUTS2
    all_data["NUTS2"] = all_data["municipality"].map(NUTS2_dict).fillna("Unknown")

    # drop unnecessary columns if they exist
    cols_to_drop = [col for col in ["specific_cost (CHF/kWh)", "index"] if col in all_data.columns]
    if cols_to_drop:
        all_data = all_data.drop(columns=cols_to_drop)

    # convert only cost columns from kCHF to MCHF
    cost_cols_to_convert = [
        col for col in all_data.columns
        if col != "NUTS2" and pd.api.types.is_numeric_dtype(all_data[col])
    ]

    for col in cost_cols_to_convert:
        all_data[col] = all_data[col] / 1000
        all_data[col] = all_data[col].round(2)

    # round other numeric columns if needed, but do NOT divide them
    for col in all_data.select_dtypes(include="number").columns:
        if col not in ["total_costs"] and col not in cost_cols_to_convert:
            all_data[col] = all_data[col].round(2)

    # reorder columns
    priority_cols = ["municipality", "NUTS2", "scenario", "total_costs"]
    existing_priority_cols = [col for col in priority_cols if col in all_data.columns]
    remaining_cols = [col for col in all_data.columns if col not in existing_priority_cols]
    all_data = all_data[existing_priority_cols + remaining_cols]

    return all_data

def prepare_cost_comparison_vs_base(all_data: pd.DataFrame) -> pd.DataFrame:
    """
    Create a comparison table of scenario costs against the base scenario.

    Required columns:
    - municipality
    - scenario
    - total_costs
    """
    data = all_data.copy()

    required_cols = ["municipality", "scenario", "total_costs"]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # keep only necessary columns
    data = data[required_cols].copy()

    # remove missing rows
    data = data.dropna(subset=["municipality", "scenario", "total_costs"])

    # base cost for each municipality
    base_data = (
        data[data["scenario"] == "Baseline"][["municipality", "total_costs"]]
        .rename(columns={"total_costs": "base_cost"})
        .drop_duplicates(subset=["municipality"])
    )

    # merge base cost into all rows
    comparison = data.merge(base_data, on="municipality", how="left")

    # remove municipalities without base scenario
    comparison = comparison.dropna(subset=["base_cost"])

    # absolute and relative changes vs base
    comparison["cost_change"] = comparison["total_costs"] - comparison["base_cost"]
    comparison["cost_change_pct"] = comparison["cost_change"] / comparison["base_cost"] * 100

    # round for display
    comparison["total_costs"] = comparison["total_costs"].round(2)
    comparison["base_cost"] = comparison["base_cost"].round(2)
    comparison["cost_change"] = comparison["cost_change"].round(2)
    comparison["cost_change_pct"] = comparison["cost_change_pct"].round(2)

    return comparison

def get_non_base_cost_comparison(comparison_df: pd.DataFrame) -> pd.DataFrame:
    data = comparison_df.copy()
    return data[data["scenario"] != "Baseline"].copy()