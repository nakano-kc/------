# ライブラリ・モジュールの読み込み
# プログラムで必要な機能を使えるようにする
import sys
import os
# pages/ フォルダの「ひとつ上の親フォルダ（ルート）」をパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import streamlit as st #-------------Web画面を作る
# from datetime import date
# import pandas as pd #----------------表データを扱う
import os #--------------------------コンピューター上のファイルやフォルダなどを操作する
# import json #------------------------JSON形式のデータを扱う（今回はカテゴリ情報を扱う）
#import matplotlib.pyplot as plt #----グラフを作る
# import openpyxl #--------------------Excelを扱う
# from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
# from openpyxl.utils import get_column_letter
# import io
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader



st.set_page_config(
    page_title="ログインページ",
    page_icon="🔑",
    layout="wide"
)
with open("config.yaml", "r", encoding="utf-8-sig") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config ["cookie"]["expiry_days"]
)

if not st.session_state.get("authentication_status"):

    login_tab, register_tab = st.tabs(["ログイン", "新規登録"])

    with login_tab:
        authenticator.login(
            location="main",
            fields={
                'Form name': 'ログイン',
                'Username': 'ユーザー名',
                'Password': 'パスワード',
                'Login': 'ログイン'
            }
        )
        if st.session_state.get("authentication_status") is False:
            st.error("ユーザー名またはパスワードが正しくありません。")
        if st.session_state.get("authentication_status") is None:
            st.warning("ユーザー名またはパスワードを入力してください。")

    with register_tab:

        st.subheader("新規アカウント作成")

        # パスワードの要件を表示する
        st.info(
            "**以下の要件でパスワードを作成してください**\n"
            "- 8文字以上、20文字以下\n"
            "- 大文字・数字・特殊文字('@$!%*?&')を含む"
        )

        try:
            email_reg, username_reg, name_reg = authenticator.register_user(
                pre_authorized=None,
                fields={
                'Form name': 'アカウント登録',
                'First name': '氏',
                'Last name': '名',
                'Email': 'メールアドレス',
                'Username': 'ユーザー名',
                'Password': '新しいパスワード',
                'Repeat password': 'パスワード(確認)',
                'Password hint': 'パスワードにヒント',
                'Captcha': '画像の数字を入力してください',
                'Register': '登録'
            }
        )
        
            if email_reg:
                st.success("ユーザー登録が完了しました！「ログイン」タブからログインしてください。")
                with open("config.yaml", "w", encoding="utf-8-sig") as file:
                    yaml.dump(config, file, default_flow_style=False, allow_unicode=True)

        except Exception as e:
            error_message = str(e)
            #エラーを日本語表記にする
            if "Password/repeat password fields cannot be empty" in error_message:
                st.error("パスワードおよび確認用パスワードを入力してください。")
            elif "Passwords do not match" in error_message:
                st.error("パスワードが一致していません。もう一度確認してください。")
            elif "already taken" in error_message:
                st.error("このユーザー名またはメールアドレスは既に使用されています。")
            elif "Captcha entered incorrectly" in error_message:
                st.error("画像認証の入力が正しくありません。")
            elif "characters" in error_message or "Password" in error_message:
                st.error("入力形式が正しくないか、パスワードの要件を満たしていません。")
            elif "not valid" in error_message:
                st.error("未入力の項目があります。すべての項目を入力してください。")
            else:
                st.error(f"登録エラーが発生しました：{error_message}")



    st.stop()

authenticator.logout("ログアウト", "sidebar")
name = st.session_state.get("name")
username = st.session_state.get("username")

roles = st.session_state.get("roles") or []

st.sidebar.write(f"ログイン中: {name}")
st.sidebar.write(f"ユーザー名: {username}")


home_page = st.Page("pages/home.py", title="収支管理", icon="📝")
page1 = st.Page("pages/page1.py", title="収支一覧", icon="📄")
page2 = st.Page("pages/page2.py", title="集計管理", icon="📊")

if "admin" in roles:
    pages = {
        " 家計簿アプリ": [home_page, page2]
    }
else:
    pages = {
        " 家計簿アプリ": [home_page, page2]
    }

pg = st.navigation(pages)
pg.run()

# # matplotlibの日本語フォント設定
# plt.rcParams['font.family'] = 'MS Gothic'

# アプリのタイトル名
#st.title("家計簿アプリ")


# # Excel出力用のデザイン設定
# HEADER_COLOR = "2D3748" # ダークグレー（ 家計簿アプリヘッダー）
# ACCENT_COLOR = "4A90D9" # ブルー（タイトル・セクション）
# ZEBRA_COLOR = "EDF2F7"  # 薄グレー（交互行）
# WHITE = "FFFFFF"

# def header_style(cell, color=HEADER_COLOR):
#     cell.fill = PatternFill("solid", fgColor=color)
#     cell.font = Font(color=WHITE, bold=True, size=10)
#     cell.alignment = Alignment(horizontal="center", vertical="center")

# def zebra_style(cell, row_idx):
#     if row_idx % 2 == 0:
#         cell.fill = PatternFill("solid", fgColor=ZEBRA_COLOR)
#     cell.alignment = Alignment(horizontal="left", vertical="center")

# def money_style(cell, row_idx):
#     if row_idx % 2 == 0:
#         cell.fill = PatternFill("solid", fgColor=ZEBRA_COLOR)
#     cell.number_format = '#,##0'
#     cell.alignment = Alignment(horizontal="right", vertical="center")

# def thin_border():
#     s = Side(style="thin", color="CBD5E0")
#     return Border(left=s, right=s, top=s, bottom=s)




# # 指定した年月の家計簿データをExcelファイルとして作成する(df == "家計簿データ")
# def export_excel(df, selected_year, selected_month):

#     # Excelブックを作成
#     wb = openpyxl.Workbook()

#     # ワークシートを取得して名前を設定
#     ws1 = wb.active
#     ws1.title = f"{selected_year}年{selected_month}月"

#     # 日付をExcel表示用の文字列に変換
#     monthly_df = df[
#         (df["日付"].dt.year == selected_year) &
#         (df["日付"].dt.month == selected_month)
#     ].copy()
#     monthly_df["日付"] = monthly_df["日付"].dt.strftime("%Y/%m/%d")

#     # ーータイトル行
#     ws1.merge_cells("A1:E1")
#     title_cell = ws1["A1"]
#     title_cell.value = f"{selected_year}年{selected_month}月 家計簿データ"
#     title_cell.fill = PatternFill("solid", fgColor=ACCENT_COLOR)
#     title_cell.font = Font(color=WHITE, bold=True, size=12)
#     title_cell.alignment = Alignment(horizontal="center", vertical= "center")
#     ws1.row_dimensions[1].height = 28

#     # ーーヘッダー行
#     headers = ["日付", "種別", "カテゴリ", "項目", "金額"]
#     for col, h in enumerate(headers, 1):
#         cell = ws1.cell(row=2, column=col, value=h)
#         header_style(cell)
#         cell.border = thin_border()
#     ws1.row_dimensions[2].height = 22

#     # ーーデータ行
#     for row_idx, (_, row) in enumerate(monthly_df.iterrows(), 1):
#         values = [row["日付"], row["種別"], row["カテゴリ"], row["項目"], row["金額"]]
#         for col, val in enumerate(values, 1):
#             cell = ws1.cell(row=row_idx + 2, column=col, value=val)
#             cell.border = thin_border()
#             if col == 5:
#                 money_style(cell, row_idx)
#             else:
#                 zebra_style(cell, row_idx)
#         ws1.row_dimensions[row_idx + 2].height = 18

#     # カテゴリ別集計
#     # ーータイトル
#     summary_start = len(monthly_df) + 5
#     ws1.merge_cells(f"A{summary_start}:C{summary_start}")
#     s_title = ws1[f"A{summary_start}"]
#     s_title.value = "カテゴリ別集計"
#     s_title.fill = PatternFill("solid", fgColor=ACCENT_COLOR)
#     s_title.font = Font(color=WHITE, bold=True, size=11)
#     s_title.alignment = Alignment(horizontal="center", vertical="center")

#     # ーーヘッダー
#     s_headers = ["種別", "カテゴリ", "合計金額"]
#     for col, h in enumerate(s_headers, 1):
#         cell = ws1.cell(row=summary_start + 1, column=col, value=h)
#         header_style(cell)
#         cell.border = thin_border()

#     # ーーデータ集計
#     cat_summary = monthly_df.groupby(["種別", "カテゴリ"])["金額"].sum().reset_index()
#     for row_idx, (_, row) in enumerate(cat_summary.iterrows(), 1):
#         for col, val in enumerate([row["種別"], row["カテゴリ"], row["金額"]],  1):
#             cell = ws1.cell(row=summary_start + 1 + row_idx, column= col, value=val)
#             cell.border = thin_border()
#             if col == 3:
#                 money_style(cell, row_idx)
#             else:
#                 zebra_style(cell, row_idx)

#     # ーー列幅
#     for col, width in zip(range(1, 6), [14, 8, 12, 20, 12]):
#         ws1.column_dimensions[get_column_letter(col)].width = width

#     # ーーExcelファイルをメモリ上に保存して返す
#     buffer = io.BytesIO()
#     wb.save(buffer)
#     buffer.seek(0)
#     return buffer





# # タブ構成
# tab1, tab2, tab3 = st.tabs(["📝 入力", "📅 月次集計", "📊 年間集計"])
# # 入力画面
# with tab1:
#     # 入力フォーム
#     st.subheader("📝 支出を入力")
#     # ユーザーから家計簿データを入力
#     # 日付入力
#     input_date = st.date_input("日付", date.today())
    
#     # 種別選択(category_type == "種別")
#     category_type = st.selectbox("種別", ["収入","支出"])

#     with st.expander(f"🛠️ {category_type}のカテゴリを追加・削除する"):
#         col_add, col_del = st.columns(2)

#         with col_add:
#             st.write("**カテゴリ追加**")
#             new_cat_input = st.text_input("新しいカテゴリ名", key="inline_new_cat")
#             if st.button("追加する", key="inline_add_btn"):
#                 if new_cat_input not in categories[category_type]:
#                     categories[category_type].append(new_cat_input)
#                     save_categories(categories)
#                     st.success(f"✅ {new_cat_input}を追加しました！")
#                     st.rerun()
#                 else:
#                     st.warning("既に存在します。")
#             else:
#                 st.warning("カテゴリ名を入力してください。")

#         with col_del:
#             st.write("**カテゴリ削除**")


#             if "delete_target" not in st.session_state:
#                 st.session_state["delete_target"] = None
#                 st.session_state["delete_type"] = None
 
#             for item in categories[category_type].copy():
#                 c1, c2 = st.columns([3,1])
#                 with c1:
#                     st.write(f" ・{item}")
#                 with c2:
#                     if st.button("🗑️", key=f"inline_del_{category_type}_{item}"):
#                         if len(categories[category_type]) <= 1:
#                             st.warning("最低1つ必要です。")                       
#                         else :
#                             st.session_state["delete_target"] = item
#                             st.session_state["delete_type"] = category_type
#                             st.rerun()

#             if st.session_state.get("delete_target") and st.session_state.get("delete_type") == category_type:
#                 target = st.session_state["delete_target"]
#                 st.warning(f" 「{target}」を削除しますか？")

#                 col_yes, col_no = st.columns(2)
#                 with col_yes:
#                     if st.button("はい", key=f"confirm_yes_{category_type}"):
#                         categories[category_type].remove(target)
#                         save_categories(categories)
#                         st.success(f"🗑️ 「{target}」を削除しました！")

#                         st.session_state["delete_target"] = None
#                         st.session_state["delete_type"] = None
#                         st.rerun()

#                 with col_no:
#                     if st.button("キャンセル", key=f"confirm_no_{category_type}"):

#                         st.session_state["delete_target"] = None
#                         st.session_state["delete_type"] = None
#                         st.rerun()


#     # # 現在のカテゴリ一覧に「新しいカテゴリを追加」と「カテゴリを削除する」という選択肢を一時的に追加する
#     # category_options = categories[category_type] + ["✚ 新しいカテゴリを追加...", "✖ カテゴリを削除する..."]
#     # selected_cat = st.selectbox("カテゴリ", category_options)

#     # #「新しいカテゴリを追加...」が選ばれた場合の処理
#     # if selected_cat == "✚ 新しいカテゴリを追加...":
#     #     new_cat_input = st.text_input("追加したい新しいカテゴリ名を入力してください")
#     #     if st.button("カテゴリを登録"):
#     #         if new_cat_input:
#     #             if new_cat_input not in categories[category_type]:
#     #                 # リストに追加してJSONに保存
#     #                 categories[category_type].append(new_cat_input)
#     #                 save_categories(categories)
#     #                 st.success(f"✅ {new_cat_input}を追加しました！")

#     #                 st.rerun()
#     #             else:
#     #                 st.warning("そのカテゴリは既に存在します。")
#     #         else:
#     #             st.warning("カテゴリ名を入力してください")

#     #     # 追加が完了するまでは、登録ボタンでエラーが出ないように空にしておく
#     #     category = None
#     # else:
#     #     category = selected_cat

#     # 現在のカテゴリ一覧に「カテゴリを削除」という項目を

#     # カテゴリ選択(category == "カテゴリ")
#     category = st.selectbox("カテゴリ", categories[category_type], key="input_category_select")

#     # 項目入力(item == "項目")※動作確認用：後で削除予定
#     if category_type == "収入":
#         item = st.text_input("項目", "内訳", key="input_item_income")
#     if category_type == "支出":
#         item = st.text_input("項目", "品目、お店", key="input_item_expence")
#     # 金額入力(amount == "金額")
#     amount = st.number_input("金額", min_value=0, value=500, key="input_amount")

#     # 登録ボタンが押されたときの処理
#     if st.button("登録"):
#         if not category:
#             st.error("有効なカテゴリを選択・追加してください。")
#         else:
            
#         # 新しいデータを作成
#             new_data = pd.DataFrame({
#                 "ユーザー": [username],
#                 "日付": [input_date],
#                 "種別": [category_type],
#                 "カテゴリ": [category],
#                 "項目": [item],
#                 "金額": [amount]
#             })

#             # CSVファイルが存在するか確認
#             if os.path.exists(csv_file):
#                 # CSVをDataFrameとして読み込む
#                 df = pd.read_csv(csv_file)
#                 # 既存ファイルにデータ追加
#                 df = pd.concat([df, new_data], ignore_index=True)
#             else:
#                 # 新規ファイル作成
#                 df = new_data

#             # CSV形式で保存
#             df.to_csv(csv_file, index=False, encoding="utf-8-sig")
#             st.success(f"✅ {input_date} | {category} | {item}:{amount}円を登録しました！")

#     # 登録済みのデータを表示★
#     st.subheader("📊 登録済みデータ")
#     # CSVファイルが存在する場合
#     if os.path.exists(csv_file):
#         # フィルターを3列に分けて横並びに表示する
#         fc1, fc2, fc3, fc4 = st.columns(4)
#         # CSVファイルをDataFrameとして読み込む
#         df_edit = pd.read_csv(csv_file)
#         # 表示対象をログインしたユーザーに絞り込む
#         df_edit = df_edit[df_edit["ユーザー"] == username].copy()
#         # 元のCSVの行番号を記録
#         df_edit["_元の行番号"] = df_edit.index
#         # 日付をdatetime型に変換
#         df_edit["日付"] = pd.to_datetime(df_edit["日付"], format="mixed")
#         # データを日付順に表示する
#         df_edit = df_edit.sort_values("日付")

#         # 1列目：年月フィルター
#         with fc1:
#             date_options = df_edit["日付"].dt.strftime("%Y/%m").unique()
#             filter_date = st.selectbox("日付", date_options, key="filter_date")

#         # 2列目：種別フィルター　〈「全て」「収入」「支出」から選択する〉
#         with fc2:
#             filter_type = st.selectbox("種別", ["全て", "収入", "支出"], key="filter_type")

#         # 3列目：カテゴリフィルター　〈 収入・支出の両方に登録されているカテゴリを取り出す〉
#         with fc3:
#             # set()：同じカテゴリが重複していても1つにまとめる
#             # for v in categories.values()：収入・支出のカテゴリ一覧を順番に取り出す
#             # for c in v：取り出したカテゴリ一覧からカテゴリ名を1つずつ取り出す
#             all_categories = ["全て"] + sorted(set(
#                 c for v in categories.values() for c in v
#             ))
#             # カテゴリを選択する
#             filter_category = st.selectbox("カテゴリ", all_categories, key="filter_category")

#         # 4列目：キーワードフィルター　〈項目名を検索するための入力欄〉
#         with fc4:
#             filter_keyword = st.text_input("キーワード（項目名）", "", key="filter_keyword")
#         # 日付が一致するデータだけに絞り込む
#         if filter_date:
#             df_edit = df_edit[df_edit["日付"].dt.strftime("%Y/%m") == filter_date]
#         # 種別が「全て」ではない場合－選択した種別のデータだけに絞り込む
#         if filter_type != "全て":
#             df_edit = df_edit[df_edit["種別"] == filter_type]
#         # カテゴリが「全て」ではない場合－選択したカテゴリのデータだけに絞り込む
#         if filter_category != "全て":
#             df_edit = df_edit[df_edit["カテゴリ"] == filter_category]
#         # キーワードが入力されている場合－「項目」列にキーワードを含むデータだけに絞り込む
#         if filter_keyword:
#             df_edit = df_edit[df_edit["項目"].str.contains(filter_keyword, na=False)]

#         # 削除用のチェックボックス列を追加する
#         df_edit["削除"] = False

#         # 表示用に行番号を1から始める
#         df_edit.index = range(1, len(df_edit) + 1)
#         # 日付のみの表示にする（時間なし）
#         df_edit["日付"] = df_edit["日付"].dt.strftime("%Y/%m/%d")
#         # 編集可能な表を画面に表示
#         edited_df = st.data_editor(
#             df_edit,
#             # 「削除」列をチェックボックスとして表示
#             column_config={
#                 "削除":st.column_config.CheckboxColumn("削除", default=False),
#             } ,
#             # 表示する列の順番を指定
#             column_order=["日付", "種別", "カテゴリ", "項目", "金額", "削除"],
#             # 行番号を表示しない
#             hide_index=False,
#             # 表の横幅を画面いっぱいにする
#             use_container_width=True
#         )
#         # 「保存」と「削除」のボタンを横並びにする
#         col_save, col_delete = st.columns(2)
#         # 編集内容を保存する処理
#         with col_save:
#             if st.button("💾編集を保存"):
#                 all_df = pd.read_csv(csv_file)
#                 # 画面で編集したデータから「削除」列を取り除く
#                 edited_data = edited_df.drop(columns=["削除"]).copy()
#                 # 日付を日付データに戻す
#                 edited_data["日付"] = pd.to_datetime(
#                     edited_data["日付"],
#                     format="mixed"
#                 )
#                 # CSV側の日付も日付データにする
#                 all_df["日付"] = pd.to_datetime(
#                     all_df["日付"],
#                     format="mixed"
#                 )
#                 # 編集した行を元のデータに反映する
#                 for index, row in edited_data.iterrows():
#                     # 元のCSVの行番号を取得
#                     original_index = int(row["_元の行番号"])
#                     # 元の行を更新する
#                     all_df.loc[original_index, ["日付", "種別", "カテゴリ", "項目", "金額"]] = [
#                         row["日付"],
#                         row["種別"],
#                         row["カテゴリ"],
#                         row["項目"],
#                         row["金額"]
#                     ]
#                 # 全データをCSVに保存
#                 all_df.to_csv(csv_file, index=False, encoding="utf-8-sig")
#                 st.success("✅保存しました")
#                 # 保存後に画面を再読み込み
#                 st.rerun()

#         # 選択した行を削除する処理
#         with col_delete:
#             if st.button("🗑️選択行を削除"):
#                 # CSV全体を読み込む
#                 all_df = pd.read_csv(csv_file)
#                 # 削除する元の行番号を取得
#                 delete_indexes = edited_df.loc[
#                     edited_df["削除"] == True,
#                     "_元の行番号"
#                 ].astype(int).tolist()
#                 # 削除対象がある場合
#                 if delete_indexes:
#                     # 元のCSVから対象行を削除
#                     all_df = all_df.drop(index=delete_indexes)
#                     # CSVを保存
#                     all_df.to_csv(csv_file, index=False, encoding="utf-8-sig")
#                     # → チェックを入れた行は削除される

#                     st.success("✅保存しました")
#                 # 削除後に画面を再読み込み
#                     st.rerun()

#     # CSVファイルが存在しない場合
#     else:
#         st.info("まだデータがありません")


# # カテゴリ追加機能
# # with tab2:
# #     st.subheader("カテゴリ管理")
# #     col1, col2 = st.columns(2)
# #     # 現在のカテゴリを見る
# #     with col1:
# #         st.write("**現在のカテゴリ**")
# #         for cat_type, items in categories.items():
# #             st.write(f"【{cat_type}】")
# #             for item in items:
# #                 st.write(f" ・{item}")
# #     # 新しいカテゴリ名を追加
# #     with col2:
# #         st.write("**カテゴリ追加**")
# #         new_type = st.selectbox("種別", ["収入", "支出"], key="new_type")
# #         new_category = st.text_input("新しいカテゴリ名")
# #         # 追加ボタン
# #         if st.button("追加"):
# #             if new_category:
# #                 if new_category not in categories[new_type]:
# #                     categories[new_type].append(new_category)
# #                     save_categories(categories)
# #                     st.success(f"✅ {new_type}に{new_category}を追加しました")
# #                     st.rerun()
# #                 else:
# #                     st.warning("既に登録されています")
# # 月次集計処理              
# with tab2:
#     st.subheader("月次集計")
#     # 年・月選択
#     current_year = date.today().year
#     current_month = date.today().month
#     col1, col2 = st.columns(2)
#     with col1:
#         year_range = range(current_year - 2, current_year + 10)
#         selected_year = st.selectbox("年", year_range, index=2, key="月間")
#     with col2:
#         selected_month = st.selectbox("月", range(1, 13), index=current_month - 1)

#     if os.path.exists(csv_file):
#         # CSVをDataFrameとして読み込む 
#         df = pd.read_csv(csv_file)
#             # データ：df = 家計簿データ全体
#         # 日付列をdatetime型に変換
#         df["日付"] = pd.to_datetime(df["日付"], format="mixed")
#         # 指定した年月のデータだけを抽出
#         filtered = df[
#             (df["日付"].dt.year == selected_year) &
#             (df["日付"].dt.month == selected_month)
#         ]
#             # データ：filtered = 指定年月の家計簿データ
#         # 指定した月にデータが1件もない場合
#         if filtered.empty:
#             st.info("この月のデータはありません")
#         else:
#             # 収入の金額を合計
#             income = filtered[filtered["種別"] == "収入"]["金額"].sum()
#             # 支出の金額を合計
#             expense = filtered[filtered["種別"] == "支出"]["金額"].sum()
#             # 収支を計算する
#             balance = income - expense
#             # 画面に結果を表示する
#             col1, col2, col3 = st.columns(3)
#             col1.metric("総収入", f"¥{income:,}")
#             col2.metric("総支出", f"¥{expense:,}")
#             col3.metric("収支", f"¥{balance:,}", delta = f"{balance:,}")
#             # カテゴリごとにデータをグループ分けして、金額を合計する
#             st.subheader("カテゴリ別内訳")
#             tf1, tf2 = st.columns(2)
#             with tf1:
#                 month_categories = ["全て"] + sorted(filtered["カテゴリ"].unique().tolist())
#                 filter_cat_month = st.selectbox("カテゴリ", month_categories, key="filter_cat_month")
#             with tf2:
#                 filter_kw_month = st.text_input("キーボード（項目名）", "", key="filter_kw_month")
#             filtered_view = filtered.copy()
#             if filter_cat_month != "全て":
#                 filtered_view = filtered_view[filtered_view["カテゴリ"] == filter_cat_month]
#             if filter_kw_month:
#                 filtered_view = filtered_view[filtered_view["項目"].str.contains(filter_kw_month,na=False)]
#             category_summary = filtered_view.groupby(["種別", "カテゴリ"])["金額"].sum().reset_index()
#             #category_summary["日付"] = category_summary["日付"].dt.strftime("%m/%d")
#             category_summary.columns = ["種別", "カテゴリ", "合計金額"]
#             category_summary["合計金額"] = category_summary["合計金額"].apply(lambda x: f"¥{x:,}")
#             category_summary.index = category_summary.index + 1
#             st.dataframe(category_summary, use_container_width=True)
#             # 月次グラフ ★
#             col_left, col_center, col_right = st.columns(3)
#             # 左側の列で支出グラフを作成する
#             with col_left:
#                 #「支出」のデータだけを取り出す
#                 expense_data = filtered[filtered["種別"] == "支出"]
#                 # 支出データがある場合だけグラフを作成する
#                 if not expense_data.empty:
#                     # 支出をカテゴリごとに分けて、カテゴリごとの金額を合計する
#                     exp_summary = expense_data.groupby("カテゴリ")["金額"].sum()
#                     exp_summary = exp_summary.sort_values(ascending=False)
#                     # 円グラフを作成する
#                     fig1, ax1 = plt.subplots(figsize=(4, 3.5))
                
#                     # カテゴリごとの支出金額を円グラフで表示する
#                     wedges, texts, autotexts = ax1.pie(exp_summary, labels=None, autopct="%1.1f%%",
#                                         startangle=90, counterclock=False, textprops={'fontsize': 10, 'color':'white'})
#                     ax1.set_title("支出内訳", fontsize=15)
#                     # 合計金額を小さい円グラフに重ねて表示する
#                     total = exp_summary.sum()
#                     ax1.pie([total], radius=0.4, colors=["white"])
#                     # 金額の桁数に合わせて文字サイズを調整
#                     if total >= 10000000:
#                         fontsize = 8.2
#                     elif total >= 100000:
#                         fontsize = 9
#                     else:
#                         fontsize = 10                    
#                     ax1.text(0, 0, f"合計:{total}円", ha="center", va="center", fontsize=fontsize)
#                     # 作成したグラフをStreamlitの画面に表示する
#                     st.pyplot(fig1, use_container_width=False)
#                     # 使用したグラフを閉じて後片付けする
#                     plt.close(fig1)
#             with col_center:
            
#                 # カテゴリごとの金額を合計する
#                 for i, (category, amount) in enumerate(exp_summary.items()):
#                     # 円グラフのカテゴリと同じ色を取得
#                     color = wedges[i].get_facecolor()
#                     # カテゴリの構成比を計算
#                     total = exp_summary.sum()
#                     percentage = (amount / total) * 100
#                     # RGBAの色をRGB（0～255）に変換
#                     r = int(color[0] * 255)
#                     g = int(color[1] * 255)
#                     b = int(color[2] * 255)
#                     # HTMLで使えるRGB形式にする
#                     rgb_color = f"rgb({r}, {g}, {b})"
#                     # 色・カテゴリ・金額・割合を画面に表示
#                     st.markdown(
#                         f'<span style="color:{rgb_color}; font-size:60px; vertical-align:middle">■</span> {category} {amount}円 ({percentage:.1f}%)',
#                         unsafe_allow_html=True
#                         )

#             # ダウンロードボタンHTML
#             st.subheader("📥 Excelエクスポート")
#             buffer = export_excel(df, selected_year, selected_month)
#             st.download_button(
#                 label="📥 ダウンロード",
#                 data=buffer,
#                 file_name=f"家計簿_{selected_year}年{selected_month}月.xlsx",
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )
                    
#     else:
#         st.info("まだデータがありません")
    
# # 年間集計処理
# with tab3:
#     st.subheader("年間集計")
#     # 年選択
#     current_year = date.today().year
#     year_range = range(current_year - 2, current_year + 3)
#     selected_year = st.selectbox("年", year_range, index=2, key="年間")
#     if os.path.exists(csv_file):
#         df = pd.read_csv(csv_file)
#         df["日付"] = pd.to_datetime(df["日付"], format="mixed")
#         # 選択した年のデータだけに絞り込む
#         filtered = df[(df["日付"].dt.year == selected_year)]
#         if filtered.empty:
#             st.info("この年のデータはありません")
#         else:
#             # 月・種別ごとに金額を合計
#             monthly_bar = filtered.groupby([filtered["日付"].dt.month, "種別"])["金額"].sum().unstack(fill_value=0)
#             # 棒の幅
#             width = 0.4
#             # 棒グラフを作成(bar == 棒グラフの形式)
#             fig3, ax3 = plt.subplots(figsize=(6, 2), dpi=150)
#             # 収入を棒グラフで表示
#             if "収入" in monthly_bar.columns:
#                 ax3.bar(monthly_bar.index - width / 2, monthly_bar["収入"], width=width, label="収入", color="#2CA02C")
#             # 支出を棒グラフで表示
#             if "支出" in monthly_bar.columns:
#                 ax3.bar(monthly_bar.index + width / 2, monthly_bar["支出"], width=width, label="支出", color="#1F77B4")
#             # グラフの設定
#             ax3.set_title("月別推移")
#             ax3.set_xlabel("月")
#             ax3.set_ylabel("金額    ", rotation=0)
#             ax3.set_xticks(range(1, 13))
#             #ax3.tick_params(labelsize=8)
#             ax3.legend()
#             ax3.grid(True, alpha=0.3)
#             # グラフを画面に表示
#             st.pyplot(fig3, use_container_width=False)
#             plt.close(fig3)
        
#             # 年間の収支計算処理
#             income = filtered[filtered["種別"] == "収入"]["金額"].sum()
#             expense = filtered[filtered["種別"] == "支出"]["金額"].sum()
#             balance = income - expense
#             # 画面に結果を表示する
#             col1, col2, col3 = st.columns(3)
#             col1.metric("総収入", f"¥{income:,}")
#             col2.metric("総支出", f"¥{expense:,}")
#             col3.metric("収支", f"¥{balance:,}", delta = f"{balance:,}")
#             # カテゴリごとにデータをグループ分けして、金額を合計する
#             st.subheader("カテゴリ別内訳")
#             category_summary = filtered.groupby(["種別", "カテゴリ"])["金額"].sum().reset_index()
#             #category_summary["日付"] = category_summary["日付"].dt.strftime("%m/%d")
#             category_summary.columns = ["種別", "カテゴリ", "合計金額"]
#             category_summary["合計金額"] = category_summary["合計金額"].apply(lambda x: f"¥{x:,}")
#             category_summary.index = category_summary.index + 1
#             st.dataframe(category_summary, use_container_width=True)