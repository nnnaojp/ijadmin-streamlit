import streamlit as st
from PIL import Image
import os
import re
import base64
from pathlib import Path
from utils.system_api import get_ip_address

_favicon = Image.open(Path(__file__).parent.parent.parent / "assets/favicon.ico")
st.set_page_config(page_title="FXIJコンフィグツール ヘルプ", layout="wide", page_icon=_favicon)

def get_base64_image(image_path):
    """Encodes an image to a base64 string."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image {image_path}: {e}")
        return None

def render_help():
    # CSS for sidebar layout (same as main.py)
    st.markdown(
        """
        <style>
        /* Hide default sidebar navigation */
        [data-testid="stSidebarNav"] {
            display: none;
        }

        [data-testid="stSidebar"] > div:nth-child(1) {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Match Main page titles */
        h1 { font-size: 2.0rem; }
        h2 { font-size: 1.5rem; }

        /* Make manual text smaller */
        .stMarkdown p, .stMarkdown li {
            font-size: 0.85rem !important;
        }
        .stMarkdown h2 {
            font-size: 1.3rem !important;
            padding-bottom: 0.2rem;
            margin-bottom: 0.5rem;
        }
        .stMarkdown h3 {
            font-size: 1.1rem !important;
            margin-bottom: 0.3rem;
            margin-top: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Logo and Info
    logo_path = Path(__file__).parent.parent.parent / "assets/logo.jpg"
    if logo_path.exists():
        st.sidebar.image(str(logo_path))

    # st.sidebar.title("FXIJコンフィグツール")
    # st.sidebar.write("Version 0.01.00")
    st.sidebar.write(f"IPアドレス： {get_ip_address()}")

    # Spacer and Navigation at bottom
    st.sidebar.markdown('<div style="margin-top: auto;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    nav = st.sidebar.radio("Navigation", ["Main", "Help"], index=1, label_visibility="collapsed", key="nav_help")
    if nav == "Main":
        st.switch_page("main.py")

    st.sidebar.caption("Version: 0.0.1")

    #st.title("操作ヘルプ")
    
    # Locate Markdown manual
    md_path = Path(__file__).parent.parent.parent / "assets/manual.md"
    
    if not md_path.exists():
        st.error(f"マニュアルファイルが見つかりません: {md_path.absolute()}")
        return

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Display Markdown
        st.markdown(md_content)
    except Exception as e:
        st.error(f"マニュアル読み込みエラー: {e}")

if __name__ == "__main__":
    render_help()
