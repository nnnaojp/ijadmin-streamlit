import streamlit as st
from utils.config_manager import save_config, load_config


def show():
    st.title("サーバー設定")
    st.write("サーバー設定の設定画面です。")

    # Current Settings
    st.subheader("現在の設定")
    current_config = load_config()
    st.code(str(current_config), language=None)

    # Head Configuration
    st.subheader("ヘッド構成")
    head_config = st.selectbox("ヘッド構成", 
        ["[1] FXIJ type 500 (W:RC1536,40mpm)",
         "[2] FXIJ type 500 (W:RC1536x2,40mpm)",
         "[3] FXIJ type 1000 (W:RC1536,40mpm)",
         "[4] FXIJ type 1000 (W:RC1536,40mpm)",
         "[5] FXIJ type 1000 (W:RC1536,40mpm)",
         "[6] FXIJ type 1000 (W:RC1536,40mpm)",
         "[7] FXIJ type 1000 (W:RC1536,40mpm)",
         ], index=0)

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

    # Save Button
    if st.button("設定を保存"):
        config_data = {
            "head_config": head_config,
            "print_direction": print_direction,
            "ips": [ip1, ip2, ip3, ip4]
        }
        if save_config(config_data):
            st.success(f"設定を保存しました (ヘッド構成: {head_config})")
        else:
            st.error("設定の保存に失敗しました")
