import os
import argparse

import pandas as pd
import numpy as np


def process_batting_stats(df):
    """
    rawな選手データ(DataFrame)をシミュレーションで使える形に加工する

    Args:
        df (pd.DataFrame): get_dataから取得したrawデータ

    Returns:
        pd.DataFrame: 加工済みの選手データ
    """
    # 列名を英語に置き換え
    eng_columns = [
        'Player', 'G', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'TB', 'RBI',
        'SB', 'CS', 'SH', 'SF', 'BB', 'IBB', 'HBP', 'SO', 'GIDP', 'AVG', 'SLG','OBP'
    ]
    df.columns = eng_columns

    # データ型を数値に変換（エラーは無視）
    for col in ['PA', 'H', '2B', '3B', 'HR', 'BB', 'HBP', 'SO']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 50打席未満の選手を除外
    df = df[df["PA"]>=50].reset_index(drop=True)

    # 一塁打を計算
    df['1B'] = df['H'] - (df['2B'] + df['3B'] + df['HR'])
    # 四死球を計算
    df['BB+HBP'] = df['BB'] + df['HBP']

    # 各種割合の計算
    df['1B_ratio'] = df['1B'] / df['PA']
    df['2B_ratio'] = df['2B'] / df['PA']
    df['3B_ratio'] = df['3B'] / df['PA']
    df['HR_ratio'] = df['HR'] / df['PA']
    df['BB+HBP_ratio'] = df['BB+HBP'] / df['PA']
    df['SO_ratio'] = df['SO'] / df['PA']

    # 三振以外のアウトの割合
    non_so_out_ratio = 1 - df[['1B_ratio', '2B_ratio', '3B_ratio', 'HR_ratio', 'BB+HBP_ratio', 'SO_ratio']].sum(axis=1)
    # 負の値にならないようにクリップ
    non_so_out_ratio = non_so_out_ratio.clip(lower=0)

    # ゴロアウトとフライアウトの割合を計算
    df['Ground_Out_ratio'] = non_so_out_ratio * 0.6
    df['Fly_Out_ratio'] = non_so_out_ratio * 0.4

    # 確率が0の項目に微小な値を付与し、その分を1B_ratioから引く
    for col in ['2B_ratio', '3B_ratio', 'HR_ratio']:
        mask = df[col] == 0
        df.loc[mask, '1B_ratio'] -= 1e-4
        df.loc[mask, col] = 1e-4

    # 全ての確率の合計が1になるように正規化
    cols_to_normalize = ['1B_ratio', '2B_ratio', '3B_ratio', 'HR_ratio', 'BB+HBP_ratio', 'SO_ratio', 'Ground_Out_ratio', 'Fly_Out_ratio']
    total_ratio = df[cols_to_normalize].sum(axis=1)
    for col in cols_to_normalize:
        df[col] = df[col] / total_ratio

    # Out_ratioも計算しておく（デバッグや分析用）
    df['Out_ratio'] = df['SO_ratio'] + df['Ground_Out_ratio'] + df['Fly_Out_ratio']

    # 最終的な出力列
    output_cols = [
        "Player", "1B_ratio", "2B_ratio", "3B_ratio", "HR_ratio",
        "BB+HBP_ratio", "SO_ratio", "Ground_Out_ratio", "Fly_Out_ratio", "Out_ratio"
    ]
    df_res = df[output_cols].reset_index(drop=True)

    return df_res

def add_speed_score(year: str, team: str, raw_dir="./data/raw"):
    """
    選手データに走力ポイントを追加する

    Args:
        year (str): 年度
        team (str): チーム名
        raw_dir (str): rawデータが格納されているディレクトリ

    Returns:
        pd.DataFrame: 走力ポイントを追加した選手データ
    """
    # data/rawから元データを読み込む
    raw_path = os.path.join(raw_dir, f"{year}/{team}.csv")
    try:
        df = pd.read_csv(raw_path)
    except FileNotFoundError:
        print(f"Error: {raw_path} not found.")
        return None

    # process_dataと同様にカラム名を英語に変換
    eng_columns = [
        'Player', 'G', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'TB', 'RBI',
        'SB', 'CS', 'SH', 'SF', 'BB', 'IBB', 'HBP', 'SO', 'GIDP', 'AVG', 'SLG', 'OBP'
    ]
    # 元のデータフレームのカラム数がeng_columnsと一致するか確認
    if len(df.columns) == len(eng_columns):
        df.columns = eng_columns
    else:
        # 選手名と成績データのみを抽出し、カラム名を再設定
        # 元データはヘッダーが2行あるため、2行目以降をデータとして扱う
        df = df.iloc[1:, :len(eng_columns)]
        df.columns = eng_columns


    # データ型を数値に変換（エラーは無視）
    for col in ['3B', 'SB', 'CS']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 走力ポイントを計算
    # 走力ポイント = (三塁打数 * 3) + (盗塁数 * 1) - (盗塁死数 * 2)
    df['Speed'] = (df['3B'] * 3) + (df['SB'] * 1) - (df['CS'] * 2)

    return df


def process_data(df, team, year, output_dir="./data/processed"):
    # process_batting_stats関数を呼び出してデータを加工
    df_processed = process_batting_stats(df.copy())

    # 走力スコアデータを取得 (rawデータの場所を指定)
    df_speed = add_speed_score(year, team)
    if df_speed is None:
        return
    # 必要なカラムのみに絞る
    df_speed_simple = df_speed[['Player', 'Speed']]

    # processedデータとマージ
    df_merged = pd.merge(df_processed, df_speed_simple, on='Player', how='left')

    # SpeedスコアがNaNの場合は0で埋める
    df_merged['Speed'] = df_merged['Speed'].fillna(0)

    # 加工済みデータをCSVに保存
    os.makedirs(os.path.join(output_dir, str(year)), exist_ok=True)
    processed_csv_path = os.path.join(output_dir, str(year), f"{team}.csv")
    df_merged.to_csv(processed_csv_path, index=False)

    return df_merged


def main(teams, year, raw_dir="./data/raw", processed_dir="./data/processed"):
    """指定されたチームと年度のデータを取得・加工するメイン関数"""
    for team in teams:
        print(f"Processing: {year} {team}")
        # get_dataはWebから取ってくるので、テストでは使いにくい。ここではrawデータは既にある前提とする。
        # raw_df = get_data(team, year)
        raw_path = os.path.join(raw_dir, f"{year}/{team}.csv")
        try:
            raw_df = pd.read_csv(raw_path)
        except FileNotFoundError:
            print(f"Raw data not found at {raw_path}, skipping.")
            continue

        if not raw_df.empty:
            # process_data内で保存先を指定できるようにする
            df = process_data(raw_df, team, year, processed_dir)
            print(f"Saved processed data to {processed_dir}/{year}/{team}.csv")
            #print(df)
        else:
            print(f"No data found for {team} in {year}.")

def calculate_player_stats(stats_df):
    """シミュレーション結果から各種成績を計算する"""
    required_cols = ['1B', '2B', '3B', 'HR', 'BB+HBP', 'SO', 'Ground_Out', 'Fly_Out', 'Sacrifice_Attempts', 'RBI', 'Sacrifice_Success']
    for col in required_cols:
        if col not in stats_df.columns:
            stats_df[col] = 0

    stats_df['Out'] = stats_df['SO'] + stats_df['Ground_Out'] + stats_df['Fly_Out']
    stats_df['PA'] = stats_df[['1B', '2B', '3B', 'HR', 'BB+HBP', 'SO', 'Ground_Out', 'Fly_Out', 'Sacrifice_Attempts']].sum(axis=1)
    stats_df['AB'] = stats_df[['1B', '2B', '3B', 'HR', 'SO', 'Ground_Out', 'Fly_Out']].sum(axis=1)
    stats_df['H'] = stats_df[['1B', '2B', '3B', 'HR']].sum(axis=1)
    stats_df['TB'] = stats_df['1B'] + 2*stats_df['2B'] + 3*stats_df['3B'] + 4*stats_df['HR']
    
    stats_df['AVG'] = (stats_df['H'] / stats_df['AB']).where(stats_df['AB'] > 0, 0)
    stats_df['OBP'] = ((stats_df['H'] + stats_df['BB+HBP']) / stats_df['PA']).where(stats_df['PA'] > 0, 0)
    stats_df['SLG'] = (stats_df['TB'] / stats_df['AB']).where(stats_df['AB'] > 0, 0)
    
    stats_df['OPS'] = stats_df['OBP'] + stats_df['SLG']
    return stats_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process player data for a specific year or a range of years.')
    parser.add_argument('--year', type=str, help='The year to process data for.')
    args = parser.parse_args()

    team_list = ["g","t","c","db","s","d","f","e","m","l","b","h"]

    if args.year:
        years_to_process = [args.year]
    else:
        years_to_process = ["2022", "2023", "2024"]

    for year in years_to_process:
        for team in team_list:
            main([team], year)
    