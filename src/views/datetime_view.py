import streamlit as st
import subprocess
import time
from datetime import datetime
from streamlit_javascript import st_javascript
from utils.config_manager import get_sudo_password
from utils.system_api import write_syslog

def show():
    write_syslog("starting datetime_view")
    st.title("サーバー時刻設定")
    st.write("サーバーの日時をブラウザのPCの日時に同期させます。")

    if "dt_view_key" not in st.session_state:
        st.session_state.dt_view_key = 0

    if "synced_time" not in st.session_state:
        st.session_state.synced_time = None

    if "sync_message" not in st.session_state:
        st.session_state.sync_message = None

    if st.session_state.sync_message:
        st.success(st.session_state.sync_message)
        st.session_state.sync_message = None

    # JavaScript to get client time in YYYY-MM-DD HH:MM:SS format
    js_code = """(function() {
        const d = new Date();
        const pad = (n) => n.toString().padStart(2, '0');
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`; 
   })();"""

    client_time_str = st_javascript(js_code, key=f"client_time_{st.session_state.dt_view_key}")
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.subheader("現在の日時")
    with col_h2:
        st.write("") # Spacer to align button somewhat
        if st.button("表示更新"):
            st.session_state.dt_view_key += 1
            st.session_state.synced_time = None
            st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.info("ブラウザ (Client)")
        if st.session_state.synced_time:
            st.write(f"**{st.session_state.synced_time}**")
        elif client_time_str and client_time_str != 0:
            st.write(f"**{client_time_str}**")

    # Get Server Time in same format
    if st.session_state.synced_time:
        server_time_str = st.session_state.synced_time
    else:
        try:
            server_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            server_time_str = f"取得エラー: {e}"

    with col2:
        st.success("サーバー (Server)")
        st.write(f"**{server_time_str}**")

    st.markdown("---")
    
    # st.subheader("時刻同期")
    # st.write("「ブラウザの日時」を「サーバー」に設定します。")
    
    if "processing_time_update" not in st.session_state:
        st.session_state.processing_time_update = False

    if st.button("サーバー時刻更新", key="btn_sync_time"):
        # Trigger update process: Force refresh client time first
        st.session_state.processing_time_update = True
        st.session_state.synced_time = None
        st.session_state.dt_view_key += 1
        st.rerun()

    if st.session_state.processing_time_update:
        if not client_time_str or client_time_str == 0:
            # Waiting for st_javascript to return fresh value (triggers rerun automatically)
            st.info("最新の時刻を取得中...")
        else:
            # We have fresh time, proceed with update
            password = get_sudo_password()
            if not password:
                st.error("設定ファイル(config.toml)にsudoパスワードが設定されていません。")
                st.session_state.processing_time_update = False
            else:
                try:
                    # Update server time using date -s "YYYY-MM-DD HH:MM:SS"
                    cmd = ["sudo", "-S", "date", "-s", client_time_str]
                    
                    res = subprocess.run(
                        cmd, 
                        input=password + "\n", 
                        capture_output=True, 
                        text=True, 
                        check=False
                    )
                    
                    if res.returncode == 0:
                        st.session_state.sync_message = f"サーバーの日時を更新しました ({client_time_str})"
                        st.session_state.synced_time = client_time_str
                        st.session_state.processing_time_update = False
                        st.rerun()
                    else:
                        write_syslog(f"Time sync failed! Result: {res.stderr}")
                        st.error(f"更新に失敗しました:\n{res.stderr}")
                        st.session_state.processing_time_update = False
                except Exception as e:
                    write_syslog(f"Time sync failed! Error: {e}")
                    st.error(f"実行エラー: {e}")
                    st.session_state.processing_time_update = False
