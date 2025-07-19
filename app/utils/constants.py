# src/main/utils/constants.py

from typing import Any, Dict, List

# 打席結果の種類 (CSVの確率の順序と一致させる)
EVENT_TYPES: List[str] = ["single", "double", "triple", "homerun", "walk", "out"]

# 各打席結果の詳細設定
EVENT_CONFIG: Dict[str, Dict[str, Any]] = {
    "single":  {"is_hit": True,  "is_walk": False, "is_out": False, "bases_to_advance": 1, "slugging_value": 1, "stat_counter_key": "singles"},
    "double":  {"is_hit": True,  "is_walk": False, "is_out": False, "bases_to_advance": 2, "slugging_value": 2, "stat_counter_key": "doubles"},
    "triple":  {"is_hit": True,  "is_walk": False, "is_out": False, "bases_to_advance": 3, "slugging_value": 3, "stat_counter_key": "triples"},
    "homerun": {"is_hit": True,  "is_walk": False, "is_out": False, "bases_to_advance": 4, "slugging_value": 4, "stat_counter_key": "homeruns"},
    "walk":    {"is_hit": False, "is_walk": True,  "is_out": False, "bases_to_advance": 1, "slugging_value": 0, "stat_counter_key": "walks"},
    "out":     {"is_hit": False, "is_walk": False, "is_out": True,  "bases_to_advance": 0, "slugging_value": 0, "stat_counter_key": None},
}

STAT_KEYS: List[str] = [
    "hits", "at_bats", "walks", "plate_appearances", "runs_batted_in",
    "singles", "doubles", "triples", "homeruns", "slugging_points"
]