$ErrorActionPreference = "Stop"

if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    throw "WSL is required for APK signing setup. Install WSL first: wsl --install"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$repoWslPath = (wsl wslpath -a "$repoRoot").Trim()

Write-Host "Generating Android keystore inside WSL..."
Write-Host "Tip: you can pre-set env vars APK_KEYSTORE_PASSWORD and APK_KEY_PASSWORD in WSL."
wsl bash -lc "cd '$repoWslPath' && chmod +x scripts/create_apk_keystore_wsl.sh && ./scripts/create_apk_keystore_wsl.sh"
