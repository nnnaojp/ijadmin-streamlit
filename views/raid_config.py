import streamlit as st
from utils.system_api import get_disk_info, init_raid_sequence, unmount_raid_volume, mount_raid_volume, write_syslog

def show():
    write_syslog("starting raid_config")
    st.title("RAID設定")
    st.write("RAID設定画面です。")
    # Placeholder for RAID Settings logic
    st.subheader("RAIDディスク")
    disk_info_placeholder = st.empty()
    disk_info_placeholder.code(get_disk_info(exclude_patterns=["sda"]), language=None)

    st.write("") # Spacer
    
    if st.button("マウント解除"):
        try:
            result = unmount_raid_volume()
            if result == "Success":
                st.success("マウントを解除しました。")
                # Refresh disk info
                disk_info_placeholder.code(get_disk_info(exclude_patterns=["sda"]), language=None)
            else:
                write_syslog(f"Unmount failed! Result: {result}")
                st.error(f"マウント解除に失敗しました:\n{result}")
        except Exception as e:
            write_syslog(f"Unmount failed! Error: {e}")
            st.error(f"実行時エラーが発生しました: {e}")

    st.write("") # Spacer

    if st.button("マウント実行"):
        try:
            result = mount_raid_volume()
            if result == "Success":
                st.success("マウントしました。")
                # Refresh disk info
                disk_info_placeholder.code(get_disk_info(exclude_patterns=["sda"]), language=None)
            else:
                write_syslog(f"Mount failed! Result: {result}")
                st.error(f"マウントに失敗しました:\n{result}")
        except Exception as e:
            write_syslog(f"Mount failed! Error: {e}")
            st.error(f"実行時エラーが発生しました: {e}")

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
            
            # Current processing state
            is_processing = st.session_state.get("raid_initializing", False)

            with col1:
                # Execution Button with state handling
                def on_click_execute():
                    st.session_state.raid_initializing = True
                
                # If processing, disable the button. Logic runs below.
                if st.button("実行", type="primary", key="raid_init_exec", disabled=is_processing, on_click=on_click_execute):
                    pass # Triggered by callback

            with col2:
                def on_click_cancel():
                    st.session_state.show_raid_confirm = False
                st.button("キャンセル", disabled=is_processing, on_click=on_click_cancel)
            
            # Logic Execution
            if is_processing:
                with st.spinner("RAID初期化を実行中..."):
                    # Force a small sleep or yield if needed for UI update? Streamlit usually handles this.
                    try:
                        result = init_raid_sequence()
                    
                        st.session_state.raid_initializing = False
                        
                        if result == "Success":
                            is_success = True
                            # Update disk info
                            disk_info_placeholder.code(get_disk_info(exclude_patterns=["sda"]), language=None)
                            st.session_state.show_raid_confirm = False
                        else:
                            write_syslog(f"RAID Init failed! Result: {result}")
                            msg_container.error(f"RAID初期化に失敗しました:\n{result}")
                    except Exception as e:
                        st.session_state.raid_initializing = False
                        write_syslog(f"RAID Init failed! Error: {e}")
                        msg_container.error(f"実行時エラーが発生しました: {e}")

        # Clear container and show success message if successful
        if is_success:
            confirm_container.empty()
            st.success("RAID初期化が完了しました。")
