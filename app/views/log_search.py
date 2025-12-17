import streamlit as st
from utils.system_api import search_system_logs

def show():
    st.title("ログ検索")
    
    # Input fields
    query = st.text_input("検索ワード", placeholder="検索したい文字列を入力してください")
    password = st.text_input("sudoパスワード", value="ijadmin", type="password", help="ログファイルの読み取りにルート権限が必要です。")
    
    if st.button("検索"):
        if not query:
            st.warning("検索ワードを入力してください。")
            return
            
        if not password:
            st.warning("パスワードを入力してください。")
            return
            
        with st.spinner("検索中..."):
            result = search_system_logs(query, password)
            st.code(result)
