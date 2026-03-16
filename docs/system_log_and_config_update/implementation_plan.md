# 実装計画

## 概要
ユーザーからの要望に基づき、以下の2つの主要な修正を実施する。
1. `mistral.json` からの `nHead` (各色ごとのラインヘッド数) の正確な抽出と、それに基づいた `PrintWidth` (印字幅) の動的な計算ロジックの修正。
2. アプリケーションの各画面（`views/*.py`）が呼び出された際に、syslogに `starting [View名]` という実行ログを出力する連携の追加。

## 変更内容

### `utils/config_manager.py`
- `load_config` 関数内で、`Server.PDC.LB` の構造に基づいて `LBID` から使用されている総ヘッド数 (`nHead`) を色ごとに正確にカウントするロジックを実装。
- 算出された `color_head_counts` の最初の要素（黒のヘッド数）を利用し、`PrintWidth` を `color_head_counts[0] * 43` mm として計算・表示する処理を追加。

### `views` ディレクトリ下の全ファイル
各UI画面が起動されたことをトラッキングするため、すべてのビューの `show()` 関数の先頭で `utils.system_api` の `write_syslog` を呼び出す。

- `views/datetime_view.py`
- `views/log_search.py`
- `views/log.py`
- `views/pagemem_config.py`
- `views/raid_config.py`
- `views/reboot.py`
- `views/server_config.py`
- `views/server_info.py`
- `views/update.py`

各ファイルに `write_syslog("starting [該当ファイル名（拡張子なし）]")` という行を追加する。

## 確認方法（Verification Plan）
### 手動での確認
- `ijadmin-ui.streamlit` を起動し、ブラウザ上で各メニューを選択する。
- サーバー上で `syslog` を確認し、選択したメニューに対応する `starting ...` のログが `[INFO]` レベルで出力されていることを目視で確認する。
- サーバー設定等で `PrintWidth` の値が固定値の `516mm` ではなく、JSONから計算された適切な数値（例: `172mm`）になっていることをUI上で確認する。
