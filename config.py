from pathlib import Path
import seaborn as sns

DATA_DIR = Path("data")

DEFAULT_SCENARIO = "base"
DEFAULT_PAGE_SIZE = "wide"

scenario_dict = {
    "base": "Baseline",
    "cp_cu": "Technical Potential",
    "cp_dr": "Discount Rate",
    "all": "All"
}

NUTS2_dict = {
    "Terre di Pedemonte": 7,
    "Verzasca": 7,
    "Ascona": 7,
    "Diessenhofen": 5,
    "Lüterkofen-Ichertswil": 2,
    "Bowil": 2,
    "Brienz (BE)": 2,
    "Rickenbach (LU)": 6,
    "Mörel-Filet": 1,
    "Hermenches": 1,
    "Wohlen (AG)": 3,
    "Arisdorf": 3
}

region_dict = {
1: 'Lake Geneva',
2: 'Espace Mittelland',
3: 'Northwest Switzerland',
4: 'Zurich',
5: 'East Switzerland',
6: 'Central Switzerland',
7: 'Ticino'
}

colors = sns.color_palette("Set2", n_colors=7)
region_color_dict = {
    'Lake Geneva': colors[0],
    'Espace Mittelland': colors[1],
    'Northwest Switzerland': colors[2],
    'Zurich': colors[3],
    'East Switzerland': colors[4],
    'Central Switzerland': colors[5],
    'Ticino': colors[6]
}

flow_type_mapping = {
        "elec": "electricity",
        "CO2": "carbon dioxide",
        "HW": "hot water",
        "SH": "space heating",
    }