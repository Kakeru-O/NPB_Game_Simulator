import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="NPB Game Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

HIDE_ST_STYLE = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
        .appview-container .main .block-container{
                            padding-top: 1rem;
                            padding-right: 3rem;
                            padding-left: 3rem;
                            padding-bottom: 1rem;
                        }  
                        .reportview-container {
                            padding-top: 0rem;
                            padding-right: 3rem;
                            padding-left: 3rem;
                            padding-bottom: 0rem;
                        }
                        header[data-testid="stHeader"] {
                            z-index: -1;
                        }
                        div[data-testid="stToolbar"] {
                        z-index: 100;
                        }
                        div[data-testid="stDecoration"] {
                        z-index: 100;
                        }
                </style>
"""

st.html(HIDE_ST_STYLE)
from app.utils.load_data import load_data_from_csv, load_default_lineups
from app.utils.player import Player
from app.utils.game import BaseballGame
from app.utils.simulator import display_player_stats, find_best_and_worst_lineups, simulate_season
from app.utils.constants import PITCHER_STATS, TEAM_COLORS

TEAM_NAME_TO_ABBR = {
    "阪神": "t", "広島": "c", "DeNA": "db", "巨人": "g", "ヤクルト": "s", "中日": "d",
    "オリックス": "b", "ロッテ": "m", "ソフトバンク": "h", "楽天": "e", "西武": "l", "日本ハム": "f"
}

CENTRAL_LEAGUE_TEAMS = ["阪神", "広島", "DeNA", "巨人", "ヤクルト", "中日"]

PROB_COLS = ["1B_ratio", "2B_ratio", "3B_ratio", "HR_ratio", "BB+HBP_ratio", "SO_ratio", "Ground_Out_ratio", "Fly_Out_ratio"]

def create_player_list(lineup: list[str], player_data: pd.DataFrame) -> list[Player]:
    """選択された打順と選手データからPlayerオブジェクトのリストを作成する"""
    players = []
    for player_name in lineup:
        # 投手データの場合
        if player_name == "投手":
            player_stats = pd.Series(PITCHER_STATS)
        else:
            player_stats = player_data[player_data["Player"] == player_name].iloc[0]
        probabilities = player_stats[PROB_COLS].tolist()
        speed = player_stats["Speed"] # Speedカラムを読み込む
        player = Player(name=player_name, probabilities=probabilities, speed=speed)
        players.append(player)
    return players

def main():
    # セッションステートの初期化
    if "lineup_for_exploration" not in st.session_state:
        st.session_state.lineup_for_exploration = []

    st.title("NPB Game Simulator") # アプリのタイトルを明示的に表示

    # サイドバー
    st.sidebar.header("設定")
    year = st.sidebar.selectbox("年度", [2025, 2024, 2023, 2022],index=1)
    
    # チーム選択
    st.sidebar.subheader("チーム選択")
    teams = list(TEAM_NAME_TO_ABBR.keys())
    
    # セッションステートで選択中のチームを管理
    if "selected_team" not in st.session_state:
        st.session_state.selected_team = teams[7] # デフォルトは最初のチーム

    # st.pills を使用してチーム選択を実装
    selected_team_pills = st.sidebar.pills(
        "",
        options=teams,
        default=st.session_state.selected_team, # indexの代わりにdefaultを使用
        key="team_pills",
        label_visibility="collapsed",
    )

    if selected_team_pills != st.session_state.selected_team:
        st.session_state.selected_team = selected_team_pills
        st.rerun()
    
    team_name = st.session_state.selected_team
    # セッションステートでDH制の状態を管理
    if "use_dh" not in st.session_state:
        st.session_state.use_dh = True # デフォルトはDH制あり

    use_dh = st.sidebar.checkbox("DH制を使用する", value=st.session_state.use_dh, key="dh_checkbox")
    if use_dh != st.session_state.use_dh:
        st.session_state.use_dh = use_dh
        st.rerun()

    # 選択されたチームの略称を取得
    team_abbr = TEAM_NAME_TO_ABBR[team_name]

    # チームカラーの取得
    selected_team_colors = TEAM_COLORS.get(team_abbr, {"main": "#000000", "accent": "#FFFFFF"}) # デフォルトは黒

    # カスタムCSSでボタン、プログレスバー、データフレームのスタイルを変更
    st.html(f"""
        <style>
        /* st.buttonのスタイル */
        div[data-testid="stButton"] > button {{
            background-color: {selected_team_colors["main"]};
            color: {selected_team_colors["accent"]};
            border: 1px solid {selected_team_colors["main"]};
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.2s ease-in-out;
        }}
        div[data-testid="stButton"] > button:hover {{
            background-color: {selected_team_colors["accent"]};
            color: {selected_team_colors["main"]};
            border: 1px solid {selected_team_colors["main"]};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}

        /* st.progressのスタイル */
        div[data-testid="stProgress"] > div > div {{
            background-color: {selected_team_colors["main"]};
        }}

        /* メインコンテンツエリアのパディング調整 */
        .st-emotion-cache-z5fcl4 {{ /* Streamlitのメインコンテンツブロックのクラス名 */
            padding-top: 2rem; /* デフォルトより少し狭く */
        }}

        /* st.dataframeのスタイル */
        div[data-testid="stDataFrame"] {{
            border: 1px solid #e6e6e6; /* 薄いグレーのボーダー */
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* 控えめなシャドウ */
            overflow: hidden; /* ボーダーの角丸を適用 */
        }}
        </style>
        """)

    # 選手データの読み込み
    player_data = load_data_from_csv(year, team_abbr)
    default_lineup_df = load_default_lineups(year)
    player_data_display = load_data_from_csv(year,team_abbr,base_path="./data/raw")
    player_data_display = player_data_display[player_data_display['打席']>=50].reset_index(drop=True)
    # メインコンテンツ
    tab1, tab2 = st.tabs(["任意打順でシミュレーション", "最適打順を探索"])

    with tab1:
        st.header("任意打順でシミュレーション")
        
        if not player_data.empty:
            st.write(f"{year}年 {team_name}の選手データ")
            st.write("50打席以上たった選手を表示しています。")
            st.dataframe(player_data_display,use_container_width=True,hide_index=True)

            st.header("打順設定")
            st.write("ポジションごとの最多出場選手を取得しています。")
            # DH制がオフの場合、投手データをplayer_dataに追加
            if not use_dh:
                pitcher_name = PITCHER_STATS["Player"]
                pitcher_df = pd.DataFrame([PITCHER_STATS])
                player_data = pd.concat([player_data, pitcher_df], ignore_index=True)

            player_names = player_data["Player"].tolist()

            # デフォルトスタメンを取得
            default_lineup_names = []
            if not default_lineup_df.empty:
                team_lineup = default_lineup_df[default_lineup_df['Team'] == team_name]
                if not team_lineup.empty:
                    default_lineup_names = team_lineup['Player'].tolist()

            # DH制オフの場合、9番目を投手に設定
            if not use_dh:
                # デフォルト打順が9人未満の場合、9人になるまで適当な選手で埋める
                while len(default_lineup_names) < 9:
                    default_lineup_names.append(player_names[0]) # 最初の選手で埋める
                # 9番目を投手に設定
                default_lineup_names[8] = pitcher_name
            # DH制オンでセ・リーグで8人しかいない場合、9人目を追加
            elif use_dh and team_name in CENTRAL_LEAGUE_TEAMS and len(default_lineup_names) == 8:
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
            
            # 探索モード用に選択された打順を保存
            st.session_state.lineup_for_exploration = lineup

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
                    st.dataframe(log_df.fillna("-"),use_container_width=True)
                
                # 選手個人の成績
                st.header("打者成績")
                player_stats_df = display_player_stats(players)
                st.dataframe(player_stats_df)

                simulation_status_message = st.empty()
                simulation_status_message.info("1年間のシミュレーションを開始します。少々お待ちください。")
                total_score, season_player_stats_df = simulate_season(143, players)
                avg_score = total_score / 143
                simulation_status_message.empty() # 完了後にメッセージをクリア

                st.metric("シーズン総得点", f"{total_score}点")
                st.metric("1試合平均得点", f"{avg_score:.2f}点")
                st.subheader("シーズン通算打者成績")
                st.dataframe(season_player_stats_df)

        else:
            st.error("選手データを読み込めませんでした。")

    with tab2:
        st.header("最適打順を探索")
        st.write("ランダムな打順を生成し、143試合シミュレーションを複数回実行して、最も平均得点が高かった打順と低かった打順を探索します。")

        num_trials = st.number_input("試行する打順の数", min_value=1, max_value=1000, value=100, help="最大値は1000回です。")

        # Calculate total available players for permutation
        total_players_for_permutation = len(player_data)

        # Calculate permutations for "全選手からランダムに9名選んで探索"
        if total_players_for_permutation >= 9:
            permutations_all_players = math.perm(total_players_for_permutation, 9)
        else:
            permutations_all_players = 0 # Not enough players

        # Calculate factorial for "任意打順で選択した9名の並び替えで探索"
        factorial_9 = math.factorial(9)

        simulation_mode = st.radio(
            "シミュレーションモード",
            (f"全選手からランダムに9名選んで探索 ({permutations_all_players:,}通り)",
             f"任意打順で選択した9名の並び替えで探索 ({factorial_9:,}通り)"),
            index=0
        )

        if st.button("探索開始"):
            if player_data.empty:
                st.error("選手データを読み込めませんでした。年度とチームを選択してください。")
            else:
                st.info(f"{num_trials}回のシミュレーションを開始します。時間がかかる場合があります。")
                progress_bar = st.progress(0)
                status_text = st.empty()

                if simulation_mode == "全選手からランダムに9名選んで探索":
                    # 全選手データからPlayerオブジェクトのリストを作成
                    all_players_list = []
                    for _, row in player_data.iterrows():
                        probabilities = row[PROB_COLS].tolist()
                        all_players_list.append(Player(name=row["Player"], probabilities=probabilities))
                    best_lineup, worst_lineup = find_best_and_worst_lineups(num_trials, all_players_list, progress_bar, status_text, shuffle_only=False)
                else: # 任意打順で選択した9名の並び替えで探索
                    if not st.session_state.lineup_for_exploration:
                        st.error("任意打順タブで打順が選択されていません。先に任意打順タブで打順を設定してください。")
                        return
                    
                    # 任意打順で選択された9名のPlayerオブジェクトのリストを作成
                    selected_players_for_exploration = create_player_list(st.session_state.lineup_for_exploration, player_data)
                    if len(selected_players_for_exploration) != 9:
                        st.error("任意打順タブで9名の選手が選択されていません。")
                        return
                    best_lineup, worst_lineup = find_best_and_worst_lineups(num_trials, selected_players_for_exploration, progress_bar, status_text, shuffle_only=True)

                st.success("探索が完了しました！")
                status_text.empty() # 完了後にテキストをクリア

                st.header("最高平均得点打順")
                st.write(f"総得点: {best_lineup["total_score"]} (平均得点: {best_lineup["avg_score"]:.2f})")
                st.dataframe(best_lineup["player_stats"],use_container_width=True)

                st.header("最低平均得点打順")
                st.write(f"総得点: {worst_lineup["total_score"]} (平均得点: {worst_lineup["avg_score"]:.2f})")
                st.dataframe(worst_lineup["player_stats"],use_container_width=True)

if __name__ == "__main__":
    main()
