import streamlit as st
from utils.config_manager import save_config, load_config
from utils.system_api import write_syslog, import_settings_package

@st.dialog("設定更新の確認")
def confirm_update_dialog(config_data, head_config_index):
    write_syslog("xxx")
    # st.write(config_data, head_config_index)
    st.write("設定を更新しますか？")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("はい"):
            if save_config(config_data,head_config_index):
                st.session_state.update_msg = ("success", f"設定を更新しました (ヘッド構成: {config_data['head_config']})")
            else:
                st.session_state.update_msg = ("error", "設定の更新に失敗しました")
            st.rerun()
    with col_no:
        if st.button("いいえ"):
            st.rerun()


def show():
    write_syslog("starting server_config")
    st.title("サーバー設定")
    st.write("サーバー設定の設定画面です。")

    # Current Settings
    st.subheader("現在の設定")
    current_config = load_config()
    st.code(str(current_config), language=None)

    # Head Configuration
    # Head Configuration
    st.subheader("ヘッド構成")
    options = [
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

    # Print Direction
    print_direction = st.radio("ヘッド印刷向き", ["正方向", "逆方向"])

    # Server IP Addresses
    st.subheader("サーバーIPアドレス")
    col1, col2 = st.columns(2)
    with col1:
        ip1 = st.text_input("サーバー１のIPアドレス", value="192.168.151.100")
        ip3 = st.text_input("サーバー３のIPアドレス", value="192.168.151.102")
    with col2:
        ip2 = st.text_input("サーバー２のIPアドレス", value="192.168.151.101")
        ip4 = st.text_input("サーバー４のIPアドレス", value="192.168.151.103")

    # Buttons
    # Check for update result message from previous run
    if "update_msg" in st.session_state:
        msg_type, msg_text = st.session_state.update_msg
        if msg_type == "success":
            st.success(msg_text)
        else:
            st.error(msg_text)
        del st.session_state.update_msg

    if st.button("設定を更新"):
        config_data = {
            "head_config": head_config,
            "print_direction": print_direction,
            "ips": [ip1, ip2, ip3, ip4]
        }
        confirm_update_dialog(config_data, head_config_index)

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
