import streamlit as st
import os
import re
import base64
from pathlib import Path
from utils.system_api import get_ip_address

st.set_page_config(page_title="FXIJコンフィグツール ヘルプ", layout="wide")

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
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Logo and Info
    logo_path = Path(__file__).parent.parent / "assets/logo.jpg"
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

    st.sidebar.caption("Version: 0.1.0")

    st.title("操作マニュアル")
    
    # Locate PDF
    pdf_path = Path(__file__).parent.parent / "fxij_configtool_r2.pdf"
    
    if not pdf_path.exists():
        st.error(f"PDF manual not found at {pdf_path.absolute()}")
        return

    try:
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        # Embed PDF
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading PDF: {e}")

if __name__ == "__main__":
    render_help()
