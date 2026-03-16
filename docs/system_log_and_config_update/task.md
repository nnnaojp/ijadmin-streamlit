# 修正タスクリスト
- [ ] utils/config_manager.pyの修正
  - [x] LBIDから各色のヘッド数を算出する処理の追加
  - [x] mistral.json の Server > PDC > LB 構造からの正しい nHead 値抽出の修正
  - [x] color_head_counts[0] * 43 を用いた PrintWidth の計算ロジックの修正

- [x] 各UI画面の先頭に `starting ...` を syslog に出力する処理を追加
  - [x] `views/datetime_view.py`
  - [x] `views/log_search.py`
  - [x] `views/log.py`
  - [x] `views/pagemem_config.py`
  - [x] `views/raid_config.py`
  - [x] `views/reboot.py`
  - [x] `views/server_config.py`
  - [x] `views/server_info.py`
  - [x] `views/update.py`
