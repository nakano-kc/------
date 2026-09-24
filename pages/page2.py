# ライブラリ・モジュールの読み込み
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from utils import export_excel

import streamlit as st
from datetime import date
import pandas as pd
import platform
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="集計管理",
    page_icon="📊",
    layout="wide"
)

if not st.session_state.get("authentication_status"):
    st.warning("先にログインページからログインしてください。")
    st.stop()

name = st.session_state.get("name")
username = st.session_state.get("username")

st.sidebar.write(f"ログイン中：{name}")

csv_file = f"kakeibo_{username}.csv"

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'MS Gothic'
else:
    plt.rcParams['font.family'] = 'DejaVu Sans'

st.title("📈 集計管理")

tab_monthly, tab_yearly = st.tabs(["📅 月次集計", "📊 年間集計"])

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------














# 月次集計処理              
with tab_monthly:
    st.subheader("月次集計")
    # 年・月選択
    current_year = date.today().year
    current_month = date.today().month
    col1, col2 = st.columns(2)
    with col1:
        year_range = range(current_year - 2, current_year + 10)
        selected_year = st.selectbox("年", year_range, index=2, key="月間")
    with col2:
        selected_month = st.selectbox("月", range(1, 13), index=current_month - 1)

    if os.path.exists(csv_file):
        # CSVをDataFrameとして読み込む 
        df = pd.read_csv(csv_file)
            # データ：df = 家計簿データ全体
        # 日付列をdatetime型に変換
        df["日付"] = pd.to_datetime(df["日付"], format="mixed")
        # 指定した年月のデータだけを抽出
        filtered = df[
            (df["日付"].dt.year == selected_year) &
            (df["日付"].dt.month == selected_month)
        ]
            # データ：filtered = 指定年月の家計簿データ
        # 指定した月にデータが1件もない場合
        if filtered.empty:
            st.info("この月のデータはありません")
        else:
            # 収入の金額を合計
            income = filtered[filtered["種別"] == "収入"]["金額"].sum()
            # 支出の金額を合計
            expense = filtered[filtered["種別"] == "支出"]["金額"].sum()
            # 収支を計算する
            balance = income - expense
            # 画面に結果を表示する
            col1, col2, col3 = st.columns(3)
            col1.metric("総収入", f"¥{income:,}")
            col2.metric("総支出", f"¥{expense:,}")
            col3.metric("収支", f"¥{balance:,}", delta = f"{balance:,}")
            # カテゴリごとにデータをグループ分けして、金額を合計する
            st.subheader("カテゴリ別内訳")
            tf1, tf2 = st.columns(2)
            with tf1:
                month_categories = ["全て"] + sorted(filtered["カテゴリ"].unique().tolist())
                filter_cat_month = st.selectbox("カテゴリ", month_categories, key="filter_cat_month")
            with tf2:
                filter_kw_month = st.text_input("キーボード（項目名）", "", key="filter_kw_month")
            filtered_view = filtered.copy()
            if filter_cat_month != "全て":
                filtered_view = filtered_view[filtered_view["カテゴリ"] == filter_cat_month]
            if filter_kw_month:
                filtered_view = filtered_view[filtered_view["項目"].str.contains(filter_kw_month,na=False)]
            category_summary = filtered_view.groupby(["種別", "カテゴリ"])["金額"].sum().reset_index()
            #category_summary["日付"] = category_summary["日付"].dt.strftime("%m/%d")
            category_summary.columns = ["種別", "カテゴリ", "合計金額"]
            category_summary["合計金額"] = category_summary["合計金額"].apply(lambda x: f"¥{x:,}")
            category_summary.index = category_summary.index + 1
            st.dataframe(category_summary, use_container_width=True)
            # 月次グラフ ★
            col_left, col_center, col_right = st.columns(3)
            # 左側の列で支出グラフを作成する
            with col_left:
                #「支出」のデータだけを取り出す
                expense_data = filtered[filtered["種別"] == "支出"]
                # 支出データがある場合だけグラフを作成する
                if not expense_data.empty:
                    # 支出をカテゴリごとに分けて、カテゴリごとの金額を合計する
                    exp_summary = expense_data.groupby("カテゴリ")["金額"].sum()
                    exp_summary = exp_summary.sort_values(ascending=False)
                    # 円グラフを作成する
                    fig1, ax1 = plt.subplots(figsize=(4, 3.5))
                
                    # カテゴリごとの支出金額を円グラフで表示する
                    wedges, texts, autotexts = ax1.pie(exp_summary, labels=None, autopct="%1.1f%%",
                                        startangle=90, counterclock=False, textprops={'fontsize': 10, 'color':'white'})
                    ax1.set_title("支出内訳", fontsize=15)
                    # 合計金額を小さい円グラフに重ねて表示する
                    total = exp_summary.sum()
                    ax1.pie([total], radius=0.4, colors=["white"])
                    # 金額の桁数に合わせて文字サイズを調整
                    if total >= 10000000:
                        fontsize = 8.2
                    elif total >= 100000:
                        fontsize = 9
                    else:
                        fontsize = 10                    
                    ax1.text(0, 0, f"合計:{total}円", ha="center", va="center", fontsize=fontsize)
                    # 作成したグラフをStreamlitの画面に表示する
                    st.pyplot(fig1, use_container_width=False)
                    # 使用したグラフを閉じて後片付けする
                    plt.close(fig1)
            with col_center:
            
                # カテゴリごとの金額を合計する
                for i, (category, amount) in enumerate(exp_summary.items()):
                    # 円グラフのカテゴリと同じ色を取得
                    color = wedges[i].get_facecolor()
                    # カテゴリの構成比を計算
                    total = exp_summary.sum()
                    percentage = (amount / total) * 100
                    # RGBAの色をRGB（0～255）に変換
                    r = int(color[0] * 255)
                    g = int(color[1] * 255)
                    b = int(color[2] * 255)
                    # HTMLで使えるRGB形式にする
                    rgb_color = f"rgb({r}, {g}, {b})"
                    # 色・カテゴリ・金額・割合を画面に表示
                    st.markdown(
                        f'<span style="color:{rgb_color}; font-size:60px; vertical-align:middle">■</span> {category} {amount}円 ({percentage:.1f}%)',
                        unsafe_allow_html=True
                        )

            # ダウンロードボタンHTML
            st.subheader("📥 Excelエクスポート")
            buffer = export_excel(df, selected_year, selected_month)
            st.download_button(
                label="📥 ダウンロード",
                data=buffer,
                file_name=f"家計簿_{selected_year}年{selected_month}月.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
                    
    else:
        st.info("まだデータがありません")



# 年間集計処理
with tab_yearly:
    st.subheader("年間集計")
    # 年選択
    current_year = date.today().year
    year_range = range(current_year - 2, current_year + 3)
    selected_year = st.selectbox("年", year_range, index=2, key="年間")
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df["日付"] = pd.to_datetime(df["日付"], format="mixed")
        # 選択した年のデータだけに絞り込む
        filtered = df[(df["日付"].dt.year == selected_year)]
        if filtered.empty:
            st.info("この年のデータはありません")
        else:
            # 月・種別ごとに金額を合計
            monthly_bar = filtered.groupby([filtered["日付"].dt.month, "種別"])["金額"].sum().unstack(fill_value=0)
            # 棒の幅
            width = 0.4
            # 棒グラフを作成(bar == 棒グラフの形式)
            fig3, ax3 = plt.subplots(figsize=(6, 2), dpi=150)
            # 収入を棒グラフで表示
            if "収入" in monthly_bar.columns:
                ax3.bar(monthly_bar.index - width / 2, monthly_bar["収入"], width=width, label="収入", color="#2CA02C")
            # 支出を棒グラフで表示
            if "支出" in monthly_bar.columns:
                ax3.bar(monthly_bar.index + width / 2, monthly_bar["支出"], width=width, label="支出", color="#1F77B4")
            # グラフの設定
            ax3.set_title("月別推移")
            ax3.set_xlabel("月")
            ax3.set_ylabel("金額    ", rotation=0)
            ax3.set_xticks(range(1, 13))
            #ax3.tick_params(labelsize=8)
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            # グラフを画面に表示
            st.pyplot(fig3, use_container_width=False)
            plt.close(fig3)
        
            # 年間の収支計算処理
            income = filtered[filtered["種別"] == "収入"]["金額"].sum()
            expense = filtered[filtered["種別"] == "支出"]["金額"].sum()
            balance = income - expense
            # 画面に結果を表示する
            col1, col2, col3 = st.columns(3)
            col1.metric("総収入", f"¥{income:,}")
            col2.metric("総支出", f"¥{expense:,}")
            col3.metric("収支", f"¥{balance:,}", delta = f"{balance:,}")
            # カテゴリごとにデータをグループ分けして、金額を合計する
            st.subheader("カテゴリ別内訳")
            category_summary = filtered.groupby(["種別", "カテゴリ"])["金額"].sum().reset_index()
            #category_summary["日付"] = category_summary["日付"].dt.strftime("%m/%d")
            category_summary.columns = ["種別", "カテゴリ", "合計金額"]
            category_summary["合計金額"] = category_summary["合計金額"].apply(lambda x: f"¥{x:,}")
            category_summary.index = category_summary.index + 1
            st.dataframe(category_summary, use_container_width=True)

            # 前年までの収支を計算し画面に表示する
            