#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Installing system packages for Buildozer"
sudo apt-get update
sudo apt-get install -y \
  git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config \
  zlib1g-dev libncurses-dev libffi-dev libssl-dev

echo "[2/4] Installing Buildozer"
python3 -m pip install --upgrade pip
python3 -m pip install cython==0.29.33 buildozer

echo "[3/4] Building Android APK (debug sideload)"
buildozer android debug

echo "[4/4] Output APK path"
ls -lh bin/*.apk
