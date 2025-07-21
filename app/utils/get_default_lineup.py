import os
import argparse
import pandas as pd
import numpy as np
import random



def get_initial_players(df, default_lineups_df, year, team, team_abbreviations):
    """multiselectの初期選択選手リストを取得する"""
    player_names = df['Player'].tolist()
    team_abbr_upper = team_abbreviations[team].upper()
    
    team_default_df = default_lineups_df[
        (default_lineups_df['Year'] == int(year)) & 
        (default_lineups_df['Team_Abbr'] == team_abbr_upper)
    ]

    if not team_default_df.empty:
        position_order = ['捕', '一', '二', '三', '遊', '左', '中', '右', '指']
        team_default_df['Position_Order'] = pd.Categorical(
            team_default_df['Position'], categories=position_order, ordered=True
        )
        initial_players = team_default_df.sort_values('Position_Order')['Player'].tolist()
    else:
        initial_players = player_names[:9]
        
    if len(initial_players) < 9:
        remaining_players = [p for p in player_names if p not in initial_players]
        random.shuffle(remaining_players)
        initial_players.extend(remaining_players[:9 - len(initial_players)])
        
    return initial_players[:9]

def get_default_lineup(year: str, league: str, team_abbr: str):
    """
    指定された年度、リーグ、チームのデフォルトスタメン（各ポジション最多先発出場選手）を抽出する。

    Args:
        year (str): 年度 (例: "2024")
        league (str): リーグ ("Pacific" または "Central")
        team_abbr (str): チーム略称 (例: "M" for Marines)

    Returns:
        dict: ポジション名をキー、選手名を値とする辞書。投手は含まない。
              例: {'捕': '選手A', '一': '選手B', ...}
    """
    if year == "2025":
        url = f'https://nf3.sakura.ne.jp/{league}/{team_abbr}/t/kiyou.htm'
    else:
        url = f'https://nf3.sakura.ne.jp/{year}/{league}/{team_abbr}/t/kiyou.htm'
    try:
        # header=[0, 1] で2行をヘッダーとして読み込む
        tables = pd.read_html(url, header=[0, 1])
        df = tables[1] # 2番目のテーブルが起用情報
    except Exception as e:
        print(f"Error reading HTML from {url}: {e}")
        return {}

    # カラム名の整形
    # MultiIndexのカラム名を結合して扱いやすくする
    # 例: ('捕手', '先発') -> '捕手_先発'
    # ただし、('名前', '名前') のような場合は '名前' にする
    new_columns = []
    for col in df.columns.values:
        if isinstance(col, tuple):
            if col[0] == col[1]: # 例: ('名前', '名前')
                new_columns.append(col[0])
            else:
                new_columns.append('_'.join(col).strip())
        else:
            new_columns.append(col)
    df.columns = new_columns

    # デバッグプリントを削除
    # print("--- DataFrame Columns after processing ---")
    # print(df.columns)

    # 不要なカラムを削除 (背番、守備、試合、途中、変更)
    # 選手名カラムは '名前'
    cols_to_drop = [col for col in df.columns if 
                    col.startswith('背番') or 
                    col.startswith('守備') or 
                    col.startswith('試合') or 
                    col.endswith('_途中') or 
                    col.endswith('_変更')]
    df = df.drop(columns=cols_to_drop)

    # 選手名から<a>タグを除去
    df['名前'] = df['名前'].apply(lambda x: x.split('>')[1].split('<')[0] if '<a' in str(x) else x)

    default_lineup = {}
    selected_players = set()

    # ポジションの優先順位 (一般的な野球のポジション)
    # 投手(P)は含めない
    # DHはパ・リーグのみ
    position_map = {
        '捕手': '捕',
        '一塁': '一',
        '二塁': '二',
        '三塁': '三',
        '遊撃': '遊',
        '左翼': '左',
        '中堅': '中',
        '右翼': '右',
        'ＤＨ': '指'
    }
    # 守備位置の表示順
    display_order = ['捕', '一', '二', '三', '遊', '左', '中', '右', '指']

    # 各ポジションの最多先発出場選手を抽出
    for pos_jp, pos_abbr in position_map.items():
        start_col = f'{pos_jp}_先発'
        if start_col not in df.columns:
            continue

        # ポジションごとの選手と先発出場数を抽出
        # '-' を 0 に変換し、数値型にする
        df_pos_players = df[['名前', start_col]].copy()
        df_pos_players[start_col] = pd.to_numeric(df_pos_players[start_col].replace('-', 0), errors='coerce').fillna(0).astype(int)
        
        # 先発出場数でソート
        df_pos_players = df_pos_players.sort_values(by=start_col, ascending=False)

        # 最多出場選手を抽出 (重複を避ける)
        for idx, row in df_pos_players.iterrows():
            player_name = row['名前']
            games_started = row[start_col]

            if games_started == 0: # 先発出場がない場合はスキップ
                continue

            if player_name not in selected_players:
                default_lineup[pos_abbr] = player_name
                selected_players.add(player_name)
                break # このポジションの選手が見つかったので次へ
    
    # セ・リーグの場合、DH(指)を除外
    if league == "Central" and '指' in default_lineup:
        del default_lineup['指']

    # 結果をdisplay_orderに基づいてソート
    sorted_lineup = {pos: default_lineup[pos] for pos in display_order if pos in default_lineup}

    return sorted_lineup


# main.py と同様のチーム略称とリーグ情報
TEAM_ABBREVIATIONS = {
    "ヤクルト": {"abbr": "S", "league": "Central"},
    "DeNA": {"abbr": "DB", "league": "Central"},
    "阪神": {"abbr": "T", "league": "Central"},
    "巨人": {"abbr": "G", "league": "Central"},
    "広島": {"abbr": "C", "league": "Central"},
    "中日": {"abbr": "D", "league": "Central"},
    "オリックス": {"abbr": "B", "league": "Pacific"},
    "ソフトバンク": {"abbr": "H", "league": "Pacific"},
    "西武": {"abbr": "L", "league": "Pacific"},
    "楽天": {"abbr": "E", "league": "Pacific"},
    "ロッテ": {"abbr": "M", "league": "Pacific"},
    "日本ハム": {"abbr": "F", "league": "Pacific"},
}

# get_default_lineup が期待するリーグ名
LEAGUE_MAP = {"Central": "Central", "Pacific": "Pacific"}

def generate_and_save_default_lineups(year: str, output_dir: str = "./data/processed"):
    """
    全球団のデフォルトスタメンを抽出し、CSVファイルとして保存する。

    Args:
        year (str): データを取得する年度。
        output_dir (str): CSVファイルを保存するディレクトリ。
    """
    all_lineups_data = []

    print(f"Generating default lineups for {year}...")

    for team_name, info in TEAM_ABBREVIATIONS.items():
        team_abbr = info["abbr"]
        league_type = info["league"]
        
        print(f"  Processing {team_name} ({league_type})...")

        # get_default_lineupのleague引数は "Pacific" or "Central" を期待
        lineup = get_default_lineup(year=year, league=LEAGUE_MAP[league_type], team_abbr=team_abbr)

        if lineup:
            print(f"    Successfully retrieved lineup for {team_name}.")
            for position, player in lineup.items():
                all_lineups_data.append({
                    "Year": year,
                    "League": league_type,
                    "Team": team_name,
                    "Team_Abbr": team_abbr,
                    "Position": position,
                    "Player": player
                })
        else:
            print(f"    Warning: Could not retrieve lineup for {team_name} ({league_type}).")

    if all_lineups_data:
        df_all_lineups = pd.DataFrame(all_lineups_data)
        
        # カラムの順序を定義
        column_order = ["Year", "League", "Team", "Team_Abbr", "Position", "Player"]
        df_all_lineups = df_all_lineups[column_order]

        output_file = os.path.join(output_dir, f"default_lineups_{year}.csv")
        os.makedirs(output_dir, exist_ok=True)
        df_all_lineups.to_csv(output_file, index=False)
        print(f"Successfully saved default lineups to {output_file}")
    else:
        print("No lineup data generated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate default lineups for a specific year or a range of years.')
    parser.add_argument('--year', type=str, help='The year to generate lineups for.')
    args = parser.parse_args()

    if args.year:
        years_to_generate = [args.year]
    else:
        years_to_generate = [str(y) for y in range(2022, 2026)]

    for year in years_to_generate:
        generate_and_save_default_lineups(year=year)
