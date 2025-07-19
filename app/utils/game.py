# src/main/utils/game.py

import numpy as np
from collections import deque
from typing import List, Tuple, Any

from .constants import EVENT_CONFIG
from .player import Player

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
        self.bases: List[Player | None] = [None, None, None]  # [一塁, 二塁, 三塁] 各塁にいるPlayerオブジェクト、またはNone
        self.outs = 0
        self.game_log: List[List[Tuple[str, str, int]]] = [] # イニングごとの (選手名, 結果, 打点) のログ
        

    def _reset_inning_state(self):
        """イニング開始時に状態をリセットする。"""
        self.outs = 0
        self.bases = [None, None, None]

    

    def should_advance_extra_base(self, runner: Player, current_base_index: int, event_type: str)->bool:
        """
        ランナーが追加の塁に進むべきかを判定するヘルパー関数。
        """
        # ベース確率 (仮の値、調整が必要)
        base_prob = 0.0 # デフォルトは進まない

        if event_type == "single":
            if current_base_index == 0: # 一塁走者が3塁へ
                base_prob = 0.1
            elif current_base_index == 1: # 二塁走者が本塁へ
                base_prob = 0.1 # シングルヒットで二塁から本塁へ
            
        elif event_type == "double":
            if current_base_index == 0: # 一塁走者が本塁へ
                base_prob = 0.1
        
        # Speedによる調整 (仮の値、調整が必要)
        # Speedが正の値なら確率増加、負の値なら確率減少
        speed_factor = 0.02 # Speed 1につき2%変化
        adjusted_prob = base_prob + (runner.speed * speed_factor)

        # アウトカウントによる調整 (仮の値、調整が必要)
        if self.outs == 0:
            adjusted_prob *= 0.9 # 0アウトではやや慎重
        elif self.outs == 2:
            adjusted_prob *= 1.1 # 2アウトでは積極的に

        # 確率のクランプ
        adjusted_prob = max(0.0, min(1.0, adjusted_prob))

        return np.random.rand() < adjusted_prob



    def advance_runners(self, batter: Player, event_type: str) -> int:
        """
        走者を進塁させ、得点を計算する。
        Args:
            batter (Player): 打者オブジェクト。
            event_type (str): 打席結果のイベントタイプ。
        Returns:
            int: このプレーで発生した得点。
        """
        runs_scored = 0
        new_bases: List[Player | None] = [None, None, None] # 新しい塁の状態

        # 走者の移動を処理
        # 三塁走者から順に処理することで、進塁による衝突を防ぐ
        # 四死球の場合の特殊処理
        if event_type == "walk":
            # # 満塁の場合、三塁走者が本塁生還
            # if self.bases[0] is not None and self.bases[1] is not None and self.bases[2] is not None:
            #     runs_scored += 1
            
            # # 塁上の走者を一つずつ進める
            # if self.bases[1] is not None: # 二塁走者が三塁へ
            #     new_bases[2] = self.bases[1]
            # if self.bases[0] is not None: # 一塁走者が二塁へ
            #     new_bases[1] = self.bases[0]
            # new_bases[0] = batter # 打者が一塁へ
            if self.bases[2] is not None:
                if self.bases[1] is not None: 
                    if self.bases[0] is not None:# 満塁
                        runs_scored += 1
                        new_bases[2] = self.bases[1]
                        new_bases[1] = self.bases[0]
                    # 2,3塁はそのまま
                elif self.bases[0] is not None:# 1,3塁
                    new_bases[1] = self.bases[0]

            else:
                if self.bases[1] is not None:
                    if self.bases[0] is not None:# 1,2塁
                        new_bases[2] = self.bases[1]
                        new_bases[1] = self.bases[0]
                        
                else:
                    if self.bases[0] is not None:#1塁
                        new_bases[1] = self.bases[0]
                        
            new_bases[0] = batter # 打者が一塁へ


        elif event_type == "homerun":
            runs_scored += 1 # 打者自身の得点
            # 塁上の走者も全て本塁生還
            for i in range(3):
                if self.bases[i] is not None:
                    runs_scored += 1
            self.bases = [None, None, None]  # 全ての走者が帰還するため塁は空になる
            return runs_scored  # この分岐では早期リターン

        elif event_type == '3B':
            # All runners score
            for i in range(0, 3):
                if self.bases[i] is not None:
                    runs_scored += 1
                    self.bases[i] = None
            # Batter to 3rd
            new_bases[2] = batter
        
        elif event_type == '2B':
            # 3rd, 2nd base runners score
            if self.bases[2] is not None: runs_scored += 1
            if self.bases[1] is not None: runs_scored += 1
            self.bases[2] = None
            self.bases[1] = None
            new_bases[2] = None
            new_bases[1] = None
            # 1st base runner
            if self.bases[0]is not None:
                if self.should_advance_extra_base(self.bases[0], 0, event_type):
                    runs_scored += 1
                else:
                    new_bases[2] = self.bases[0]
                new_bases[0] = None
            # Batter to 2nd
            new_bases[1] = batter

        else:
            # 3rd base runners score
            if self.bases[2] is not None: runs_scored += 1
            self.bases[2] = None
            new_bases[2] = None
            if self.bases[1] is not None:
                if self.should_advance_extra_base(self.bases[1], 1, event_type):
                    runs_scored += 1
                else:
                    new_bases[2] = self.bases[1]
            self.bases[1] = None
            new_bases[1] = None
            if self.bases[0] is not None:
                if self.should_advance_extra_base(self.bases[0], 0, event_type):
                    new_bases[2] = self.bases[0]
                else:
                    new_bases[1] = self.bases[0]
                new_bases[0] = None
            # Batter to 1st
            new_bases[0] = batter
                
            
        self.bases = new_bases
        
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
                runs = self.advance_runners(current_player, event_type)
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
        
        # simulate_gameの最後にoutsとbasesをリセット
        self.outs = 0
        self.bases = [None, None, None]

        return self.score, self.game_log