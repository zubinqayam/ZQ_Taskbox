#!/usr/bin/env bash
set -euo pipefail

run_pkg_cmd() {
  if command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    "$@"
  fi
}

download_with_retry_mirror() {
  local url="$1"
  local dest="$2"
  local sha256="$3"
  shift 3
  local mirrors=("$@")
  local max_retries=3
  local retry_delay=5

  echo "Downloading $url to $dest..."
  for attempt in $(seq 1 $((max_retries + ${#mirrors[@]}))); do
    local current_url="$url"
    if [ $attempt -gt $max_retries ]; then
      local mirror_idx=$((attempt - max_retries - 1))
      if [ $mirror_idx -lt ${#mirrors[@]} ]; then
        current_url="${mirrors[$mirror_idx]}"
        echo "Trying mirror: $current_url (attempt $attempt)"
      fi
    fi

    if curl --fail --location --retry 3 --retry-delay 2 -o "$dest.tmp" "$current_url" 2>/dev/null; then
      if [[ -z "$sha256" ]]; then
        mv "$dest.tmp" "$dest"
        echo "✓ Downloaded: $dest (no checksum)"
        return 0
      elif echo "$sha256  $dest.tmp" | sha256sum --check - >/dev/null 2>&1; then
        mv "$dest.tmp" "$dest"
        echo "✓ SHA256 verified: $dest"
        return 0
      else
        echo "✗ SHA256 mismatch for download from $current_url"
      fi
    fi
    rm -f "$dest.tmp"
    sleep $((retry_delay * attempt))
  done
  echo "✗ Failed: $url and mirrors"
  return 1
}

prefetch_sdl_deps() {
  local api="${ANDROID_API:-34}"
  local platform_dir="$HOME/.buildozer/android/platform/android-$api"
  mkdir -p "$platform_dir"/patches/{SDL2,SDL2_image,SDL2_mixer,SDL2_ttf,python3}

  download_with_retry_mirror \
    "https://github.com/libsdl-org/SDL/archive/refs/tags/release-2.30.8.tar.gz" \
    "$platform_dir/patches/SDL2/SDL-release-2.30.8.tar.gz" \
    "" \
    "https://libsdl-org.s3.dualstack.us-east-1.amazonaws.com/release/SDL-2.30.8.tar.gz" \
    "https://www.libsdl.org/release/SDL-2.30.8.tar.gz"

  download_with_retry_mirror \
    "https://github.com/libsdl-org/SDL_image/archive/refs/tags/release-2.8.2.tar.gz" \
    "$platform_dir/patches/SDL2_image/SDL_image-release-2.8.2.tar.gz" \
    "" \
    "https://www.libsdl.org/projects/SDL_image/release/SDL2_image-2.8.2.tar.gz"

  download_with_retry_mirror \
    "https://github.com/libsdl-org/SDL_mixer/archive/refs/tags/release-2.8.0.tar.gz" \
    "$platform_dir/patches/SDL2_mixer/SDL_mixer-release-2.8.0.tar.gz" \
    "" \
    "https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-2.8.0.tar.gz"

  download_with_retry_mirror \
    "https://github.com/libsdl-org/SDL_ttf/archive/refs/tags/release-2.22.1.tar.gz" \
    "$platform_dir/patches/SDL2_ttf/SDL_ttf-release-2.22.1.tar.gz" \
    "" \
    "https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.22.1.tar.gz"

  echo "✓ SDL deps pre-fetched (full set). Buildozer will use these."
}

echo "[1/6] Installing system packages for Buildozer"
if command -v apt-get >/dev/null 2>&1; then
  run_pkg_cmd apt-get update
  run_pkg_cmd apt-get install -y \
    git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config patch \
    zlib1g-dev libncurses-dev libffi-dev libssl-dev
elif command -v dnf >/dev/null 2>&1; then
  run_pkg_cmd dnf -y install \
    git zip unzip python3-pip autoconf libtool pkgconf-pkg-config patch \
    zlib-devel ncurses-devel libffi-devel openssl-devel
  if dnf -q list available java-17-openjdk-devel >/dev/null 2>&1; then
    run_pkg_cmd dnf -y install java-17-openjdk-devel
  elif dnf -q list available java-21-openjdk-devel >/dev/null 2>&1; then
    run_pkg_cmd dnf -y install java-21-openjdk-devel
  elif dnf -q list available java-25-openjdk-devel >/dev/null 2>&1; then
    run_pkg_cmd dnf -y install java-25-openjdk-devel
  else
    echo "No supported OpenJDK devel package found (need Java 17+)."
    exit 1
  fi
else
  echo "Unsupported package manager. Install dependencies manually."
  exit 1
fi

echo "[2/6] Installing Buildozer"
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools wheel
python3 -m pip install cython==0.29.33 buildozer

echo "[3/6] Pre-fetching SDL deps with retry/mirrors"
prefetch_sdl_deps

echo "[4/6] Checking keystore"

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

echo "[4/6] Building Android APK (release unsigned)"
buildozer android release

echo "[5/6] Locating Android build tools"
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

echo "[6/6] Aligning and signing APK"
"$ZIPALIGN" -f 4 "$UNSIGNED_APK" "$ALIGNED_APK"
"$APKSIGNER" sign \
  --ks "$KEYSTORE_PATH" \
  --ks-key-alias "$KEY_ALIAS" \
  --ks-pass "env:APK_KEYSTORE_PASSWORD" \
  --key-pass "env:APK_KEY_PASSWORD" \
  --out "$SIGNED_APK" \
  "$ALIGNED_APK"

"$APKSIGNER" verify --verbose "$SIGNED_APK"

echo "[6/6] Signed APK ready"
ls -lh "$SIGNED_APK"
