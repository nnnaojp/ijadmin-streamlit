import streamlit as st
from utils.config_manager import get_mistral_cma_size
from utils.system_api import get_server_total_memory_gb

def show():
    st.title("印刷ページメモリ調整")
    st.write("印刷ページメモリを調整します。")
    st.subheader("現在のページメモリ")
    cma_mem = get_mistral_cma_size()
    server_mem = get_server_total_memory_gb()
    
    st.write(f"- サーバーメモリ:  {server_mem} GB")
    st.write(f"- 印刷ページメモリ:  {cma_mem} GB")
        
    st.write("") # Spacer
    
    if st.button("印刷ページメモリ調整"):
        # Placeholder for update logic
        st.success("印刷ページメモリを調整しました (未実装)")
