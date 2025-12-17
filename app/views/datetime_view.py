import streamlit as st
import subprocess

def show():
    st.title("日時表示")
    st.write("サーバーの現在日時を表示します。")

    if st.button("更新"):
        # Just reruns the script, updating the date
        pass

    try:
        # Execute the 'date' command
        result = subprocess.run(["date"], capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            current_date = result.stdout.strip()
            # Use st.code to provide a copy button on the top right
            st.code(current_date, language="text")
        else:
            st.error(f"日時の取得に失敗しました: {result.stderr}")
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
