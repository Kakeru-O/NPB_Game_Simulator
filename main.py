import streamlit as st

st.set_page_config(layout="wide")

# st.Page を使って各ページを定義
pages = [
    st.Page("app/pages/main_app.py", title="シミュレーター", icon="⚾"),
    st.Page("app/pages/about.py", title="このアプリについて", icon="💡"),
]

# ナビゲーションを生成
pg = st.navigation(pages)

# 現在選択されているページを実行
pg.run()