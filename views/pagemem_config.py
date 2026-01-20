import streamlit as st
from utils.config_manager import get_mistral_cma_size, update_mistral_cma_config
from utils.system_api import get_server_total_memory_gb, execute_sudo_command

def show():
    st.title("印刷ページメモリ調整")
    st.write("印刷ページメモリを調整します。")
    st.subheader("現在のページメモリ")
    cma_mem = get_mistral_cma_size()
    server_mem = get_server_total_memory_gb()
    
    st.write(f"- サーバーメモリ:  {server_mem} GB")
    st.write(f"- 印刷ページメモリ:  {cma_mem} GB")
        
    st.write("") # Spacer
    
    if st.button("印刷ページメモリ調整"):
        # Update GRUB Config CMA size
        res_config_update = update_mistral_cma_config(server_mem)
        if res_config_update != "Success":
             st.error(f"/etc/default/grubの更新に失敗しました: {res_config_update}")
        else:
            # Remount /boot RW
            res_mount_rw = execute_sudo_command(["mount", "-o", "rw,remount", "/boot"])
            if res_mount_rw != "Success":
                st.error(f"/bootのリマウント(rw)に失敗しました: {res_mount_rw}")
            else:
                # Update Grub
                res_update = execute_sudo_command(["update-grub"])
                
                # Remount /boot RO (Always try to remount RO if RW was successful)
                res_mount_ro = execute_sudo_command(["mount", "-o", "ro,remount", "/boot"])
    
                if res_update == "Success":
                    if res_mount_ro == "Success":
                        st.success("印刷ページメモリを調整しました (update-grubを実行しました)")
                    else:
                        st.warning(f"update-grubは成功しましたが、/bootのリマウント(ro)に失敗しました: {res_mount_ro}")
                else:
                    st.error(f"update-grubの実行に失敗しました: {res_update}")
                    if res_mount_ro != "Success":
                        st.error(f"さらに、/bootのリマウント(ro)にも失敗しました: {res_mount_ro}")
