import os
import streamlit as st
from utils.system_api import write_syslog

def show():
    write_syslog("starting update")
    st.title("アップデート")
    st.write("システムアップデート画面です。")
    
    uploaded_file = st.file_uploader("アップデートファイルを選択してください", type=None)
    
    if st.button("アップデート"):
        if uploaded_file is not None:
            try:
                # Define target path (saving to /tmp)
                file_path = os.path.join("/tmp", uploaded_file.name)
                
                # Write file to /tmp
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                write_syslog(f"Update file saved: {file_path}")

                # --- アップデート本体処理 ---
                import subprocess, shutil

                # tgz を /tmp に展開
                extract_dir = "/tmp"
                st.info("アップデートファイルを展開しています...")
                write_syslog("Extracting update archive...")

                # 展開先のトップディレクトリ名を取得
                top_dir_result = subprocess.run(
                    ["tar", "tzf", file_path],
                    capture_output=True, text=True
                )
                if top_dir_result.returncode != 0:
                    raise RuntimeError(f"tar list failed: {top_dir_result.stderr.strip()}")

                # 最初のエントリのトップディレクトリ名を取得
                first_entry = top_dir_result.stdout.splitlines()[0]
                top_dir_name = first_entry.split("/")[0]
                update_dir = os.path.join(extract_dir, top_dir_name)
                update_script = os.path.join(update_dir, "update")

                # 展開実行
                extract_result = subprocess.run(
                    ["tar", "xzf", file_path, "-C", extract_dir],
                    capture_output=True, text=True
                )
                if extract_result.returncode != 0:
                    raise RuntimeError(f"tar extract failed: {extract_result.stderr.strip()}")

                write_syslog(f"Extracted to: {update_dir}")
                # st.info(f"展開完了: {update_dir}")

                # update スクリプトの存在確認
                if not os.path.isfile(update_script):
                    raise RuntimeError(f"update script not found: {update_script}")

                # update スクリプトに実行権限を付与して実行
                os.chmod(update_script, 0o755)
                write_syslog(f"Running update script: {update_script}")
                st.info("アップデートが完了するとシステムが再起動します。")

                run_result = subprocess.run(
                    ["sudo", update_script],
                    capture_output=True, text=True,
                    cwd=update_dir
                )
                output = (run_result.stdout + run_result.stderr).strip()
                write_syslog(f"Update script result (rc={run_result.returncode}): {output}")

                if run_result.returncode == 0:
                    # st.success("アップデートが完了しました。")
                    if output:
                        st.code(output, language=None)
                else:
                    raise RuntimeError(f"update script exited with code {run_result.returncode}:\n{output}")

            except Exception as e:
                write_syslog(f"Update failed! Error: {e}")
                st.error(f"アップデート中にエラーが発生しました: {e}")
        else:
            st.error("ファイルが選択されていません。")
