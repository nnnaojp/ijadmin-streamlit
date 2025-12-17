import streamlit as st
from utils.system_api import get_mistral_version, get_pdc_versions, get_hif_versions

def show():
    st.title("サーバー情報")
    
    mistral_version = get_mistral_version()
    
    # Format PDC versions
    pdc_versions = get_pdc_versions()
    pdc_str = " ".join(pdc_versions) if pdc_versions else "Unknown"
    
    # Format HIF versions
    hif_versions = get_hif_versions()
    if hif_versions:
        # Join inner lists with space, outer list with newline + indent
        # Example: [[1,2], [3,4]] -> "1 2\n                    3 4"
        indent = " " * 19  # Matches "HIFバージョン    : " width (13 + 4 + 3 = 20)
        hif_str = (f"\n{indent}").join([" ".join(map(str, row)) for row in hif_versions])
    else:
        hif_str = "Unknown"
    
    server_info_text = f"""
Mistralバージョン : {mistral_version}
PDCバージョン     : {pdc_str}
HIFバージョン     : {hif_str}
"""
    st.code(server_info_text, language=None)
