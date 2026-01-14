import streamlit as st
from utils.system_api import reboot_system


def show():
    st.title("再起動")
    st.write("システム再起動画面です。")
    if st.button("再起動を実行"):
        st.warning("本当に再起動しますか？ (デモ機能)")
        # In a real scenario, you might want a confirmation dialog or logic here
        # result = reboot_system()
        # st.info(result)
