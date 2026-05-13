import streamlit as st
import subprocess
import os
import time
from utils.config_manager import get_sudo_password
from utils.system_api import get_ip_address, write_syslog

def show():
    write_syslog("starting log")
    st.title("ログ取得")
    st.write("ログファイルをダウンロードします。")
    
    if "log_archive_path" not in st.session_state:
        st.session_state.log_archive_path = None

    if st.session_state.log_archive_path is None:
        if st.button("ダウンロード", type="primary"):
            print("archiving...")
            with st.spinner("内部でアーカイブを作成しています..."):
                password = get_sudo_password()
                if not password:
                    st.error("設定ファイル(config.toml)にsudoパスワードが設定されていません。")
                    return

                ip_addr = get_ip_address()
                if not ip_addr or "Unknown" in ip_addr:
                     ip_addr = "server"
                
                output_zip = f"/tmp/mistlog-{ip_addr}.zip"
                zip_command_str = f"zip -j {output_zip} /var/mistral/log/mistlog*"
                cmd = ["sudo", "-S", "sh", "-c", zip_command_str]

                try:
                    proc = subprocess.run(
                        cmd, 
                        input=password + "\n", 
                        capture_output=True, 
                        text=True, 
                        check=False
                    )
                    
                    if proc.returncode == 0:
                        st.session_state.log_archive_path = output_zip
                        if hasattr(st, "rerun"):
                            st.rerun()
                        else:
                            st.experimental_rerun()
                    else:
                        write_syslog(f"Log Archive failed! Result: {proc.stderr}")
                        st.error("アーカイブ作成に失敗しました。")
                        error_details = f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}"
                        st.code(error_details, language="text")
                        return
                except Exception as e:
                    write_syslog(f"Log Archive failed! Error: {e}")
                    st.error(f"予期せぬエラーが発生しました: {e}")
                    return
    else:
        # Show download button if file is generated and exists
        st.success("アーカイブの準備が完了しました。")
        with open(st.session_state.log_archive_path, "rb") as f:
            st.download_button(
                label="ファイルを保存",
                data=f,
                file_name=os.path.basename(st.session_state.log_archive_path),
                mime="application/zip",
                type="primary"
            )
            st.session_state.log_archive_path = None
        if st.button("戻る", type="secondary"):
            st.session_state.log_archive_path = None
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.experimental_rerun()
