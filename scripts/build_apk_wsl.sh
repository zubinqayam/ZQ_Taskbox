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
        rm -f "$dest.tmp" "$dest"
        continue
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

  # SHA256 hashes are not pinned here; pass a 64-char hex string as the 3rd
  # argument to enable verification once you have the official release checksums.
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

echo "[1/5] Installing system packages for Buildozer"
if command -v apt-get >/dev/null 2>&1; then
  run_pkg_cmd apt-get update
  run_pkg_cmd apt-get install -y \
    git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config patch \
    zlib1g-dev libncurses-dev libffi-dev libssl-dev
elif command -v dnf >/dev/null 2>&1; then
  run_pkg_cmd dnf -y install \
    git zip unzip python3-pip autoconf libtool pkgconf-pkg-config patch \
    zlib-devel ncurses-devel libffi-devel openssl-devel
  java_pkgs=("java-25-openjdk-devel" "java-21-openjdk-devel" "java-17-openjdk-devel")
  selected_java_pkg=""
  for pkg in "${java_pkgs[@]}"; do
    if dnf list available "$pkg" >/dev/null 2>&1 || dnf list installed "$pkg" >/dev/null 2>&1; then
      selected_java_pkg="$pkg"
      break
    fi
  done
  if [[ -n "$selected_java_pkg" ]]; then
    run_pkg_cmd dnf -y install "$selected_java_pkg"
    echo "Using $selected_java_pkg (selected via dnf detection)"
  else
    echo "No suitable OpenJDK package found via dnf (tried: ${java_pkgs[*]}). Please install Java manually."
  fi
else
  echo "Unsupported package manager. Install dependencies manually."
  exit 1
fi

echo "[2/5] Installing Buildozer"
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools wheel
python3 -m pip install cython==0.29.33 buildozer

echo "[3/5] Pre-fetching SDL deps with retry/mirrors"
prefetch_sdl_deps

echo "[4/5] Building Android APK (debug sideload)"
echo y | buildozer android debug

echo "[5/5] Output APK path"
ls -lh bin/*.apk
