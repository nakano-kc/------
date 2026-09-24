import streamlit as st

if not st.session_state.get("authentication_status"):
    st.warning("先にログインページからログインしてください。")
    st.stop()
st.title("ページ1")
st.write("これはページ1のコンテンツです。")
name = st.session_state.get("name")
username = st.session_state.get("username")
roles = st.session_state.get("roles", [])
st.subheader("ログインユーザー情報")
st.write(f"名前: {name}")
st.write(f"ユーザー名: {username}")
st.write(f"権限: {roles}")
if st.button("ボタンを押す"):
    st.success("ボタンが押されました。")
