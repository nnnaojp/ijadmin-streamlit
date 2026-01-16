import streamlit as st
import subprocess
import time
from streamlit_javascript import st_javascript
from utils.config_manager import get_sudo_password

def show():
    st.title("サーバー時刻設定")
    st.write("サーバーの日時をブラウザのPCの日時に同期させます。")

    if "dt_view_key" not in st.session_state:
        st.session_state.dt_view_key = 0

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
            st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.info("ブラウザ (Client)")
        if client_time_str and client_time_str != 0:
            st.write(f"**{client_time_str}**")
        else:
            st.warning("時刻を取得中... (ロード完了までお待ちください)")

    # Get Server Time in same format
    server_time_str = "Unknown"
    try:
        # Use date command with specific format
        res = subprocess.run(["env", "LC_ALL=C", "date", "+%Y-%m-%d %H:%M:%S"], capture_output=True, text=True)
        if res.returncode == 0:
            server_time_str = res.stdout.strip()
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
                        st.success(f"サーバーの日時を更新しました ({client_time_str})")
                        st.session_state.processing_time_update = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"更新に失敗しました:\n{res.stderr}")
                        st.session_state.processing_time_update = False
                except Exception as e:
                    st.error(f"実行エラー: {e}")
                    st.session_state.processing_time_update = False
