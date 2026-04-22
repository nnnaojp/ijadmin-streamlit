import streamlit as st
from utils.config_manager import get_mistral_cma_size, update_mistral_cma_config
from utils.system_api import get_server_total_memory_gb, execute_sudo_command, write_syslog

def show():
    write_syslog("starting pagemem_config")
    st.title("印刷ページメモリ調整")
    st.write("印刷ページメモリを調整します。")
    st.subheader("現在のページメモリ")
    
    mem_info_placeholder = st.empty()
    
    # We need server_mem available for the update function later
    server_mem = get_server_total_memory_gb()

    def render_mem_info():
        cma_mem = get_mistral_cma_size()
        # We can reuse the outer server_mem or fetch again. 
        # Using outer variable is fine if it doesn't change.
        with mem_info_placeholder.container():
            st.write(f"- サーバーメモリ:  {server_mem} GB")
            st.write(f"- 印刷ページメモリ:  {cma_mem} GB")
            
    render_mem_info()
        
    st.write("") # Spacer
    
    if st.button("印刷ページメモリ調整"):
        st.session_state.show_pagemem_confirm = True

    if st.session_state.get("show_pagemem_confirm", False):
        confirm_container = st.empty()
        # Variable to track success state for UI clearing
        is_success = False

        with confirm_container.container():
            st.warning("印刷ページメモリ調整を実行しますか？")
            col1, col2 = st.columns([1, 5])
            
            # Placeholder for error messages (full width)
            msg_container = st.empty()
            
            # Current processing state
            is_processing = st.session_state.get("pagemem_initializing", False)
            
            with col1:
                 # Execution Button with state handling
                def on_click_execute():
                    st.session_state.pagemem_initializing = True
                
                # If processing, disable the button.
                if st.button("実行", type="primary", key="pagemem_exec", disabled=is_processing, on_click=on_click_execute):
                     pass
            
            with col2:
                def on_click_cancel():
                    st.session_state.show_pagemem_confirm = False
                st.button("キャンセル", disabled=is_processing, on_click=on_click_cancel)

            # Logic Execution
            if is_processing:
                with st.spinner("設定を更新中..."):
                    try:
                        # Update GRUB Config CMA size
                        res_config_update = update_mistral_cma_config(server_mem)
                        
                        final_result = "Failure"
                        error_msg = ""

                        if res_config_update != "Success":
                             error_msg = f"/etc/default/grubの更新に失敗しました: {res_config_update}"
                        else:
                            # Remount /boot RW
                            res_mount_rw = execute_sudo_command(["mount", "-o", "rw,remount", "/boot"])
                            if res_mount_rw != "Success":
                                error_msg = f"/bootのリマウント(rw)に失敗しました: {res_mount_rw}"
                            else:
                                # Update Grub
                                res_update = execute_sudo_command(["update-grub"])
                                
                                # Remount /boot RO (Always try to remount RO if RW was successful)
                                res_mount_ro = execute_sudo_command(["mount", "-o", "ro,remount", "/boot"])
                
                                if res_update == "Success":
                                    if res_mount_ro == "Success":
                                        final_result = "Success"
                                    else:
                                        # Success but with warning on RO remount
                                        final_result = "Warning"
                                        error_msg = f"update-grubは成功しましたが、/bootのリマウント(ro)に失敗しました: {res_mount_ro}"
                                else:
                                    error_msg = f"update-grubの実行に失敗しました: {res_update}"
                                    if res_mount_ro != "Success":
                                        error_msg += f"\nさらに、/bootのリマウント(ro)にも失敗しました: {res_mount_ro}"
                    except Exception as e:
                        final_result = "Exception"
                        error_msg = f"実行時エラーが発生しました: {e}"
                    
                    st.session_state.pagemem_initializing = False

                    if final_result == "Success":
                        is_success = True
                        st.session_state.show_pagemem_confirm = False
                    elif final_result == "Warning":
                        # Treated somewhat like success but showing warning. 
                        # User didn't specify warning behavior, but let's clear dialog and show warning.
                        is_success = True 
                        st.session_state.show_pagemem_confirm = False
                        # We will output warning below but let's treat "action completed" as success.
                    else:
                        write_syslog(f"Page Memory Config failed! Error: {error_msg}")
                        msg_container.error(f"実行に失敗しました:\n{error_msg}")

        # Clear container and show success/warning message if successful
        if is_success:
            confirm_container.empty()
            if final_result == "Success":
                st.success("印刷ページメモリを調整しました")
                render_mem_info()
            elif final_result == "Warning":
                 st.warning(error_msg)
                 render_mem_info()
