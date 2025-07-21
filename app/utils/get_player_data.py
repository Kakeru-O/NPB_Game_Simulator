import os
import argparse
#import requests
#import urllib  #HTMLにアクセス＆取得
#from bs4 import BeautifulSoup #HTMLからデータ抽出
import pandas as pd
import numpy as np


def scrape_player_data(team:str, year:str):

    # URLを指定
    url = f'https://npb.jp/bis/{year}/stats/idb1_{team}.html'

    # HTMLからテーブルを読み込む
    tables = pd.read_html(url)

    # 最初のテーブルを取得
    df = tables[0]
    df = df.loc[1:,1:].reset_index(drop=True)
    df.columns = df.iloc[0]
    # 半角スペースを削除
    df.columns = df.columns.str.replace(' ', '', regex=False)
    # 半角スペース、全角スペース、改行コードを削除
    df.columns = df.columns.str.replace(r'[\s\u3000]', '', regex=True)

    df = df.loc[1:].reset_index(drop=True)
    
    # 列ごとに型変換を試みる
    for col in df.columns[1:]:
        # 数値変換を試みる
        try:
            # 一度 float 型に変換
            temp_col = pd.to_numeric(df[col], errors='coerce')
            # NaN のない整数値のみなら int 型に変換
            if temp_col.dropna().mod(1).eq(0).all():
                df[col] = temp_col.astype('Int64')  # 欠損値対応の int 型
            else:
                df[col] = temp_col  # float 型のまま
        except ValueError:
            # 数値変換できない場合はそのまま
            pass

    df['選手'] = df['選手'].str.replace(r'\s+', '', regex=True)

    os.makedirs(f"./data/raw/{year}", exist_ok=True)
    csv_path = f"./data/raw/{year}/{team}.csv"
    df.to_csv(csv_path,index=False)

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape player data for a specific year or a range of years.')
    parser.add_argument('--year', type=str, help='The year to scrape data for.')
    args = parser.parse_args()

    team_list = ["g","t","c","db","s","d","f","e","m","l","b","h"]
    
    if args.year:
        years_to_scrape = [args.year]
    else:
        years_to_scrape = ["2022", "2023", "2024"]

    for year in years_to_scrape:
        for team in team_list:
            print(f"Scraping data for team: {team}, year: {year}")
            scrape_player_data(team, year)
    
