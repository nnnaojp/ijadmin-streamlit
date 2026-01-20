import streamlit as st
from utils.system_api import get_disk_info, init_raid_sequence

def show():
    st.title("RAID設定")
    st.write("RAID設定画面です。")
    # Placeholder for RAID Settings logic
    st.subheader("RAIDディスク")
    disk_info_placeholder = st.empty()
    disk_info_placeholder.code(get_disk_info(exclude_patterns=["sda"]), language=None)

    st.write("") # Spacer
    if st.button("RAID初期化"):
        st.session_state.show_raid_confirm = True

    if st.session_state.get("show_raid_confirm", False):
        confirm_container = st.empty()
        
        # Variable to track success state for UI clearing
        is_success = False

        with confirm_container.container():
            st.warning("RAID初期化を実行しますか？\nディスクの内容はすべて消去されます。")
            col1, col2 = st.columns([1, 5])
            
            # Placeholder for error messages (full width)
            msg_container = st.empty()

            with col1:
                if st.button("実行", type="primary", key="raid_init_exec"):
                    result = init_raid_sequence()
                    if result == "Success":
                        # Set success flag
                        is_success = True
                        
                        # Refresh disk info
                        disk_info_placeholder.code(get_disk_info(exclude_patterns=["sda"]), language=None)
                        st.session_state.show_raid_confirm = False
                    else:
                        msg_container.error(f"RAID初期化に失敗しました:\n{result}")
            with col2:
                if st.button("キャンセル"):
                    st.session_state.show_raid_confirm = False
                    st.rerun()
        
        # Clear container and show success message if successful
        if is_success:
            confirm_container.empty()
            st.success("RAID初期化が完了しました。")
