from pathlib import Path

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