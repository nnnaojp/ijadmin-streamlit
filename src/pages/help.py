import streamlit as st
from PIL import Image
import os
import re
import base64
from pathlib import Path
from utils.system_api import get_ip_address

_favicon = Image.open(Path(__file__).parent.parent / "assets/favicon.ico")
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

    st.sidebar.caption("Version: 0.1.00")

    #st.title("操作ヘルプ")
    
    # Locate Markdown manual
    md_path = Path(__file__).parent.parent / "assets/manual.md"
    
    if not md_path.exists():
        st.error(f"マニュアルファイルが見つかりません: {md_path.absolute()}")
        return

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Markdown内のローカル画像(相対パス)をBase64 Data URIに変換する
        def replace_img_with_base64(match):
            alt_text = match.group(1)
            img_rel_path = match.group(2)
            
            # URLの場合はスキップ
            if img_rel_path.startswith("http://") or img_rel_path.startswith("https://") or img_rel_path.startswith("data:"):
                return match.group(0)
            
            # "assets/setup_flow.png" のような指定も考慮し、mdファイルからの相対パスとして解決
            img_full_path = md_path.parent / img_rel_path.replace("assets/", "")
            
            if img_full_path.exists():
                b64_data = get_base64_image(img_full_path)
                if b64_data:
                    ext = img_full_path.suffix.lower()
                    mime = "image/png" if ext == ".png" else "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/gif"
                    return f"![{alt_text}](data:{mime};base64,{b64_data})"
            return match.group(0)

        md_content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img_with_base64, md_content)

        # Display Markdown
        st.markdown(md_content, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"マニュアル読み込みエラー: {e}")

if __name__ == "__main__":
    render_help()
