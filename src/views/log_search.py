import streamlit as st
from utils.system_api import search_system_logs, write_syslog
from utils.config_manager import get_sudo_password

def show():
    write_syslog("starting log_search")
    st.title("ログ検索")
    
    # Input fields
    with st.form(key="search_form"):
        query = st.text_input("検索ワード", placeholder="検索したい文字列を入力してください (スペース区切り: AND, |区切り: OR)")
        # password = st.text_input("sudoパスワード", value="ijadmin", type="password", help="ログファイルの読み取りにルート権限が必要です。")
        submitted = st.form_submit_button("検索")
    
    if submitted:
        if not query:
            st.warning("検索ワードを入力してください。")
            return
            
        password = get_sudo_password()
        if not password:
            st.warning("設定ファイル(config.toml)にsudoパスワードが設定されていません。")
            return
            
        with st.spinner("検索中..."):
            result = search_system_logs(query, password)
            st.text_area("検索結果", result, height=600)
