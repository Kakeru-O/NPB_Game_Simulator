# src/main/utils/game.py

import numpy as np
from collections import deque
from typing import List, Tuple, Any

from app.utils.constants import EVENT_CONFIG
from app.utils.player import Player

class BaseballGame:
    """野球の試合をシミュレートするクラス。"""
    def __init__(self, players: List[Player]):
        """
        Args:
            players (List[Player]): 試合に出場する選手のリスト。打順もこのリスト順に従う。
        """
        self.players = players # 初期打順
        self.current_lineup: deque[Player] = deque()
        self.score = 0
        self.bases = np.zeros(3, dtype=int)  # [一塁, 二塁, 三塁]
        self.outs = 0
        self.game_log: List[List[Tuple[str, str, int]]] = [] # イニングごとの (選手名, 結果, 打点) のログ
        

    def _reset_inning_state(self):
        """イニング開始時に状態をリセットする。"""
        self.outs = 0
        self.bases = np.zeros(3, dtype=int)

    def advance_runners(self, batter_advances: int) -> int:
        """
        走者を進塁させ、得点を計算する。
        打者自身もこのメソッド内で進塁処理される。

        Args:
            batter_advances (int): 打者が進む塁の数 (例: single=1, homerun=4, walk=1)。

        Returns:
            int: このプレーで発生した得点。
        """
        runs_scored = 0

        # 塁上の走者を進める (三塁から順に処理)
        for i in range(2, -1, -1): # i = 2 (三塁), 1 (二塁), 0 (一塁)
            if self.bases[i] == 1: # その塁に走者がいる場合
                self.bases[i] = 0 # 元の塁から走者を動かす
                new_base_index = i + batter_advances
                if new_base_index >= 3: # 本塁生還
                    runs_scored += 1
                else:
                    self.bases[new_base_index] = 1 # 新しい塁へ

        # 打者を進める
        if batter_advances == 4: # ホームラン
            runs_scored += 1
        elif batter_advances > 0: # ホームラン以外の安打または四球
            self.bases[batter_advances - 1] = 1 # 打者を新しい塁へ (0-indexed)
        
        return runs_scored

    def play_inning(self):
        """1イニング分の攻撃をシミュレートする。"""
        self._reset_inning_state()
        inning_log: List[Tuple[str, str, int]] = [] 

        if not self.current_lineup: # 初回または新しい試合
            self.current_lineup = deque(self.players)


        while self.outs < 3:
            if not self.current_lineup: # 万が一のため (通常は起こらない)
                break 
            
            current_player = self.current_lineup.popleft()
            event_type, bases_to_advance = current_player.simulate_at_bat()
            
            event_details = EVENT_CONFIG[event_type]
            runs = 0
            if event_details["is_out"]:
                self.outs += 1
            else:
                runs = self.advance_runners(bases_to_advance)
                self.score += runs
                current_player.stats["runs_batted_in"] += runs


            inning_log.append((current_player.name, event_type, runs))

            
            self.current_lineup.append(current_player) # 打順の最後に再度追加

        self.game_log.append(inning_log)

    def simulate_game(self, num_innings: int = 9) -> Tuple[int, List[List[Tuple[str, str, int]]]]:
        """
        指定されたイニング数の試合をシミュレートする。

        Args:
            num_innings (int): 試合のイニング数。デフォルトは9。

        Returns:
            Tuple[int, List[List[Tuple[str, str]]]]: (最終スコア, ゲームログ)
        """
        self.score = 0
        self.game_log = []
        # 各試合開始時に打順をセット
        self.current_lineup = deque(self.players) 

        for _ in range(num_innings):
            self.play_inning()
        return self.score, self.game_log