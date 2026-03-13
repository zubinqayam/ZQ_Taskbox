$ErrorActionPreference = "Stop"

if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    throw "WSL is required for APK builds on Windows. Install WSL first: wsl --install"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$repoWslPath = (wsl wslpath -a "$repoRoot").Trim()

Write-Host "Running signed release APK build inside WSL Ubuntu..."
Write-Host "Before running, export in WSL: APK_KEYSTORE_PASSWORD and APK_KEY_PASSWORD"
wsl bash -lc "cd '$repoWslPath' && chmod +x scripts/build_apk_release_wsl.sh && ./scripts/build_apk_release_wsl.sh"
