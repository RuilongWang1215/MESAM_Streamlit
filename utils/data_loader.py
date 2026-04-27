from pathlib import Path
import pandas as pd
from config import DATA_DIR, scenario_dict, NUTS2_dict
from config import flow_type_mapping

def sort_row(data: pd.DataFrame) -> pd.DataFrame:
    scenario_order = list(scenario_dict.values())
    data = data.sort_values(
        by=["NUTS2", "municipality", "scenario"],
        key=lambda x: x.map({v: i for i, v in enumerate(scenario_order)}) if x.name == "scenario" else x
    )
    return data

def _clean_time_column(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    # only keep year part if the time column contains datetime
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce').dt.year.fillna(df[time_col])
    return df

def _clean_investment_data(df: pd.DataFrame) -> pd.DataFrame:
    investment_cols = [col for col in df.columns if "invested_available_unit" in col.lower()]
    techs = df['name'].unique()
    for tech in techs: 
        sub_df = df[df['name'] == tech]
        # if all the investment cols for this tech are zero for all years, then we can drop this tech from the table
        if sub_df[investment_cols].sum().sum() == 0:
            df = df[df['name'] != tech]
    return df

def _rename_investment_columns(df: pd.DataFrame) -> pd.DataFrame:
    # rename scale_MW to scale per unit (MW)
    df = df.rename(columns={'scale_MW': 'scale per unit (MW)'})
    return df

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

def load_aggregated_investment_data(municipality):
    file_path = DATA_DIR / municipality / "investment_decision" / "aggregated_investment_decision.xlsx"
    if file_path.exists():
        df = pd.read_excel(file_path)
        df = _clean_time_column(df, "time")
        df = _clean_investment_data(df)
        df = _rename_investment_columns(df)
        # put name, scale per unit (MW), time in the front 
        cols = df.columns.tolist()
        new_order = ["name", "scale per unit (MW)", "time"] + [col for col in cols if col not in ["name", "scale per unit (MW)", "time"]]
        df = df[new_order]
        return df
    return pd.DataFrame()

def electrolyzer_investment_decision(municipality):
    # input: municipality name
    # output: boolean value indicating whether there is any investment in electrolyzer
    df = load_aggregated_investment_data(municipality)
    if df.empty:
        return False
    if "electrolyzer" in df["name"].str.lower().values:
        return True
    return False

def get_operation_level(municipality:str, scenario_name: str):
    levels = []
    path = DATA_DIR / municipality / "operation" / scenario_name 
    # read the levels from the file names in this folder 
    # level is the part after first _ 
    if path.exists():
        for file in path.iterdir():
            if file.is_file() and file.suffix in [".xlsx", ".csv"]:
                level = file.stem.split("_")[1] if "_" in file.stem else file.stem
                levels.append(level)
    levels = list(set(levels))
    return sorted(levels, reverse=True) # show building first, then district, then municipality

def get_flow_types(municipality:str, scenario_name: str, level: str):
    flow_types = []
    path = DATA_DIR / municipality / "operation" / scenario_name 
    if path.exists():
        for file in path.iterdir():
            if file.is_file() and file.suffix in [".xlsx", ".csv"] and level in file.stem:
                parts = file.stem.split("_")
                flow_type = parts[0]
                flow_types.append(flow_type)
    flow_types = list(set(flow_types))
    flow_types = [flow_type_mapping.get(ft, ft) for ft in flow_types]
    return sorted(flow_types)

def load_operation_data(municipality, scenario, level, flow_type, sub_type=None):
    path = DATA_DIR / municipality / "operation" / scenario
    if path.exists():
        flow_type_key = None
        for key in flow_type_mapping.keys():
            if flow_type_mapping[key] == flow_type:
                flow_type_key = key
                break
        file_name = f"{flow_type_key}_{level}_level_data.xlsx"
        file_path = path / file_name
        if file_path.exists():
            if sub_type is not None:
                df = pd.read_excel(file_path, sheet_name=f"{sub_type}")
            else:
                df = pd.read_excel(file_path)
            return df
    return pd.DataFrame()

def get_sub_type(municipality, scenario, flow_type, level = "building"):
    # read the sheet names in the file flow_type_building_level_data.xlsx, the building types are the part after second _ and before _level
    path = DATA_DIR / municipality / "operation" / scenario
    if path.exists():
        flow_type_key = None
        for key in flow_type_mapping.keys():
            if flow_type_mapping[key] == flow_type:
                flow_type_key = key
                break
        file_name = f"{flow_type_key}_{level}_level_data.xlsx"
        file_path = path / file_name
        if file_path.exists():
            xls = pd.ExcelFile(file_path)
            sub_types = xls.sheet_names
            return sorted(list(set(sub_types)))    

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
    all_data = sort_row(all_data)
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
    comparison = get_non_base_cost_comparison(comparison)
    comparison['NUTS2'] = comparison['municipality'].map(NUTS2_dict).fillna("Unknown")
    return comparison

def get_non_base_cost_comparison(comparison_df: pd.DataFrame) -> pd.DataFrame:
    data = comparison_df.copy()
    return data[data["scenario"] != "Baseline"].copy()

def load_re_potential(municipality):
    data = pd.read_excel(DATA_DIR / "summary_table_by_sheet.xlsx")
    data = data[data["muni_name"].eq(municipality)]

    potential_cols = data.filter(regex="(?i)potential").columns

    potentials = {
        "Baseline": "base_scenario",
        "Discount Rate": "base_scenario",
        "Technical Potential": "Technical_potential_scenario",
        "All": "Technical_potential_scenario"
    }

    rows = []
    for scenario in scenario_dict.values():
        sheet = potentials.get(scenario)
        if sheet is None:
            continue

        values = data.loc[data["sheet_name"].eq(sheet), potential_cols].iloc[0]
        values.fillna(0, inplace=True)  
        rows.append({"scenario": scenario, **values.to_dict()})

    return pd.DataFrame(rows)
        
