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
    
    # State to hold the generated file path
    if "generated_zip" not in st.session_state:
        st.session_state.generated_zip = None

    if st.button("アーカイブ作成"):
        password = get_sudo_password()
        if not password:
            st.error("設定ファイル(config.toml)にsudoパスワードが設定されていません。")
            return

        st.session_state.generated_zip = None # Reset previous
        
        target_path = "/var/mistral/log"
        
        # Determine output filename based on IP
        ip_addr = get_ip_address()
        # Clean up IP string if needed or fallback
        if not ip_addr or "Unknown" in ip_addr:
             ip_addr = "server"
        
        output_zip = f"/tmp/mistlog-{ip_addr}.zip"
        
        # zip specific files matching /var/mistral/log/mistlog*
        # We need to construct the command carefully for shell glob expansion
        # Using `sh -c` to allow globbing of the input files
        zip_command_str = f"zip -j {output_zip} /var/mistral/log/mistlog*"
        cmd = ["sudo", "-S", "sh", "-c", zip_command_str]

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
                write_syslog(f"Log Archive failed! Result: {proc.stderr}")
                st.error("アーカイブ作成に失敗しました。")
                # Combine stdout and stderr to ensure we see the message
                error_details = f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}"
                st.code(error_details, language="text")
                # Common sudo error: "incorrect password" uses stderr
        except Exception as e:
            write_syslog(f"Log Archive failed! Error: {e}")
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
