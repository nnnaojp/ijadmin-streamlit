import streamlit as st
from utils.system_api import search_system_logs, get_all_system_logs, write_syslog
from utils.config_manager import get_sudo_password

def show():
    write_syslog("starting log_search")
    st.title("ログ検索")
    
    # Input fields
    with st.form(key="search_form"):
        query = st.text_input("検索ワード", placeholder="検索したい文字列を入力してください (スペース区切り: AND, |区切り: OR)　※空白のまま検索するとログ全体を表示します")
        # password = st.text_input("sudoパスワード", value="ijadmin", type="password", help="ログファイルの読み取りにルート権限が必要です。")
        submitted = st.form_submit_button("検索")
    
    if submitted:
        password = get_sudo_password()
        if not password:
            st.warning("設定ファイル(config.toml)にsudoパスワードが設定されていません。")
            return

        if not query:
            # 検索ワードなし → ログ全体を表示（10MB超の場合は末尾10MBのみ）
            with st.spinner("ログ全体を取得中..."):
                result, truncated = get_all_system_logs(password)
                if truncated:
                    st.info("ログサイズが10MBを超えるため、最近の10MB分のみ表示しています。")
                st.text_area("ログ全体", result, height=600)
        else:
            with st.spinner("検索中..."):
                result = search_system_logs(query, password)
                st.text_area("検索結果", result, height=600)
