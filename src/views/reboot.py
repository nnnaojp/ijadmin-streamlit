import streamlit as st
from utils.system_api import reboot_system, shutdown_system, execute_sudo_command, write_syslog
import time

@st.dialog("再起動の確認")
def confirm_reboot_dialog():
    st.warning("本当にシステムを再起動しますか？")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("はい", key="btn_reboot_yes"):
            with st.spinner("再起動を実行中..."):
                try:
                    result = reboot_system()
                    if result == "Success":
                        st.success("再起動コマンドを送信しました。")
                        time.sleep(3)
                        st.rerun()
                    else:
                        write_syslog(f"Reboot failed! Result: {result}")
                        st.error(result)
                except Exception as e:
                    write_syslog(f"Reboot failed! Error: {e}")
                    st.error(f"実行時エラーが発生しました: {e}")
    with col_no:
        if st.button("いいえ", key="btn_reboot_no"):
            st.rerun()

@st.dialog("シャットダウンの確認")
def confirm_shutdown_dialog():
    st.warning("本当にシステムをシャットダウンしますか？")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("はい", key="btn_shutdown_yes"):
            with st.spinner("シャットダウンを実行中..."):
                try:
                    result = shutdown_system()
                    if result == "Success":
                        st.success("シャットダウンコマンドを送信しました。")
                        time.sleep(3)
                        st.rerun()
                    else:
                        write_syslog(f"Shutdown failed! Result: {result}")
                        st.error(result)
                except Exception as e:
                    write_syslog(f"Shutdown failed! Error: {e}")
                    st.error(f"実行時エラーが発生しました: {e}")
    with col_no:
        if st.button("いいえ", key="btn_shutdown_no"):
            st.rerun()

@st.dialog("モジュール再起動の確認")
def confirm_module_restart_dialog():
    st.warning("本当にモジュールを再起動しますか？")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("はい", key="btn_module_restart_yes"):
            with st.spinner("モジュールを再起動中..."):
                try:
                    result = execute_sudo_command(["/usr/mistral/bin/restart.sh"])
                    if result == "Success":
                        st.success("モジュール再起動コマンドを送信しました。")
                        time.sleep(3)
                        st.rerun()
                    else:
                        write_syslog(f"Module restart failed! Result: {result}")
                        st.error(result)
                except Exception as e:
                    write_syslog(f"Module restart failed! Error: {e}")
                    st.error(f"実行時エラーが発生しました: {e}")
    with col_no:
        if st.button("いいえ", key="btn_module_restart_no"):
            st.rerun()

def show():
    write_syslog("starting reboot")
    st.title("再起動/シャットダウン")
    st.write("サーバーの再起動/シャットダウン、およびモジュール再起動を実行します。")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("再起動を実行", type="primary", use_container_width=True):
            confirm_reboot_dialog()
            
    with col2:
        if st.button("シャットダウンを実行", type="primary", use_container_width=True):
            confirm_shutdown_dialog()

    col3, col4 = st.columns(2)
    with col3:
        if st.button("モジュール再起動", type="primary", use_container_width=True):
            confirm_module_restart_dialog()
