# NPB Game Simulator

NPBの打順をシミュレートして、最強の打順を見つけるアプリケーションです。

## アプリケーションの概要

このアプリケーションは、NPB（日本プロ野球）の実際の選手データを使用して、様々な打順の得点能力をシミュレートします。ユーザーは年度とチームを選択し、自由に打順を組んで1試合のシミュレーションを行ったり、多数のランダムな打順を試行して最も得点効率の高い「最強打順」を探したりすることができます。

Streamlitの機能を活用し、インタラクティブで直感的な操作性を実現しています。プロ野球ファンはもちろん、データ分析やStreamlitに興味がある方にも楽しんでいただける内容を目指しています。

### データについて

本アプリケーションで使用される選手データは、NPB公式サイトなどからスクレイピングによって取得されます。データの取得と加工は自動化されており、GitHub Actionsを用いて定期的に最新の情報に更新されます。

## 主な機能

- **年度・チーム選択**: シミュレーションしたい年度とチームを選べます。
- **任意打順シミュレーション**: 好きな選手で打順を組み、1試合のシミュレーションを実行できます。イニングごとの詳細な試合経過や、打者成績も確認できます。1年間のシミュレーション結果も表示されます。
- **最強打順の探索**: 指定した回数だけランダムな打順でシーズン（143試合）をシミュレートし、最も平均得点が高かった打順と低かった打順を提示します。任意で選択した9名の選手の並び替えでの探索も可能です。

## 技術スタック

- **言語**: Python
- **フレームワーク**: Streamlit
- **ライブラリ**: Pandas, NumPy

## ファイル構造

```
.
├── .github/                 # GitHub Actions ワークフロー
├── .gitignore
├── .python-version
├── Design.md
├── GEMINI.md
├── README.md
├── app/
│   ├── pages/               # Streamlitのページ
│   │   ├── about.py
│   │   └── main_app.py
│   └── utils/               # ユーティリティスクリプト
│       ├── constants.py
│       ├── data_process.py
│       ├── game.py
│       ├── get_default_lineup.py
│       ├── get_player_data.py
│       ├── load_data.py
│       ├── player.py
│       └── simulator.py
├── data/
│   ├── processed/           # 加工済みデータ
│   └── raw/                 # スクレイピングした生データ
├── gamini-log/              # 開発ログ
├── pyproject.toml
├── task.md                  # タスク管理
├── tests/                   # テストコード
└── uv.lock
```

## セットアップと実行方法

1. **リポジトリをクローン**:
   ```bash
   git clone https://github.com/your-username/NPB_Game_Simulator.git
   cd NPB_Game_Simulator
   ```

2. **依存ライブラリのインストール**:
   `uv` を使用して `pyproject.toml` に記載された依存ライブラリをインストールします。
   ```bash
   uv sync
   ```

3. **Streamlitアプリケーションを実行**:
   ```bash
   uv run streamlit run app/pages/main_app.py
   ```

ブラウザで `http://localhost:8501` を開くと、アプリケーションが表示されます。

## Streamlit Cloudでの利用

本アプリケーションはStreamlit Cloudにデプロイされており、以下のURLから直接アクセスして利用することも可能です。

[NPB Game Simulator on Streamlit Cloud](https://npbgamesimulator-gpuczxpycyknrzbjc8x2d8.streamlit.app/)

## 使い方

1. サイドバーから**年度**と**チーム**を選択します。
2. **「任意打順でシミュレーション」** タブで、好きな選手を1番から9番までに配置し、「シミュレーション実行」ボタンをクリックします。1試合の詳細結果と、1年間のシミュレーション結果が表示されます。
3. **「最強打順を探索」** タブで、試行したい打順の数を入力し、シミュレーションモードを選択して「探索開始」ボタンをクリックすると、最も効率の良い打順と低い打順が表示されます。
