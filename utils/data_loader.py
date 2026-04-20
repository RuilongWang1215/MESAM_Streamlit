from pathlib import Path
import pandas as pd
from config import DATA_DIR


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


def load_all_summary_data():
    rows = []
    for municipality in get_municipality_list():
        df = load_summary_data(municipality)
        if not df.empty:
            df["municipality"] = municipality
            rows.append(df)
    if rows:
        return pd.concat(rows, ignore_index=True)
    return pd.DataFrame()