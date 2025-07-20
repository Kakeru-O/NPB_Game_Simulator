

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any
import random

from .player import Player
from .game import BaseballGame
from .constants import EVENT_TYPES # CSV読み込み時の確認用

def load_players_from_csv(file_path: str, num_players: int = 9) -> List[Player]:
    """
    CSVファイルから選手データを読み込んでPlayerオブジェクトのリストを作成する。
    CSVファイルは特定のカラム名を持つことを想定:
    Player, 1B_ratio, 2B_ratio, 3B_ratio, HR_ratio, BB+HBP_ratio, Out_ratio

    Args:
        file_path (str): CSVファイルのパス。
        num_players (int): 読み込む選手の数。デフォルトは9。

    Returns:
        List[Player]: Playerオブジェクトのリスト。
    """
    try:
        data = pd.read_csv(file_path)
        if num_players > 0:
            data = data.head(num_players)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

    players = []
    expected_cols = ["Player", "1B_ratio", "2B_ratio", "3B_ratio", "HR_ratio", "BB+HBP_ratio", "Out_ratio", "Speed"]
    if not all(col in data.columns for col in expected_cols):
        print(f"Error: CSV file must contain columns: {expected_cols}")
        return []

    for _, row in data.iterrows():
        try:
            probabilities = [
                row["1B_ratio"],    # single
                row["2B_ratio"],    # double
                row["3B_ratio"],    # triple
                row["HR_ratio"],    # homerun
                row["BB+HBP_ratio"],# walk (四球+死球)
                row["Out_ratio"]    # out
            ]
            speed = row["Speed"] # Speedカラムを読み込む
            # 確率の合計が1になるかチェック (小さな誤差は許容)
            if not np.isclose(sum(probabilities), 1.0, atol=0.01): # atolで許容誤差を設定
                 print(f"Warning: Probabilities for player {row['Player']} do not sum to 1 (sum={sum(probabilities)}). Adjusting Out_ratio.")
                 current_sum_except_out = sum(probabilities[:-1])
                 probabilities[-1] = 1.0 - current_sum_except_out
                 if probabilities[-1] < 0:
                     print(f"Error: Cannot normalize probabilities for player {row['Player']}. Skipping.")
                     continue

            player = Player(name=row["Player"], probabilities=probabilities, speed=speed)
            players.append(player)
        except KeyError as e:
            print(f"Error: Missing column {e} for player {row.get('Player', 'Unknown')}. Skipping this player.")
        except ValueError as e:
            print(f"Error creating player {row.get('Player', 'Unknown')}: {e}. Skipping this player.")
    return players

def display_player_stats(players: List[Player]) -> pd.DataFrame:
    """
    選手の成績をまとめてデータフレームで表示する。

    Args:
        players (List[Player]): Playerオブジェクトのリスト。

    Returns:
        pd.DataFrame: 選手の成績をまとめたデータフレーム。
    """
    stats_list = []
    for player in players:
        stats_list.append({
            "選手名": player.name,
            "打席": player._get_stat("plate_appearances"),
            "打数": player._get_stat("at_bats"),
            "安打": player._get_stat("hits"),
            "単打": player._get_stat("singles"),
            "二塁打": player._get_stat("doubles"),
            "三塁打": player._get_stat("triples"),
            "本塁打": player._get_stat("homeruns"),
            "四死球": player._get_stat("walks"),
            "打点": player._get_stat("runs_batted_in"),
            "打率": round(player.batting_average(), 3),
            "出塁率": round(player.on_base_percentage(), 3),
            "長打率": round(player.slugging_percentage(), 3),
            "OPS": round(player.ops(), 3),
            "三振": player._get_stat("strikeouts"),
            "併殺打": player._get_stat("double_plays"),
            "犠打": player._get_stat("sacrifice_bunts"),
            "進塁打": player._get_stat("ground_out_advances"),
            "犠打失敗": player._get_stat("bunt_fails"),
            "犠飛": player._get_stat("sacrifice_flies"),
        })
    return pd.DataFrame(stats_list)

def simulate_season(num_games: int, players_list: List[Player]) -> Tuple[int, pd.DataFrame]:
    """
    指定された試合数のシーズンをシミュレートし、チームの総得点と各選手の通算成績を返す。

    Args:
        num_games (int): シミュレートする試合数。
        players_list (List[Player]): Playerオブジェクトのリスト。

    Returns:
        Tuple[int, pd.DataFrame]: (シーズン総得点, 各選手の通算成績DataFrame)
    """
    if not players_list:
        print("No players loaded. Cannot simulate season.")
        return 0, pd.DataFrame()

    total_team_score = 0
    
    # シーズン開始時に選手の成績をリセット
    for player in players_list:
        player.reset_stats()

    for game_num in range(num_games):
        # 各試合ごとに新しいBaseballGameインスタンスを作成し、
        # 同じPlayerオブジェクトのリスト（累積成績を持つ）を渡す
        game = BaseballGame(players_list) 
        game_score, _ = game.simulate_game()
        total_team_score += game_score
    
    # 全試合終了後の選手成績を表示
    season_player_stats_df = display_player_stats(players_list)
    return total_team_score, season_player_stats_df

def run_one_game_simulation(players_list: List[Player]):
    """
    1試合のシミュレーションを実行し、結果を詳細に表示する。
    注意：この関数を複数回呼び出すと、選手の成績は累積されます。
    各試合でリセットしたい場合は、呼び出し前に `player.reset_stats()` を手動で実行してください。

    Args:
        players_list (List[Player]): Playerオブジェクトのリスト。
    """
    if not players_list:
        print("No players loaded. Cannot simulate game.")
        return

    # ここでは、この関数を呼び出す前に Player オブジェクトがリセットされていることを前提とする。
    # もし1試合ごとの独立した結果が欲しい場合は、外部で reset_stats() を呼び出すか、
    # load_players_from_csv を再実行して新しいPlayerインスタンスのリストを渡す。

    game = BaseballGame(players_list)
    final_score, game_log_data = game.simulate_game()
    print(f"最終スコア: {final_score}\n")

    print("--- イニングごとの打席結果 ---")
    for i, inning_events in enumerate(game_log_data):
        print(f"\n--- {i+1}回 ---")
        if not inning_events:
            print(" (攻撃なし)")
            continue
        for player_name, result, rbi in inning_events: 
            rbi_text = f", {rbi}打点" if rbi > 0 else ""
            print(f"{player_name}: {result}{rbi_text}")
    
    print("\n--- 選手の総合成績 ---")
    player_stats_df = display_player_stats(players_list)
    print(player_stats_df.to_string())

def generate_random_lineup(players_pool: List[Player], shuffle_only: bool = False) -> List[Player]:
    """
    選手プールからランダムに9名を選び、ランダムな打順を生成する。
    shuffle_onlyがTrueの場合、与えられたplayers_poolをシャッフルする。
    """
    if shuffle_only:
        if len(players_pool) != 9:
            raise ValueError("shuffle_onlyがTrueの場合、players_poolは9名の選手を含む必要があります。")
        selected_players = list(players_pool) # コピーを作成して元のリストを変更しない
    else:
        if len(players_pool) < 9:
            raise ValueError("選手数が9名未満のため、打順を生成できません。")
        selected_players = random.sample(players_pool, 9)
    
    random.shuffle(selected_players)
    
    return selected_players

def find_best_and_worst_lineups(num_trials: int, players_for_exploration: List[Player], progress_bar=None, status_text=None, shuffle_only: bool = False) -> Tuple[Dict, Dict]:
    """
    指定された回数だけランダムな打順を生成し、シーズンシミュレーションを実行して、
    最高得点と最低得点の打順を特定する。
    """
    best_lineup_info = {"avg_score": -1, "lineup": [], "player_stats": pd.DataFrame()}
    worst_lineup_info = {"avg_score": float('inf'), "lineup": [], "player_stats": pd.DataFrame()}

    # all_players_dataからPlayerオブジェクトのリストを一度作成
    # all_players_list = []
    # PROB_COLS = ["1B_ratio", "2B_ratio", "3B_ratio", "HR_ratio", "BB+HBP_ratio", "Out_ratio"]
    # for _, row in all_players_data.iterrows():
    #     probabilities = row[PROB_COLS].tolist()
    #     all_players_list.append(Player(name=row["Player"], probabilities=probabilities))

    for i in range(num_trials):
        # ランダムな打順を生成
        current_lineup_players = generate_random_lineup(players_for_exploration, shuffle_only=shuffle_only)
        
        # シーズンシミュレーションを実行
        total_score, player_stats_df = simulate_season(143, current_lineup_players)
        avg_score = total_score / 143

        # 最高得点の打順を更新
        if avg_score > best_lineup_info["avg_score"]:
            best_lineup_info["avg_score"] = avg_score
            best_lineup_info["total_score"] = total_score # 総得点も保存
            best_lineup_info["lineup"] = [p.name for p in current_lineup_players]
            best_lineup_info["player_stats"] = player_stats_df
        
        # 最低得点の打順を更新
        if avg_score < worst_lineup_info["avg_score"]:
            worst_lineup_info["avg_score"] = avg_score
            worst_lineup_info["total_score"] = total_score # 総得点も保存
            worst_lineup_info["lineup"] = [p.name for p in current_lineup_players]
            worst_lineup_info["player_stats"] = player_stats_df

        # 進捗を更新
        if progress_bar and status_text:
            progress_bar.progress((i + 1) / num_trials)
            status_text.text(f"シミュレーション中: {i + 1}/{num_trials} パターン完了")
            
    return best_lineup_info, worst_lineup_info

if __name__ == '__main__':
    # 使用例
    # 1. CSVから選手データを読み込む
    file_path = '../../data/processed/2024_t.csv'
    players = load_players_from_csv(file_path)

    if players:
        # 2. 1試合のシミュレーションを実行
        print("--- 1試合シミュレーション ---")
        run_one_game_simulation(players)

        # 3. 143試合のシーズンシミュレーションを実行
        print("\n\n--- 143試合シーズンシミュレーション ---")
        num_season_games = 143
        total_score, season_stats = simulate_season(num_season_games, players)
        avg_score = total_score / num_season_games if num_season_games > 0 else 0
        print(f"\nシーズン総得点: {total_score}")
        print(f"平均得点: {avg_score:.2f}")
        print("\nシーズン通算成績:")
        print(season_stats.to_string())
