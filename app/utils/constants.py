# src/main/utils/constants.py

from typing import Any, Dict, List

# 打席結果の種類 (CSVの確率の順序と一致させる)
EVENT_TYPES: List[str] = ["single", "double", "triple", "homerun", "walk", "strikeout", "ground_out", "fly_out"]

# 各打席結果の詳細設定
EVENT_CONFIG: Dict[str, Dict[str, Any]] = {
    "single":  {"is_hit": True,  "is_walk": False, "is_out": False, "bases_to_advance": 1, "slugging_value": 1, "stat_counter_key": "singles"},
    "double":  {"is_hit": True,  "is_walk": False, "is_out": False, "bases_to_advance": 2, "slugging_value": 2, "stat_counter_key": "doubles"},
    "triple":  {"is_hit": True,  "is_walk": False, "is_out": False, "bases_to_advance": 3, "slugging_value": 3, "stat_counter_key": "triples"},
    "homerun": {"is_hit": True,  "is_walk": False, "is_out": False, "bases_to_advance": 4, "slugging_value": 4, "stat_counter_key": "homeruns"},
    "walk":    {"is_hit": False, "is_walk": True,  "is_out": False, "bases_to_advance": 1, "slugging_value": 0, "stat_counter_key": "walks"},
    "strikeout": {"is_hit": False, "is_walk": False, "is_out": True,  "bases_to_advance": 0, "slugging_value": 0, "stat_counter_key": None},
    "ground_out": {"is_hit": False, "is_walk": False, "is_out": True,  "bases_to_advance": 0, "slugging_value": 0, "stat_counter_key": None},
    "fly_out":  {"is_hit": False, "is_walk": False, "is_out": True,  "bases_to_advance": 0, "slugging_value": 0, "stat_counter_key": None},
}

STAT_KEYS: List[str] = [
    "hits", "at_bats", "walks", "plate_appearances", "runs_batted_in",
    "singles", "doubles", "triples", "homeruns", "slugging_points",
    "strikeouts", "double_plays", "sacrifice_bunts", "ground_out_advances", "bunt_fails", "sacrifice_flies"
]

# 投手（架空の選手）の打撃成績の仮の値
PITCHER_STATS = {
    "Player": "投手",
    "1B_ratio": 0.14,  # 単打率
    "2B_ratio": 0.01, # 二塁打率
    "3B_ratio": 0.0001, # 三塁打率
    "HR_ratio": 0.0001, # 本塁打率
    "BB+HBP_ratio": 0.02, # 四死球率
    "SO_ratio": 0.4298,   # 三振率
    "Ground_Out_ratio": 0.2, # ゴロアウト率
    "Fly_Out_ratio": 0.2, # フライアウト率
    "Speed": 0 # スピード
}

# シミュレーション確率設定
BUNT_ATTEMPT_FACTOR = 0.1 # 犠打試行確率の係数
SACRIFICE_BUNT_SUCCESS_RATE = 0.8 # 犠打成功率
DOUBLE_PLAY_PROBABILITY = 0.4 # 併殺打確率
GROUND_OUT_ADVANCE_PROBABILITY = 0.3 # 進塁打確率
SACRIFICE_FLY_PROBABILITY = 0.5 # 犠飛確率

# チームカラー設定
TEAM_COLORS = {
    "t": {"main": "#FFE201", "accent": "#000000"}, # 阪神 (黄、黒)
    "g": {"main": "#F97709", "accent": "#000000"}, # 巨人 (オレンジ、黒)
    "c": {"main": "#CD1919", "accent": "#FFFFFF"}, # 広島 (赤、白)
    "s": {"main": "#98C145", "accent": "#FFFFFF"}, # ヤクルト (濃い青、水色)
    "d": {"main": "#002569", "accent": "#FFFFFF"}, # 中日 (濃い青、グレー)
    "db": {"main": "#003F8E", "accent": "#FFFFFF"}, # DeNA (青、白)
    "f": {"main": "#01609A", "accent": "#FFFFFF"}, # 日本ハム (紺、赤)
    "e": {"main": "#8C0000", "accent": "#FFFFFF"}, # 楽天 (えんじ、白)
    "m": {"main": "#000000", "accent": "#FFFFFF"}, # ロッテ (黒、白)
    "l": {"main": "#051E46", "accent": "#FFFFFF"}, # 西武 (青、白)
    "b": {"main": "#002D6B", "accent": "#B88E4F"}, # オリックス (紺、茶)
    "h": {"main": "#FFB800", "accent": "#000000"}, # ソフトバンク (黄、黒)
}