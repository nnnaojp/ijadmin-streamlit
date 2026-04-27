#!/bin/bash
set -euo pipefail

# ============================================================
# ijconfig-ui 難読化スクリプト
# 使い方: ./obfus-armor.sh
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
info "[1/2] PyArmor obfuscating..."
rm -rf "${DIST_DIR}"
pyarmor gen -O "${DIST_DIR}" "${SRC_DIR}"
info "      done → ${DIST_DIR}"

# --- Step 2: 調整 ---
info "[2/2] Installing files..."
mv ${DIST_DIR}/src/* ${DIST_DIR}
rmdir ${DIST_DIR}/src
cp -a .streamlit ${DIST_DIR}
cp -a ${SRC_DIR}/assets ${DIST_DIR}
cp ${SRC_DIR}/main.py ${DIST_DIR}
cp ${SRC_DIR}/pages/help.py ${DIST_DIR}/pages
info "      done → ${DIST_DIR}"

