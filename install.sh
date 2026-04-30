#!/bin/bash
set -euo pipefail

# ============================================================
# ijconfig-ui リリーススクリプト
# 使い方: sudo ./release.sh
# ============================================================

APP_USER="ijadmin"
APP_GROUP="devp"
APP_NAME="ijconfig-ui"
SRC_DIR="./src"
DIST_DIR="./dist"
BASE_DIR="/usr/mistral"
INSTALL_DIR="ijconfig-ui"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="streamlit-ijconfig.service"

# --- 色付きログ関数 ---
info()    { echo -e "\e[32m[INFO]\e[0m  $*"; }
warn()    { echo -e "\e[33m[WARN]\e[0m  $*"; }
error()   { echo -e "\e[31m[ERROR]\e[0m $*" >&2; }

# --- root確認 ---
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root."
    exit 1
fi

# --- インストール先ディレクトリの確認 ---
# if [[ ! -d "${BASE_DIR}/${INSTALL_DIR}" ]]; then
#     error "Installation directory not found. ${BASE_DIR}/${INSTALL_DIR}"
#     exit 1
# fi

# ============================================================

# --- Step 1: インストールディレクトリのクリア & コピー ---
info "[1/2] Clearing files..."
rm -rf /usr/mistral/ijconfig-ui
# rm -rf /usr/mistral/ijconfig-ui/*
info "[2/2] Installing files..."
cp -rp "${DIST_DIR}" "${BASE_DIR}/${INSTALL_DIR}"
chown -R ${APP_USER}:${APP_GROUP} "${BASE_DIR}/${INSTALL_DIR}"
info "      done → ${BASE_DIR}/${INSTALL_DIR}"

# ============================================================

