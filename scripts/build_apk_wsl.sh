#!/usr/bin/env bash
set -euo pipefail

run_pkg_cmd() {
  if command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    "$@"
  fi
}

echo "[1/4] Installing system packages for Buildozer"
if command -v apt-get >/dev/null 2>&1; then
  run_pkg_cmd apt-get update
  run_pkg_cmd apt-get install -y \
    git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config patch \
    zlib1g-dev libncurses-dev libffi-dev libssl-dev
elif command -v dnf >/dev/null 2>&1; then
  run_pkg_cmd dnf -y install \
    git zip unzip python3-pip autoconf libtool pkgconf-pkg-config patch \
    zlib-devel ncurses-devel libffi-devel openssl-devel
  run_pkg_cmd dnf -y install java-25-openjdk-devel
  echo "Using java-25-openjdk-devel (detected)"
else
  echo "Unsupported package manager. Install dependencies manually."
  exit 1
fi

echo "[2/4] Installing Buildozer"
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools wheel
python3 -m pip install cython==0.29.33 buildozer

echo "[3/4] Building Android APK (debug sideload)"
echo y | buildozer android debug

echo "[4/4] Output APK path"
ls -lh bin/*.apk
