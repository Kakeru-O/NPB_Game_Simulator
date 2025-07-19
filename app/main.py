import streamlit as st
import pandas as pd
from utils.load_data import load_data_from_csv

TEAM_NAME_TO_ABBR = {
    "阪神": "t", "広島": "c", "DeNA": "db", "巨人": "g", "ヤクルト": "s", "中日": "d",
    "オリックス": "b", "ロッテ": "m", "ソフトバンク": "h", "楽天": "e", "西武": "l", "日本ハム": "f"
}

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

    # メインコンテンツ
    tab1, tab2 = st.tabs(["任意打順でシミュレーション", "最強打順を探索"])

    with tab1:
        st.header("任意打順でシミュレーション")
        st.write(f"{year}年 {team_name}の選手データ")
        
        if not player_data.empty:
            st.dataframe(player_data)
        else:
            st.error("選手データを読み込めませんでした。")

    with tab2:
        st.header("最強打順を探索")
        # ここに最強打順探索のUIを実装

if __name__ == "__main__":
    main()
