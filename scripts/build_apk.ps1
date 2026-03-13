$ErrorActionPreference = "Stop"

if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    throw "WSL is required for APK builds on Windows. Install WSL first: wsl --install"
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is required to build APKs. Install Python first."
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$repoWslPath = (wsl wslpath -a "$repoRoot").Trim()

Write-Host "Running APK build inside WSL Ubuntu..."
wsl bash -lc "cd '$repoWslPath' && chmod +x scripts/build_apk_wsl.sh && ./scripts/build_apk_wsl.sh"
