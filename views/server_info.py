import streamlit as st
from utils.system_api import get_mistral_version, get_pdc_versions, get_hif_versions, get_cpu_info, get_memory_info, get_disk_info, write_syslog 

def show():
    write_syslog("starting server_info")
    
    st.title("サーバー情報")
    st.write("ハードウェア情報を表示します。")

    st.subheader("CPU")
    st.code(get_cpu_info(), language=None)

    st.subheader("メモリ")
    st.code(get_memory_info(), language=None)

    st.subheader("ディスク")
    st.code(get_disk_info(), language=None)

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.subheader("Mistralバージョン")
    with col2:
        if st.button("表示更新", use_container_width=True):
            st.rerun()
            
    st.code(get_mistral_version(), language=None)
    
    st.subheader("PDCバージョン")
    pdc_versions = get_pdc_versions()
    # pdc_str = " ".join(pdc_versions) if pdc_versions else "Unknown"
    if pdc_versions:
        pdc_str = "\n".join(pdc_versions)
    else:
        pdc_str = "Unknown"
    st.code(pdc_str, language=None)
    
    st.subheader("HIFバージョン")
    hif_versions = get_hif_versions()
    if hif_versions:
        hif_str = "\n".join([" ".join(map(str, row)) for row in hif_versions])
    else:
        hif_str = "Unknown"
    st.code(hif_str, language=None)
