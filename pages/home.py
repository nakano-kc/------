# ライブラリ・モジュールの読み込み
import sys
import os

# pages/ フォルダの「ひとつ上の親フォルダ（ルート）」をパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# パッケージとしてインポートする
from utils import load_categories, save_categories, export_excel

import streamlit as st
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="ホーム",
    page_icon="🏠",
    layout="wide"
)

if not st.session_state.get("authentication_status"):
    st.warning("先にログインページからログインしてください。")
    st.stop()

name = st.session_state.get("name")
username = st.session_state.get("username")

csv_file = f"kakeibo_{username}.csv"
csv_file = f"kakeibo_{username}.csv"

# セッションにカテゴリが保存されていない、またはNoneの場合は読み込む
if "categories" not in st.session_state or st.session_state["categories"] is None:
    st.session_state["categories"] = load_categories()

categories = st.session_state["categories"]

st.title("📝 収支管理")
# st.write("ログイン後に表示されるホーム画面です")
# st.info("このページはログイン済みユーザーが閲覧できます")

# タブ構成
tabs = st.tabs(["📝 入力"])
tab1 = tabs[0]

# 入力画面
with tab1:
    # 入力フォーム
    st.subheader("📝 支出・収入を入力")
    # ユーザーから家計簿データを入力
    # 日付入力
    input_date = st.date_input("日付", date.today())
    
    # 種別選択(category_type == "種別")
    category_type = st.selectbox("種別", ["収入","支出"])

    with st.expander(f"🛠️ {category_type}のカテゴリを追加・削除する"):
        col_add, col_del = st.columns(2)

        with col_add:
            st.write("**カテゴリ追加**")
            new_cat_input = st.text_input("新しいカテゴリ名", key="inline_new_cat")
            if st.button("追加する", key="inline_add_btn"):
                if new_cat_input not in categories[category_type]:
                    categories[category_type].append(new_cat_input)
                    save_categories(categories)
                    st.success(f"✅ {new_cat_input}を追加しました！")
                    st.rerun()
                else:
                    st.warning("既に存在します。")
            else:
                st.warning("カテゴリ名を入力してください。")

        with col_del:
            st.write("**カテゴリ削除**")


            if "delete_target" not in st.session_state:
                st.session_state["delete_target"] = None
                st.session_state["delete_type"] = None
 
            for item in categories[category_type].copy():
                c1, c2 = st.columns([3,1])
                with c1:
                    st.write(f" ・{item}")
                with c2:
                    if st.button("🗑️", key=f"inline_del_{category_type}_{item}"):
                        if len(categories[category_type]) <= 1:
                            st.warning("最低1つ必要です。")                       
                        else :
                            st.session_state["delete_target"] = item
                            st.session_state["delete_type"] = category_type
                            st.rerun()

            if st.session_state.get("delete_target") and st.session_state.get("delete_type") == category_type:
                target = st.session_state["delete_target"]
                st.warning(f" 「{target}」を削除しますか？")

                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("はい", key=f"confirm_yes_{category_type}"):
                        categories[category_type].remove(target)
                        save_categories(categories)
                        st.success(f"🗑️ 「{target}」を削除しました！")

                        st.session_state["delete_target"] = None
                        st.session_state["delete_type"] = None
                        st.rerun()

                with col_no:
                    if st.button("キャンセル", key=f"confirm_no_{category_type}"):

                        st.session_state["delete_target"] = None
                        st.session_state["delete_type"] = None
                        st.rerun()

    # カテゴリ選択(category == "カテゴリ")
    category = st.selectbox("カテゴリ", categories[category_type], key="input_category_select")

    # 項目入力(item == "項目")※動作確認用：事前入力ではなく、例として上書きできる形式にできるか？
    if category_type == "収入":
        item = st.text_input("項目", "内訳", key="input_item_income")
    if category_type == "支出":
        item = st.text_input("項目", "品目、お店", key="input_item_expence")
    # 金額入力(amount == "金額")
    amount = st.number_input("金額", min_value=0, value=500, key="input_amount")

    # 登録ボタンが押されたときの処理
    if st.button("登録"):
        if not category:
            st.error("有効なカテゴリを選択・追加してください。")
        else:
            
        # 新しいデータを作成
            new_data = pd.DataFrame({
                "ユーザー": [username],
                "日付": [input_date],
                "種別": [category_type],
                "カテゴリ": [category],
                "項目": [item],
                "金額": [amount]
            })

            # CSVファイルが存在するか確認
            if os.path.exists(csv_file):
                # CSVをDataFrameとして読み込む
                df = pd.read_csv(csv_file)
                # 既存ファイルにデータ追加
                df = pd.concat([df, new_data], ignore_index=True)
            else:
                # 新規ファイル作成
                df = new_data

            # CSV形式で保存
            df.to_csv(csv_file, index=False, encoding="utf-8-sig")
            st.success(f"✅ {input_date} | {category} | {item}:{amount}円を登録しました！")

    # 登録済みのデータを表示★
    st.subheader("📊 登録済みデータ")
    # CSVファイルが存在する場合
    if os.path.exists(csv_file):
        # フィルターを3列に分けて横並びに表示する
        fc1, fc2, fc3, fc4 = st.columns(4)
        # CSVファイルをDataFrameとして読み込む
        df_edit = pd.read_csv(csv_file)
        # 表示対象をログインしたユーザーに絞り込む
        df_edit = df_edit[df_edit["ユーザー"] == username].copy()
        # 元のCSVの行番号を記録
        df_edit["_元の行番号"] = df_edit.index
        # 日付をdatetime型に変換
        df_edit["日付"] = pd.to_datetime(df_edit["日付"], format="mixed")
        # データを日付順に表示する
        df_edit = df_edit.sort_values("日付")

        # 1列目：年月フィルター
        with fc1:
            date_options = df_edit["日付"].dt.strftime("%Y/%m").unique()
            filter_date = st.selectbox("日付", date_options, key="filter_date")

        # 2列目：種別フィルター　〈「全て」「収入」「支出」から選択する〉
        with fc2:
            filter_type = st.selectbox("種別", ["全て", "収入", "支出"], key="filter_type")

        # 3列目：カテゴリフィルター　〈 収支の種類（全て / 収入 / 支出）に応じてセレクトボックスの中身を分岐〉
        with fc3:
            # set()：同じカテゴリが重複していても1つにまとめる
            # for v in categories.values()：収入・支出のカテゴリ一覧を順番に取り出す
            # for c in v：取り出したカテゴリ一覧からカテゴリ名を1つずつ取り出す

            # 全カテゴリを結合・重複削除して「全て」を先頭に追加
            if filter_type == "全て" :
                options = ["全て"] + sorted(set(c for v in categories.values() for c in v))

            # 収入のカテゴリ一覧を取得して「全て」を追加
            if filter_type == "収入":
                options = ["全て"] + sorted(list(categories["収入"]))

            # 支出のカテゴリ一覧を取得して「全て」を追加
            if filter_type == "支出":
                options = ["全て"] + sorted(list(categories["支出"]))

            # カテゴリを選択する
            filter_category = st.selectbox("カテゴリ", options, key="filter_category")

        # 4列目：キーワードフィルター　〈項目名を検索するための入力欄〉
        with fc4:
            filter_keyword = st.text_input("キーワード（項目名）", "", key="filter_keyword")
        # 日付が一致するデータだけに絞り込む
        if filter_date:
            df_edit = df_edit[df_edit["日付"].dt.strftime("%Y/%m") == filter_date]
        # 種別が「全て」ではない場合－選択した種別のデータだけに絞り込む
        if filter_type != "全て":
            df_edit = df_edit[df_edit["種別"] == filter_type]
        # カテゴリが「全て」ではない場合－選択したカテゴリのデータだけに絞り込む
        if filter_category != "全て":
            df_edit = df_edit[df_edit["カテゴリ"] == filter_category]
        # キーワードが入力されている場合－「項目」列にキーワードを含むデータだけに絞り込む
        if filter_keyword:
            df_edit = df_edit[df_edit["項目"].str.contains(filter_keyword, na=False)]

        # 削除用のチェックボックス列を追加する
        df_edit["削除"] = False

        # 表示用に行番号を1から始める
        df_edit.index = range(1, len(df_edit) + 1)
        # 日付のみの表示にする（時間なし）
        df_edit["日付"] = df_edit["日付"].dt.strftime("%Y/%m/%d")
        # 編集可能な表を画面に表示
        edited_df = st.data_editor(
            df_edit,
            # 「削除」列をチェックボックスとして表示
            column_config={
                "削除":st.column_config.CheckboxColumn("削除", default=False),
            } ,
            # 表示する列の順番を指定
            column_order=["日付", "種別", "カテゴリ", "項目", "金額", "削除"],
            # 行番号を表示しない
            hide_index=False,
            # 表の横幅を画面いっぱいにする
            use_container_width=True
        )
        # 「保存」と「削除」のボタンを横並びにする
        col_save, col_delete = st.columns(2)
        # 編集内容を保存する処理
        with col_save:
            if st.button("💾編集を保存"):
                all_df = pd.read_csv(csv_file)
                # 画面で編集したデータから「削除」列を取り除く
                edited_data = edited_df.drop(columns=["削除"]).copy()
                # 日付を日付データに戻す
                edited_data["日付"] = pd.to_datetime(
                    edited_data["日付"],
                    format="mixed"
                )
                # CSV側の日付も日付データにする
                all_df["日付"] = pd.to_datetime(
                    all_df["日付"],
                    format="mixed"
                )
                # 編集した行を元のデータに反映する
                for index, row in edited_data.iterrows():
                    # 元のCSVの行番号を取得
                    original_index = int(row["_元の行番号"])
                    # 元の行を更新する
                    all_df.loc[original_index, ["日付", "種別", "カテゴリ", "項目", "金額"]] = [
                        row["日付"],
                        row["種別"],
                        row["カテゴリ"],
                        row["項目"],
                        row["金額"]
                    ]
                # 全データをCSVに保存
                all_df.to_csv(csv_file, index=False, encoding="utf-8-sig")
                st.success("✅保存しました")
                # 保存後に画面を再読み込み
                st.rerun()

        # 選択した行を削除する処理
        with col_delete:
            if st.button("🗑️選択行を削除"):
                # CSV全体を読み込む
                all_df = pd.read_csv(csv_file)
                # 削除する元の行番号を取得
                delete_indexes = edited_df.loc[
                    edited_df["削除"] == True,
                    "_元の行番号"
                ].astype(int).tolist()
                # 削除対象がある場合
                if delete_indexes:
                    # 元のCSVから対象行を削除
                    all_df = all_df.drop(index=delete_indexes)
                    # CSVを保存
                    all_df.to_csv(csv_file, index=False, encoding="utf-8-sig")
                    # → チェックを入れた行は削除される

                    st.success("✅保存しました")
                # 削除後に画面を再読み込み
                    st.rerun()

    # CSVファイルが存在しない場合
    else:
        st.info("まだデータがありません")