#!/bin/bash
set -euo pipefail

# ============================================================
# ijconfig-ui 難読化スクリプト
# 使い方: ./obfus-pyc.sh
# ============================================================

APP_USER="ijadmin"
APP_GROUP="devp"
APP_NAME="ijconfig-ui"
SRC_DIR="./src"
DIST_DIR="./dist"

# --- 色付きログ関数 ---
info()    { echo -e "\e[32m[INFO]\e[0m  $*"; }
warn()    { echo -e "\e[33m[WARN]\e[0m  $*"; }
error()   { echo -e "\e[31m[ERROR]\e[0m $*" >&2; }

# --- Step 1: 難読化 ---
info "[1/1] pyc compiling..."
rm -rf "${DIST_DIR}"
cp -rf "$SRC_DIR" "$DIST_DIR"
find "$DIST_DIR" -name "*~" -delete
find "$DIST_DIR" -name "__pycache__" -type d -prune -exec rm -rf {} +
python3 -m compileall -b "${DIST_DIR}"
find "$DIST_DIR" -name "*.py" -delete
cp "$SRC_DIR"/main.py "$DIST_DIR"
cp "$SRC_DIR"/pages/help.py "$DIST_DIR"/pages
mkdir "$DIST_DIR"/.streamlit
cp -rp dot.streamlit/* "$DIST_DIR"/.streamlit
info "      done → ${DIST_DIR}"

