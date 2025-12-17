import streamlit as st
from views import server_config, raid_config, update, log, reboot, server_info, log_search
from pathlib import Path
from utils.system_api import get_ip_address

VERSION="0.1.0"
st.set_page_config(page_title="FXIJコンフィグツール", layout="wide")

# Custom CSS to make disabled text areas look like normal text
st.markdown(
    """
    <style>
    /* Change disabled text area background and text color */
    # .stTextArea textarea:disabled {
    #     background-color: #ffffff; /* White background */
    #     color: #31333F; /* Default Streamlit text color */
    #     opacity: 1; /* Remove transparency */
    #     -webkit-text-fill-color: #31333F; /* For Safari/Chrome */
    # }
    # /* Dark mode support could be added here if needed, keeping it simple for now or assuming light mode or adapting colors */
    # @media (prefers-color-scheme: dark) {
    #     .stTextArea textarea:disabled {
    #         background-color: #0e1117; /* Dark background */
    #         color: #fafafa; /* Light text */
    #         -webkit-text-fill-color: #fafafa;
    #     }
    # }
    
    /* Enforce Japanese-friendly monospace font for code blocks */
    .stCodeBlock code {
        font-family: 'Menlo', 'Consolas', 'DejaVu Sans Mono', 'Noto Sans Mono CJK JP', 'MS Gothic', 'Meiryo', monospace !important;
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
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
logo_path = Path(__file__).parent / "assets/logo.jpg"
if logo_path.exists():
    st.sidebar.image(str(logo_path))

st.sidebar.write(f"IPアドレス： {get_ip_address()}")
st.sidebar.title("Menu")

page = st.sidebar.radio(
    "Go to", ["サーバー情報", "サーバー設定", "RAID設定", "アップデート", "ログ取得", "ログ検索", "再起動"]
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
elif page == "RAID設定":
    raid_config.show()
elif page == "アップデート":
    update.show()
elif page == "ログ取得":
    log.show()
elif page == "ログ検索":
    log_search.show()
elif page == "再起動":
    reboot.show()
