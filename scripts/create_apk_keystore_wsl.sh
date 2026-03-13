#!/usr/bin/env bash
set -euo pipefail

mkdir -p .secrets

KEYSTORE_PATH="${APK_KEYSTORE_PATH:-.secrets/innm-upload.jks}"
KEY_ALIAS="${APK_KEY_ALIAS:-innmupload}"
KEY_DNAME="${APK_KEY_DNAME:-CN=INNM Taskbox, OU=ZQ AI LOGIC, O=ZQ AI LOGIC, L=Sohar, ST=Al Batinah, C=OM}"
KEY_VALIDITY_DAYS="${APK_KEY_VALIDITY_DAYS:-10000}"

if [[ -z "${APK_KEYSTORE_PASSWORD:-}" ]]; then
  read -r -s -p "Enter keystore password: " APK_KEYSTORE_PASSWORD
  echo
fi

if [[ -z "${APK_KEY_PASSWORD:-}" ]]; then
  read -r -s -p "Enter key password: " APK_KEY_PASSWORD
  echo
fi

if [[ -f "$KEYSTORE_PATH" ]]; then
  echo "Keystore already exists: $KEYSTORE_PATH"
  echo "Delete it first if you want to regenerate."
  exit 1
fi

keytool -genkeypair \
  -v \
  -keystore "$KEYSTORE_PATH" \
  -alias "$KEY_ALIAS" \
  -keyalg RSA \
  -keysize 2048 \
  -validity "$KEY_VALIDITY_DAYS" \
  -storepass:env APK_KEYSTORE_PASSWORD \
  -keypass:env APK_KEY_PASSWORD \
  -dname "$KEY_DNAME"

echo "Keystore created: $KEYSTORE_PATH"
