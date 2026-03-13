#!/usr/bin/env bash
set -euo pipefail

echo "[1/6] Installing system packages for Buildozer"
sudo apt-get update
sudo apt-get install -y \
  git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config \
  zlib1g-dev libncurses-dev libffi-dev libssl-dev

echo "[2/6] Installing Buildozer"
python3 -m pip install --upgrade pip
python3 -m pip install cython==0.29.33 buildozer

KEYSTORE_PATH="${APK_KEYSTORE_PATH:-.secrets/innm-upload.jks}"
KEY_ALIAS="${APK_KEY_ALIAS:-innmupload}"

if [[ ! -f "$KEYSTORE_PATH" ]]; then
  echo "Missing keystore: $KEYSTORE_PATH"
  echo "Create one first with: ./scripts/create_apk_keystore_wsl.sh"
  exit 1
fi

if [[ -z "${APK_KEYSTORE_PASSWORD:-}" || -z "${APK_KEY_PASSWORD:-}" ]]; then
  echo "Missing signing passwords."
  echo "Set APK_KEYSTORE_PASSWORD and APK_KEY_PASSWORD in your WSL shell."
  exit 1
fi

echo "[3/6] Building Android APK (release unsigned)"
buildozer android release

echo "[4/6] Locating Android build tools"
BUILD_TOOLS_DIR=$(find "$HOME/.buildozer/android/platform/android-sdk/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -n 1)
if [[ -z "${BUILD_TOOLS_DIR:-}" ]]; then
  echo "Android build-tools not found"
  exit 1
fi

ZIPALIGN="$BUILD_TOOLS_DIR/zipalign"
APKSIGNER="$BUILD_TOOLS_DIR/apksigner"
UNSIGNED_APK=$(ls -t bin/*-release-unsigned.apk | head -n 1)
ALIGNED_APK="${UNSIGNED_APK%-unsigned.apk}-aligned.apk"
SIGNED_APK="${UNSIGNED_APK%-unsigned.apk}-signed.apk"

echo "[5/6] Aligning and signing APK"
"$ZIPALIGN" -f 4 "$UNSIGNED_APK" "$ALIGNED_APK"
"$APKSIGNER" sign \
  --ks "$KEYSTORE_PATH" \
  --ks-key-alias "$KEY_ALIAS" \
  --ks-pass "pass:$APK_KEYSTORE_PASSWORD" \
  --key-pass "pass:$APK_KEY_PASSWORD" \
  --out "$SIGNED_APK" \
  "$ALIGNED_APK"

"$APKSIGNER" verify --verbose "$SIGNED_APK"

echo "[6/6] Signed APK ready"
ls -lh "$SIGNED_APK"
