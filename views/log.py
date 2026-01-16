import streamlit as st
import subprocess
import os
import time
from utils.config_manager import get_sudo_password

def show():
    st.title("ログ取得")
    st.write("ログファイルをダウンロードします。")

    # Options
    option = st.radio("対象を選択", ["すべてのログファイル", "最新のログファイル"])
    
    # Sudo Password Input (Removed)
    
    # State to hold the generated file path
    if "generated_zip" not in st.session_state:
        st.session_state.generated_zip = None

    if st.button("アーカイブ作成"):
        password = get_sudo_password()
        if not password:
            st.error("設定ファイル(config.toml)にsudoパスワードが設定されていません。")
            return

        st.session_state.generated_zip = None # Reset previous
        
        target_path = ""
        output_zip = ""
        
        if option == "すべてのログファイル":
            target_path = "/var/mistral/log"
            output_zip = "/tmp/mistlog_all.zip"
            # zip -r for directory
            cmd = ["sudo", "-S", "zip", "-r", output_zip, target_path]
        else:
            # Latest log (assuming active file)
            target_path = "/var/mistral/log/mistlog.log"
            output_zip = "/tmp/mistlog_latest.zip"
            # zip for single file
            cmd = ["sudo", "-S", "zip", "-j", output_zip, target_path] # -j to verify path structure? just zip it.

        try:
            # Execute sudo command
            # input=password + "\n" izs crucial for sudo -S
            proc = subprocess.run(
                cmd, 
                input=password + "\n", 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if proc.returncode == 0:
                st.success(f"アーカイブを作成しました: {output_zip}")
                st.session_state.generated_zip = output_zip
            else:
                st.error("アーカイブ作成に失敗しました。")
                # Combine stdout and stderr to ensure we see the message
                error_details = f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}"
                st.code(error_details, language="text")
                # Common sudo error: "incorrect password" uses stderr
        except Exception as e:
            st.error(f"予期せぬエラーが発生しました: {e}")

    # Show download button if file is generated and exists
    if st.session_state.generated_zip and os.path.exists(st.session_state.generated_zip):
        with open(st.session_state.generated_zip, "rb") as f:
            st.download_button(
                label="ダウンロード",
                data=f,
                file_name=os.path.basename(st.session_state.generated_zip),
                mime="application/zip"
            )
