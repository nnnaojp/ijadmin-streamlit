import streamlit as st
from PIL import Image
from views import server_config, raid_config, update, log, reboot, server_info, log_search, datetime_view, pagemem_config
from pathlib import Path
from utils.system_api import get_ip_address, write_syslog, execute_sudo_command

VERSION="0.0.1"
_favicon = Image.open(Path(__file__).parent / "assets/favicon.ico")
st.set_page_config(page_title="FXIJコンフィグツール", layout="wide", page_icon=_favicon)

# Custom CSS to make disabled text areas look like normal text
st.markdown(
    """
    <style>
    /* Enforce Japanese-friendly monospace font for code blocks */
    .stCodeBlock code {
        font-family: 'Menlo', 'Consolas', 'DejaVu Sans Mono', 'Noto Sans Mono CJK JP', 'MS Gothic', 'Meiryo', monospace !important;
    }

    /* Hide copy button in st.code - Multiple strategies */
    div[data-testid="stCodeBlock"] > div:first-child {
        display: none;
    }
    
    /* Hide default sidebar navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Make sidebar a flex container to push items to bottom */
    [data-testid="stSidebar"] > div:nth-child(1) {
        height: 100vh;
        display: flex;
        flex-direction: column;
    }

    /* st.title() は h1、st.subheader() は h2 になることが多い */
    h1 { font-size: 2.0rem; }  /* ここを好みで微調整 */
    h2 { font-size: 1.5rem; }  /* ここを好みで微調整 */
    </style>
    """,
    unsafe_allow_html=True
)

from utils.config_manager import get_admin_password

# Login Screen
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("管理者ログイン")
    with st.form("login_form"):
        password = st.text_input("パスワードを入力してください", type="password", max_chars=16)
        submitted = st.form_submit_button("ログイン")
    if submitted:
        if password == get_admin_password():
            st.session_state.authenticated = True
            # execute_sudo_command(["killall", "splmd", "splwd", "dcmd", "sg3sd"])
            execute_sudo_command(["killall", "dcmd", "sg3sd"])
            st.rerun()
        else:
            st.error("パスワードが正しくありません")
            
    st.markdown("※コンフィグツールにログインするとMistralサービスは一旦停止されます。<br>※作業終了後に再起動メニューからモジュール再起動を実行してください。", unsafe_allow_html=True)
    st.stop()  # Stop rendering the rest of the app until authenticated

# Sidebar Navigation
logo_path = Path(__file__).parent / "assets/logo.jpg"
if logo_path.exists():
    st.sidebar.image(str(logo_path))

st.sidebar.write(f"IPアドレス： {get_ip_address()}")
st.sidebar.title("Menu")

page = st.sidebar.radio(
    "Go to", ["サーバー情報", "サーバー設定", "サーバー時刻設定", "RAID設定", 
    "ログ取得", "ログ検索", "印刷ページメモリ調整", "ソフトウェアアップデート",  "再起動/シャットダウン"]
)

# Spacer to push content to bottom
st.sidebar.markdown('<div style="margin-top: auto;"></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", ["Main", "Help"], index=0, label_visibility="collapsed", key="nav_main")
if nav == "Help":
    st.switch_page("pages/help.py")

st.sidebar.caption(f"Version: {VERSION}")

# Page Routing
if page == "サーバー情報":
    server_info.show()
elif page == "サーバー設定":
    server_config.show()
elif page == "サーバー時刻設定":
    datetime_view.show()
elif page == "RAID設定":
    raid_config.show()
elif page == "ログ取得":
    log.show()
elif page == "ログ検索":
    log_search.show()
elif page == "印刷ページメモリ調整":
    pagemem_config.show()
elif page == "ソフトウェアアップデート":
    update.show()
elif page == "再起動/シャットダウン":
    reboot.show()
