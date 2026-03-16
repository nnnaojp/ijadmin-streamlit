import os
import streamlit as st
from utils.system_api import write_syslog

def show():
    write_syslog("starting update")
    st.title("アップデート")
    st.write("システムアップデート画面です。")
    
    uploaded_file = st.file_uploader("アップデートファイルを選択してください", type=None)
    
    if st.button("アップデート"):
        if uploaded_file is not None:
            try:
                # Define target path (saving to /tmp)
                file_path = os.path.join("/tmp", uploaded_file.name)
                
                # Write file to /tmp
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"ファイルをコピーしました: {file_path}")
            except Exception as e:
                st.error(f"ファイルのコピー中にエラーが発生しました: {e}")
        else:
            st.error("ファイルが選択されていません。")
