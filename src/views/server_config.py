import streamlit as st
from utils.config_manager import save_config, load_config
from utils.system_api import write_syslog, import_settings_package




def show():
    write_syslog("starting server_config")
    st.title("サーバー設定")
    st.write("サーバー設定の設定画面です。")

    # Current Settings
    st.subheader("現在の設定")
    current_config = load_config()
    st.code(str(current_config), language=None)

    # Head Configuration
    st.subheader("ヘッド構成")
    options = [
        "[0] 現在の構成",
        "[1] FXIJ type 500 (W:RC1536,40mpm)",
        "[2] FXIJ type 500 (W:RC1536x2,40mpm)",
        "[3] FXIJ type 500 (W:SambaG5Lx2,40mpm)",
        "[4] FXIJ type 1000 (W:RC1536,40mpm)",
        "[5] FXIJ type 1000 (W:RC1536x2,40mpm)",
        "[6] FXIJ type 1000 (W:SambaG5Lx2,30mpm)",
        "[7] FXIJ type 1000 (W:SambaG5Lx2,50mpm)",
    ]
    head_config = st.selectbox("ヘッド構成", options, index=0)
    
    # Capture the selected index in a variable as requested
    try:
        head_config_index = options.index(head_config)
    except ValueError:
        head_config_index = 0

    import json
    import os
    current_mistral_json = {}
    mistral_conf_path = "/usr/mistral/conf/mistral.json"
    if head_config_index == 0 and os.path.exists(mistral_conf_path):
        try:
            with open(mistral_conf_path, "r", encoding="utf-8") as f:
                current_mistral_json = json.load(f)
        except Exception as e:
            write_syslog(f"Failed to read mistral.json: {e}")

    # Print Direction
    default_print_direction = 0
    if head_config_index == 0 and "System" in current_mistral_json:
        try:
            pd = current_mistral_json["System"]["InkjetHead"][0]["PrintDirection"]
            if pd == 1:
                default_print_direction = 1
        except (KeyError, IndexError, TypeError):
            pass

    # Print Direction
    print_direction = st.radio("ヘッド印刷向き", ["正方向", "逆方向"], index=default_print_direction)

    req_servers_map = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3}
    if head_config_index == 0:
        if "System" in current_mistral_json and "nServer" in current_mistral_json["System"]:
            num_servers = current_mistral_json["System"]["nServer"]
        else:
            num_servers = 4
    else:
        num_servers = req_servers_map.get(head_config_index, 4)

    default_ips = ["192.168.151.100", "192.168.151.101", "192.168.151.102", "192.168.151.103"]
    if head_config_index == 0 and "Server" in current_mistral_json:
        servers = current_mistral_json["Server"]
        for i in range(min(4, len(servers))):
            if "IPAddress" in servers[i]:
                default_ips[i] = servers[i]["IPAddress"]

    # Server IP Addresses
    st.subheader("サーバーIPアドレス")
    col1, col2 = st.columns(2)
    with col1:
        ip1 = st.text_input("サーバー１のIPアドレス", value=default_ips[0], disabled=(num_servers < 1))
        ip3 = st.text_input("サーバー３のIPアドレス", value=default_ips[2], disabled=(num_servers < 3))
    with col2:
        ip2 = st.text_input("サーバー２のIPアドレス", value=default_ips[1], disabled=(num_servers < 2))
        ip4 = st.text_input("サーバー４のIPアドレス", value=default_ips[3], disabled=(num_servers < 4))

    # Buttons
    # Check for update result message from previous run
    if "update_msg" in st.session_state:
        msg_type, msg_text = st.session_state.update_msg
        if msg_type == "success":
            st.success(msg_text)
        else:
            st.error(msg_text)
        del st.session_state.update_msg

    if "confirm_update_config" not in st.session_state:
        st.session_state.confirm_update_config = False

    if st.button("設定を更新"):
        import ipaddress
        invalid_ips = []
        active_ips = [
            ("サーバー１", ip1, num_servers >= 1),
            ("サーバー２", ip2, num_servers >= 2),
            ("サーバー３", ip3, num_servers >= 3),
            ("サーバー４", ip4, num_servers >= 4)
        ]
        
        for name, ip, is_active in active_ips:
            if is_active:
                try:
                    ipaddress.ip_address(ip)
                except ValueError:
                    invalid_ips.append(name)
        
        if invalid_ips:
            st.error(f"IPアドレスのフォーマットが不正です: {', '.join(invalid_ips)}")
        else:
            st.session_state.confirm_update_config = True
            st.session_state.pending_config_data = {
                "head_config": head_config,
                "print_direction": print_direction,
                "ips": [ip1, ip2, ip3, ip4]
            }
            st.session_state.pending_head_config_index = head_config_index - 1

    if st.session_state.confirm_update_config:
        st.warning("設定を更新しますか？")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("はい", key="confirm_update_yes"):
                config_data = st.session_state.pending_config_data
                h_index = st.session_state.pending_head_config_index
                try:
                    if save_config(config_data, h_index):
                        st.session_state.update_msg = ("success", f"設定を更新しました (ヘッド構成: {config_data['head_config']})")
                    else:
                        st.session_state.update_msg = ("error", "設定の更新に失敗しました")
                except Exception as e:
                    write_syslog(f"Config update failed! Error: {e}")
                    st.session_state.update_msg = ("error", f"実行時エラーが発生しました: {e}")
                
                st.session_state.confirm_update_config = False
                st.rerun()
        with col_no:
            if st.button("いいえ", key="confirm_update_no"):
                st.session_state.confirm_update_config = False
                st.rerun()

    if "show_import_uploader" not in st.session_state:
        st.session_state.show_import_uploader = False

    if st.button("設定をインポート"):
        st.session_state.show_import_uploader = not st.session_state.show_import_uploader

    if st.session_state.show_import_uploader:
        uploaded_file = st.file_uploader("設定ファイル(tgz)を選択してください", type="tgz")
        if uploaded_file is not None:
             # Save to /tmp
            import os
            import tempfile
            _, ext = os.path.splitext(uploaded_file.name)
            with tempfile.NamedTemporaryFile(dir="/tmp", suffix=ext, prefix="upload_", delete=False) as tf:
                tf.write(uploaded_file.getbuffer())
                temp_path = tf.name

            with st.spinner("設定をインポート中..."):
                result = import_settings_package(temp_path)
            
            if result == "Success":
                st.success("設定のインポートが完了しました。")
                st.session_state.show_import_uploader = False
                # Ideally refresh the page or config to show new values
            else:
                st.error(f"設定のインポートに失敗しました:\n{result}")
