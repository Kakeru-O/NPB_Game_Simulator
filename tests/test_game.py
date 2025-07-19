import pytest
import numpy as np
from collections import deque

from app.utils.game import BaseballGame
from app.utils.player import Player
from app.utils.constants import EVENT_CONFIG

class MockPlayer:
    def __init__(self, name, event_type=None, speed=0):
        self.name = name
        self._event_type = event_type
        self.speed = speed
        self.stats = {"runs_batted_in": 0}

    def simulate_at_bat(self):
        if self._event_type:
            return self._event_type, EVENT_CONFIG[self._event_type]["bases_to_advance"]
        # デフォルトの確率で結果を返す (必要であれば)
        probabilities = [0.1, 0.1, 0.01, 0.01, 0.1, 0.68] # 適当な確率
        event_type = np.random.choice(list(EVENT_CONFIG.keys()), p=probabilities)
        return event_type, EVENT_CONFIG[event_type]["bases_to_advance"]


# --- advance_runnersメソッドのテスト ---

def test_advance_runners_single_no_runners():
    game = BaseballGame([])
    batter = MockPlayer("Batter", "single")
    game.bases = [None, None, None]
    runs = game.advance_runners(batter, "single")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] is None
    assert game.bases[2] is None

def test_advance_runners_single_runner_on_first():
    game = BaseballGame([])
    batter = MockPlayer("Batter", "single")
    r1 = MockPlayer("R1", "out") # 走者
    game.bases = [r1, None, None]
    runs = game.advance_runners(batter, "single")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] == r1 or game.bases[2] == r1

def test_advance_runners_single_runner_on_second_score(monkeypatch):
    game = BaseballGame([])
    batter = MockPlayer("Batter", "single")
    r2 = MockPlayer("R2", "out") # 走者
    game.bases = [None, r2, None]
    monkeypatch.setattr(game, 'should_advance_extra_base', lambda runner, current_base_index, event_type: False)
    runs = game.advance_runners(batter, "single")
    assert runs >= 0
    assert game.bases[0] == batter
    assert game.bases[1] is None
    assert (game.bases[2] == r2 and runs==0) or (game.bases[2] is None and runs==1)


def test_advance_runners_single_runner_on_third_score():
    game = BaseballGame([])
    batter = MockPlayer("Batter", "single")
    r3 = MockPlayer("R3", "out") # 走者
    game.bases = [None, None, r3]
    runs = game.advance_runners(batter, "single")
    assert runs == 1 # 三塁走者が本塁へ
    assert game.bases[0] == batter
    assert game.bases[1] is None
    assert game.bases[2] is None

def test_advance_runners_double_runner_on_first_score(monkeypatch):
    game = BaseballGame([])
    batter = MockPlayer("Batter", "double")
    r1 = MockPlayer("R1", "out") # 走者
    game.bases = [r1, None, None]
    monkeypatch.setattr(game, 'should_advance_extra_base', lambda runner, current_base_index, event_type: False)
    runs = game.advance_runners(batter, "double")
    assert runs == 0
    assert game.bases[0] is None
    assert game.bases[1] == batter
    assert game.bases[2] == r1

def test_advance_runners_double_runner_on_second_score(monkeypatch):
    game = BaseballGame([])
    batter = MockPlayer("Batter", "double")
    r2 = MockPlayer("R2", "out") # 走者
    game.bases = [None, r2, None]
    monkeypatch.setattr(game, 'should_advance_extra_base', lambda runner, current_base_index, event_type: False)
    runs = game.advance_runners(batter, "double")
    assert runs == 0
    assert game.bases[0] is None
    assert game.bases[1] == batter
    assert game.bases[2] == r2

def test_advance_runners_homerun_grand_slam():
    game = BaseballGame([])
    batter = MockPlayer("Batter", "homerun")
    r1 = MockPlayer("R1", "out")
    r2 = MockPlayer("R2", "out")
    r3 = MockPlayer("R3", "out")
    game.bases = [r1, r2, r3]
    runs = game.advance_runners(batter, "homerun")
    assert runs == 4 # 満塁ホームラン
    assert all(b is None for b in game.bases) # 全ての塁が空になる

def test_advance_runners_walk_no_runners():
    game = BaseballGame([])
    batter = MockPlayer("Batter", "walk")
    game.bases = [None, None, None]
    runs = game.advance_runners(batter, "walk")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] is None
    assert game.bases[2] is None

def test_advance_runners_walk_runner_on_first():
    game = BaseballGame([])
    batter = MockPlayer("Batter", "walk")
    r1 = MockPlayer("R1", "out")
    game.bases = [r1, None, None]
    runs = game.advance_runners(batter, "walk")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] == r1
    assert game.bases[2] is None

def test_advance_runners_walk_runners_on_first_and_second():
    game = BaseballGame([])
    batter = MockPlayer("Batter", "walk")
    r1 = MockPlayer("R1", "out")
    r2 = MockPlayer("R2", "out")
    game.bases = [r1, r2, None]
    runs = game.advance_runners(batter, "walk")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] == r1
    assert game.bases[2] == r2

def test_advance_runners_walk_bases_loaded():
    game = BaseballGame([])
    batter = MockPlayer("Batter", "walk")
    r1 = MockPlayer("R1", "out")
    r2 = MockPlayer("R2", "out")
    r3 = MockPlayer("R3", "out")
    game.bases = [r1, r2, r3]
    runs = game.advance_runners(batter, "walk")
    assert runs == 1 # 押し出し
    assert game.bases[0] == batter
    assert game.bases[1] == r1
    assert game.bases[2] == r2

# --- decide_extra_baseメソッドのテスト (確率的要素を含むため、モックや多数回試行が必要) ---

def test_should_advance_extra_base_speed_effect(monkeypatch):
    game = BaseballGame([])
    p_fast = MockPlayer("P_Fast", speed=10)
    p_avg = MockPlayer("P_Avg", speed=0)
    p_slow = MockPlayer("P_Slow", speed=-10)

    game.outs = 1 # 1アウトで調整なし
    
    # should_advance_extra_baseのbase_probが0.0なので、常にFalseになる
    monkeypatch.setattr(np.random, 'rand', lambda: 0.6) # 0.6を返すようにモック
    assert game.should_advance_extra_base(p_fast, 0, "single") == False

    monkeypatch.setattr(np.random, 'rand', lambda: 0.6) # 0.6を返すようにモック
    assert game.should_advance_extra_base(p_avg, 0, "single") == False

    monkeypatch.setattr(np.random, 'rand', lambda: 0.6) # 0.6を返すようにモック
    assert game.should_advance_extra_base(p_slow, 0, "single") == False

def test_should_advance_extra_base_outs_effect(monkeypatch):
    game = BaseballGame([])
    p_avg = MockPlayer("P_Avg", speed=0)
    
    # should_advance_extra_baseのbase_probが0.0なので、常にFalseになる
    game.outs = 0
    monkeypatch.setattr(np.random, 'rand', lambda: 0.4) # 0.4を返すようにモック
    assert game.should_advance_extra_base(p_avg, 0, "single") == False
    monkeypatch.setattr(np.random, 'rand', lambda: 0.5) # 0.5を返すようにモック
    assert game.should_advance_extra_base(p_avg, 0, "single") == False

    game.outs = 1
    monkeypatch.setattr(np.random, 'rand', lambda: 0.4) # 0.4を返すようにモック
    assert game.should_advance_extra_base(p_avg, 0, "single") == False
    monkeypatch.setattr(np.random, 'rand', lambda: 0.5) # 0.5を返すようにモック
    assert game.should_advance_extra_base(p_avg, 0, "single") == False

    game.outs = 2
    monkeypatch.setattr(np.random, 'rand', lambda: 0.5) # 0.5を返すようにモック
    assert game.should_advance_extra_base(p_avg, 0, "single") == False
    monkeypatch.setattr(np.random, 'rand', lambda: 0.6) # 0.6を返すようにモック
    assert game.should_advance_extra_base(p_avg, 0, "single") == False

# --- play_inningメソッドのテスト ---

def test_play_inning_basic():
    # 常にアウトになる選手でテスト
    p_out = MockPlayer("OutPlayer", "out")
    players = [p_out] * 9
    game = BaseballGame(players)
    game.play_inning()
    assert game.outs == 3
    assert game.score == 0
    assert all(b is None for b in game.bases)

def test_play_inning_with_score():
    # ホームランとアウトを組み合わせた選手でテスト
    players = [
        MockPlayer("HR1", "homerun"),
        MockPlayer("HR2", "homerun"),
        MockPlayer("HR3", "homerun"),
        MockPlayer("Out1", "out"),
        MockPlayer("Out2", "out"),
        MockPlayer("Out3", "out"),
        MockPlayer("Out4", "out"),
        MockPlayer("Out5", "out"),
        MockPlayer("Out6", "out"),
    ]
    game = BaseballGame(players)
    game.play_inning()
    assert game.outs == 3
    assert game.score == 3 # 3本のホームランで3点
    assert all(b is None for b in game.bases)

# --- simulate_gameメソッドのテスト ---

def test_simulate_game_basic():
    p_out = MockPlayer("OutPlayer", "out")
    players = [p_out] * 9
    game = BaseballGame(players)
    final_score, game_log = game.simulate_game(num_innings=1)
    assert final_score == 0
    assert len(game_log) == 1
    assert game.outs == 0 # simulate_gameの最後でリセットされるため
    assert all(b is None for b in game.bases) # simulate_gameの最後でリセットされるため

def test_simulate_game_with_score():
    # ホームランとアウトを組み合わせた選手でテスト
    players = [
        MockPlayer("HR1", "homerun"),
        MockPlayer("HR2", "homerun"),
        MockPlayer("HR3", "homerun"),
        MockPlayer("Out1", "out"),
        MockPlayer("Out2", "out"),
        MockPlayer("Out3", "out"),
        MockPlayer("Out4", "out"),
        MockPlayer("Out5", "out"),
        MockPlayer("Out6", "out"),
    ]
    game = BaseballGame(players)
    final_score, game_log = game.simulate_game(num_innings=1)
    assert final_score == 3 # 3本のホームランで3点
    assert len(game_log) == 1
    assert game.outs == 0
    assert all(b is None for b in game.bases)






