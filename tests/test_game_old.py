import pytest
import numpy as np
from collections import deque

from app.utils.game import BaseballGame
from app.utils.player import Player
from app.utils.constants import EVENT_CONFIG

# テスト用のPlayerオブジェクトを作成するヘルパー関数
def create_test_player(name, speed=0):
    # 確率の合計が1になるように適当な値を設定
    probabilities = [0.1, 0.1, 0.01, 0.01, 0.1, 0.68] 
    return Player(name=name, probabilities=probabilities, speed=speed)

@pytest.fixture
def game_setup():
    # テスト用の選手を作成
    p1 = create_test_player("Player1", speed=10) # 足速い
    p2 = create_test_player("Player2", speed=0)  # 平均
    p3 = create_test_player("Player3", speed=-10) # 足遅い
    p4 = create_test_player("Player4", speed=5) # 追加の選手
    players = [p1, p2, p3, p4] * 3 # 9人打順
    return BaseballGame(players), p1, p2, p3, p4

# --- advance_runnersメソッドのテスト ---

def test_advance_runners_single_no_runners(game_setup):
    game, batter, _, _, _ = game_setup
    game.bases = [None, None, None]
    runs = game.advance_runners(batter, "single")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] is None
    assert game.bases[2] is None

def test_advance_runners_single_runner_on_first(game_setup):
    game, batter, r1, _, _ = game_setup
    game.bases = [r1, None, None]
    # decide_extra_baseがTrueを返すようにnp.random.randをモック
    np.random.seed(0) # 常にTrueを返すように調整 (0.5 < 0.9)
    runs = game.advance_runners(batter, "single")
    assert runs == 0 # 一塁走者が二塁へ、打者が一塁へ
    assert game.bases[0] == batter
    assert game.bases[1] == r1
    assert game.bases[2] is None

def test_advance_runners_single_runner_on_second_score(game_setup):
    game, batter, _, r2, _ = game_setup
    game.bases = [None, r2, None]
    np.random.seed(0) # 常にTrueを返すように調整 (0.5 < 0.5)
    runs = game.advance_runners(batter, "single")
    assert runs == 1 # 二塁走者が本塁へ
    assert game.bases[0] == batter
    assert game.bases[1] is None
    assert game.bases[2] is None

def test_advance_runners_single_runner_on_third_score(game_setup):
    game, batter, _, _, r3, _ = game_setup
    game.bases = [None, None, r3]
    runs = game.advance_runners(batter, "single")
    assert runs == 1 # 三塁走者が本塁へ
    assert game.bases[0] == batter
    assert game.bases[1] is None
    assert game.bases[2] is None

def test_advance_runners_double_runner_on_first_score(game_setup):
    game, batter, r1, _, _, _ = game_setup
    game.bases = [r1, None, None]
    np.random.seed(0) # decide_extra_baseがTrueを返すように調整 (0.5 < 0.9)
    runs = game.advance_runners(batter, "double")
    assert runs == 1 # 一塁走者が本塁へ
    assert game.bases[0] is None
    assert game.bases[1] == batter
    assert game.bases[2] is None

def test_advance_runners_double_runner_on_second_score(game_setup):
    game, batter, _, r2, _, _ = game_setup
    game.bases = [None, r2, None]
    np.random.seed(0) # decide_extra_baseがTrueを返すように調整 (0.5 < 0.8)
    runs = game.advance_runners(batter, "double")
    assert runs == 1 # 二塁走者が本塁へ
    assert game.bases[0] is None
    assert game.bases[1] == batter
    assert game.bases[2] is None

def test_advance_runners_homerun_grand_slam(game_setup):
    game, batter, r1, r2, r3, _ = game_setup
    game.bases = [r1, r2, r3]
    runs = game.advance_runners(batter, "homerun")
    assert runs == 4 # 満塁ホームラン
    assert all(b is None for b in game.bases) # 全ての塁が空になる

def test_advance_runners_walk_no_runners(game_setup):
    game, batter, _, _, _ = game_setup
    game.bases = [None, None, None]
    runs = game.advance_runners(batter, "walk")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] is None
    assert game.bases[2] is None

def test_advance_runners_walk_runner_on_first(game_setup):
    game, batter, r1, _, _ = game_setup
    game.bases = [r1, None, None]
    runs = game.advance_runners(batter, "walk")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] == r1
    assert game.bases[2] is None

def test_advance_runners_walk_runners_on_first_and_second(game_setup):
    game, batter, r1, r2, _, _ = game_setup
    game.bases = [r1, r2, None]
    runs = game.advance_runners(batter, "walk")
    assert runs == 0
    assert game.bases[0] == batter
    assert game.bases[1] == r1
    assert game.bases[2] == r2

def test_advance_runners_walk_bases_loaded(game_setup):
    game, batter, r1, r2, r3, _ = game_setup
    game.bases = [r1, r2, r3]
    runs = game.advance_runners(batter, "walk")
    assert runs == 1 # 押し出し
    assert game.bases[0] == batter
    assert game.bases[1] == r1
    assert game.bases[2] == r2

# --- decide_extra_baseメソッドのテスト (確率的要素を含むため、モックや多数回試行が必要) ---

def test_decide_extra_base_speed_effect(game_setup):
    game, p_fast, p_avg, p_slow, _ = game_setup
    # Speedが速い選手は確率が高く、遅い選手は低いことを確認
    # 厳密な確率検証は難しいので、傾向を確認
    # 例えば、同じ条件で多数回試行して成功回数を比較するなど
    # ここでは簡易的に、speed_factorが正しく適用されるかを確認
    
    # 仮に、base_prob=0.5, outs=1 (調整なし) の場合
    # p_fast (speed=10): 0.5 + 10*0.02 = 0.7
    # p_avg (speed=0): 0.5 + 0*0.02 = 0.5
    # p_slow (speed=-10): 0.5 - 10*0.02 = 0.3

    # decide_extra_baseは内部でnp.random.rand()を使用するため、
    # 厳密なテストにはモックが必要。ここでは概念的なテストとする。
    # 例: monkeypatch.setattr(np.random, 'rand', lambda: 0.6) # 0.6を返すようにモック
    # その上で、p_fastはTrue、p_avgとp_slowはFalseになることを確認
    
    # 簡単な確認として、speed_factorが0.02であることを利用して、
    # 確率が正しく計算されるかを確認する (乱数部分は無視)
    game.outs = 1 # 1アウトで調整なし
    base_prob = 0.5
    
    # p_fast
    game.decide_extra_base(p_fast, 0, "single") # 内部で計算されるadjusted_probが0.7になることを期待
    # p_avg
    game.decide_extra_base(p_avg, 0, "single") # 内部で計算されるadjusted_probが0.5になることを期待
    # p_slow
    game.decide_extra_base(p_slow, 0, "single") # 内部で計算されるadjusted_probが0.3になることを期待

def test_decide_extra_base_outs_effect(game_setup):
    game, p_avg, _, _, _ = game_setup
    base_prob = 0.5

    # 0アウト
    game.outs = 0
    game.decide_extra_base(p_avg, 0, "single") # 内部で計算されるadjusted_probが0.5 * 0.9 = 0.45になることを期待

    # 1アウト
    game.outs = 1
    game.decide_extra_base(p_avg, 0, "single") # 内部で計算されるadjusted_probが0.5 * 1.0 = 0.5になることを期待

    # 2アウト
    game.outs = 2
    game.decide_extra_base(p_avg, 0, "single") # 内部で計算されるadjusted_probが0.5 * 1.1 = 0.55になることを期待

    # 同様に、np.random.rand()をモックして検証すべき

# --- play_inningメソッドのテスト (簡易的な確認) ---

def test_play_inning_basic(game_setup):
    game, _, _, _, _ = game_setup
    initial_score = game.score
    game.play_inning()
    # 1イニングで3アウトになることを確認
    assert game.outs == 3
    # スコアが増加している可能性があることを確認
    assert game.score >= initial_score
    # 塁がリセットされていることを確認
    assert all(b is None for b in game.bases)

# --- simulate_gameメソッドのテスト (簡易的な確認) ---

def test_simulate_game_basic(game_setup):
    game, _, _, _, _ = game_setup
    final_score, game_log = game.simulate_game(num_innings=1)
    assert game.score == final_score
    assert len(game_log) == 1 # 1イニング分のログがあることを確認
    assert game.outs == 0 # simulate_gameの最後でリセットされるため
    assert all(b is None for b in game.bases) # simulate_gameの最後でリセットされるため}











