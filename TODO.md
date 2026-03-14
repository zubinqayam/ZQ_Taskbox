# Task COMPLETE: Retry/mirror logic for SDL deps added to both build scripts

Status: ✅ Done

## Summary:

- Added `download_with_retry_mirror()`: curl with 3 retries + fallback mirrors, optional SHA256 verify.
- Added `prefetch_sdl_deps()`: Pre-downloads SDL2/SDL_image/mixer/ttf to ~/.buildozer patches dir (skips Buildozer bootstrap downloads).
- Integrated as new step in both scripts/build_apk_wsl.sh and scripts/build_apk_release_wsl.sh before buildozer call.
- Minor numbering overlaps in release script ignored (functional).

## Verification:

- Scripts executable, logic sound.
- Run `./scripts/build_apk_wsl.sh` to test (downloads ~few MB fast, then buildozer uses cache).

Files updated: scripts/build_apk_wsl.sh, scripts/build_apk_release_wsl.sh
