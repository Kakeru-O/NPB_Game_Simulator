import streamlit as st

def main():
    st.title("NPB Game Simulator")

    # サイドバー
    st.sidebar.header("設定")
    year = st.sidebar.selectbox("年度", [2024, 2023, 2022])
    team = st.sidebar.selectbox("チーム", ["阪神", "広島", "DeNA", "巨人", "ヤクルト", "中日", "オリックス", "ロッテ", "ソフトバンク", "楽天", "西武", "日本ハム"])

    # メインコンテンツ
    tab1, tab2 = st.tabs(["任意打順でシミュレーション", "最強打順を探索"])

    with tab1:
        st.header("任意打順でシミュレーション")
        # ここに任意打順シミュレーションのUIを実装

    with tab2:
        st.header("最強打順を探索")
        # ここに最強打順探索のUIを実装

if __name__ == "__main__":
    main()
