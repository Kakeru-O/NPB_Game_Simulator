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

# 投手（架空の選手）の打撃成績の仮の値
PITCHER_STATS = {
    "Player": "投手",
    "1B_ratio": 0.01,  # 単打率
    "2B_ratio": 0.001, # 二塁打率
    "3B_ratio": 0.0001, # 三塁打率
    "HR_ratio": 0.0001, # 本塁打率
    "BB+HBP_ratio": 0.02, # 四死球率
    "SO_ratio": 0.5,   # 三振率 (Out_ratioから逆算されるため、ここでは使用しないが参考として)
    "Ground_Out_ratio": 0.2, # ゴロアウト率 (Out_ratioから逆算されるため、ここでは使用しないが参考として)
    "Fly_Out_ratio": 0.2, # フライアウト率 (Out_ratioから逆算されるため、ここでは使用しないが参考として)
    "Out_ratio": 0.9688, # アウト率 (1 - (1B+2B+3B+HR+BB+HBP) = 1 - (0.01+0.001+0.0001+0.0001+0.02) = 0.9688)
    "Speed": 0 # スピード
}