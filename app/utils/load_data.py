
import pandas as pd

def load_default_lineups(year):
    """指定された年のデフォルトスタメンデータを読み込む"""
    file_path = f"./data/processed/default_lineups_{year}.csv"
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame()
    

def load_data_from_csv(year: int, team_abbr: str, base_path: str = "./data/processed"):
    """指定された年とチームの選手成績データをCSVから読み込む"""
    file_path_processed = f"{base_path}/{year}_{team_abbr}.csv"

    try:
        df = pd.read_csv(file_path_processed)
        return df
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame()
