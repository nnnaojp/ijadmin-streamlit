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

    st.sidebar.title("FXIJコンフィグツール")
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
    
    # Locate operation_manual.md
    # Try current directory first (root where streamlit run is executed)
    md_path = Path("operation_manual.md")
    if not md_path.exists():
        # Fallback to relative to this file
        md_path = Path(__file__).parent.parent.parent / "operation_manual.md"
    
    if not md_path.exists():
        st.error(f"Operation manual not found at {md_path.absolute()}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find and replace local images with base64
    # Pattern: ![alt text](path/to/image.png)
    # We assume paths are relative to the markdown file's directory
    md_dir = md_path.parent

    def replace_image(match):
        alt_text = match.group(1)
        img_rel_path = match.group(2)
        
        # Skip external links
        if img_rel_path.startswith("http") or img_rel_path.startswith("https"):
            return match.group(0)
            
        img_full_path = md_dir / img_rel_path
        
        if img_full_path.exists():
            ext = img_full_path.suffix.lower().replace(".", "")
            if ext == "jpg": ext = "jpeg"
            b64_str = get_base64_image(img_full_path)
            if b64_str:
                return f'<img src="data:image/{ext};base64,{b64_str}" alt="{alt_text}" style="max-width: 100%;">'
        
        return match.group(0)

    # Use regex to find images
    pattern = r'!\[(.*?)\]\((.*?)\)'
    content = re.sub(pattern, replace_image, content)

    st.markdown(content, unsafe_allow_html=True)

if __name__ == "__main__":
    render_help()
