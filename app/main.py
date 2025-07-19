import streamlit as st
import pandas as pd
from utils.load_data import load_data_from_csv, load_default_lineups
from utils.player import Player
from utils.game import BaseballGame
from utils.simulator import display_player_stats

TEAM_NAME_TO_ABBR = {
    "阪神": "t", "広島": "c", "DeNA": "db", "巨人": "g", "ヤクルト": "s", "中日": "d",
    "オリックス": "b", "ロッテ": "m", "ソフトバンク": "h", "楽天": "e", "西武": "l", "日本ハム": "f"
}

CENTRAL_LEAGUE_TEAMS = ["阪神", "広島", "DeNA", "巨人", "ヤクルト", "中日"]

PROB_COLS = ["1B_ratio", "2B_ratio", "3B_ratio", "HR_ratio", "BB+HBP_ratio", "Out_ratio"]

def create_player_list(lineup: list[str], player_data: pd.DataFrame) -> list[Player]:
    """選択された打順と選手データからPlayerオブジェクトのリストを作成する"""
    players = []
    for player_name in lineup:
        player_stats = player_data[player_data["Player"] == player_name].iloc[0]
        probabilities = player_stats[PROB_COLS].tolist()
        player = Player(name=player_name, probabilities=probabilities)
        players.append(player)
    return players

def main():
    st.title("NPB Game Simulator")

    # サイドバー
    st.sidebar.header("設定")
    year = st.sidebar.selectbox("年度", [2024, 2023, 2022])
    team_name = st.sidebar.selectbox("チーム", list(TEAM_NAME_TO_ABBR.keys()))

    # 選択されたチームの略称を取得
    team_abbr = TEAM_NAME_TO_ABBR[team_name]

    # 選手データの読み込み
    player_data = load_data_from_csv(year, team_abbr)
    default_lineup_df = load_default_lineups(year)

    # メインコンテンツ
    tab1, tab2 = st.tabs(["任意打順でシミュレーション", "最強打順を探索"])

    with tab1:
        st.header("任意打順でシミュレーション")
        
        if not player_data.empty:
            st.write(f"{year}年 {team_name}の選手データ")
            st.dataframe(player_data)

            st.header("打順設定")
            player_names = player_data["Player"].tolist()
            
            # デフォルトスタメンを取得
            default_lineup_names = []
            if not default_lineup_df.empty:
                team_lineup = default_lineup_df[default_lineup_df['Team'] == team_name]
                if not team_lineup.empty:
                    default_lineup_names = team_lineup['Player'].tolist()

            # セ・リーグで8人しかいない場合、9人目を追加
            if team_name in CENTRAL_LEAGUE_TEAMS and len(default_lineup_names) == 8:
                for p_name in player_names:
                    if p_name not in default_lineup_names:
                        default_lineup_names.append(p_name)
                        break

            lineup = []
            for i in range(9):
                default_player = default_lineup_names[i] if i < len(default_lineup_names) else player_names[0]
                default_index = player_names.index(default_player) if default_player in player_names else 0
                selected_player = st.selectbox(f"{i+1}番", player_names, key=f"player_{i}", index=default_index)
                lineup.append(selected_player)

            if st.button("シミュレーション実行"):
                # Playerオブジェクトのリストを作成
                players = create_player_list(lineup, player_data)

                # 1試合のシミュレーションを実行
                game = BaseballGame(players)
                final_score, game_log = game.simulate_game()

                st.header("シミュレーション結果")
                st.metric("最終スコア", f"{final_score}点")

                # イニングごとの詳細ログ (DataFrame形式)
                with st.expander("イニングごとの詳細ログを見る"):
                    log_df = pd.DataFrame(index=[p.name for p in players], columns=range(1, 10))
                    for i, inning_events in enumerate(game_log):
                        inning_col = i + 1
                        for player_name, result, rbi in inning_events:
                            rbi_text = f"({rbi})" if rbi > 0 else ""
                            event_text = f"{result}{rbi_text}"
                            # 同じイニングに同じ選手が複数回打席に立った場合
                            if pd.isna(log_df.loc[player_name, inning_col]):
                                log_df.loc[player_name, inning_col] = event_text
                            else:
                                log_df.loc[player_name, inning_col] += f", {event_text}"
                    st.dataframe(log_df.fillna("-"))
                
                # 選手個人の成績
                st.header("打者成績")
                player_stats_df = display_player_stats(players)
                st.dataframe(player_stats_df)

        else:
            st.error("選手データを読み込めませんでした。")

    with tab2:
        st.header("最強打順を探索")
        # ここに最強打順探索のUIを実装

if __name__ == "__main__":
    main()
