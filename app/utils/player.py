# src/main/utils/player.py

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any

from .constants import EVENT_TYPES, EVENT_CONFIG, STAT_KEYS

class Player:
    """野球選手とその成績を管理するクラス。"""
    def __init__(self, name: str, probabilities: List[float]):
        """
        Args:
            name (str): 選手名。
            probabilities (List[float]): 打席結果の確率のリスト。
                [single, double, triple, homerun, walk, out] の順。
        """
        if len(probabilities) != len(EVENT_TYPES):
            raise ValueError(f"Probabilities list must have {len(EVENT_TYPES)} elements, corresponding to {EVENT_TYPES}")
        if not np.isclose(sum(probabilities), 1.0):
            raise ValueError("Probabilities must sum to 1.0")

        self.name = name
        self.probabilities = np.array(probabilities)
        self.stats: Dict[str, int] = {}
        self.reset_stats()

    def reset_stats(self):
        """選手の成績を初期化する。"""
        for key in STAT_KEYS:
            self.stats[key] = 0

    def simulate_at_bat(self) -> Tuple[str, int]:
        """
        1打席の結果をシミュレートし、成績を更新する。

        Returns:
            Tuple[str, int]: (打席結果のイベント名, 打者と走者が進む塁の数)
        """
        event_type: str = np.random.choice(EVENT_TYPES, p=self.probabilities)
        event_details = EVENT_CONFIG[event_type]

        self.stats["plate_appearances"] += 1

        if not event_details["is_walk"]:
            self.stats["at_bats"] += 1

        if event_details["is_hit"]:
            self.stats["hits"] += 1
            self.stats["slugging_points"] += event_details["slugging_value"]

        if event_details["is_walk"]:
            self.stats["walks"] +=1

        stat_counter_key = event_details["stat_counter_key"]
        if stat_counter_key:
            self.stats[stat_counter_key] += 1
            
        return event_type, event_details["bases_to_advance"]

    def _get_stat(self, stat_name: str) -> int:
        """指定された統計値を取得する。存在しない場合は0を返す。"""
        return self.stats.get(stat_name, 0)

    def batting_average(self) -> float:
        """打率 (安打 / 打数) を計算する。"""
        hits = self._get_stat("hits")
        at_bats = self._get_stat("at_bats")
        return hits / at_bats if at_bats > 0 else 0.0

    def on_base_percentage(self) -> float:
        """出塁率 ((安打 + 四球) / 打席数) を計算する。"""
        hits = self._get_stat("hits")
        walks = self._get_stat("walks")
        plate_appearances = self._get_stat("plate_appearances")
        return (hits + walks) / plate_appearances if plate_appearances > 0 else 0.0

    def slugging_percentage(self) -> float:
        """長打率 (塁打数 / 打数) を計算する。"""
        slugging_points = self._get_stat("slugging_points")
        at_bats = self._get_stat("at_bats")
        return slugging_points / at_bats if at_bats > 0 else 0.0

    def ops(self) -> float:
        """OPS (出塁率 + 長打率) を計算する。"""
        return self.on_base_percentage() + self.slugging_percentage()