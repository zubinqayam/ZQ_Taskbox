$ErrorActionPreference = "Stop"

function Convert-ToWslPath {
    param([Parameter(Mandatory = $true)][string]$WindowsPath)

    $converted = ""
    try {
        $converted = (wsl wslpath -a "$WindowsPath" 2>$null)
    } catch {
        $converted = ""
    }

    if ($converted) {
        $converted = $converted.Trim()
        if ($converted -match '^/') {
            return $converted
        }
    }

    if ($WindowsPath -match '^[A-Za-z]:\\') {
        $drive = $WindowsPath.Substring(0, 1).ToLower()
        $rest = $WindowsPath.Substring(2).Replace('\', '/')
        return "/mnt/$drive$rest"
    }

    throw "Could not convert Windows path to WSL path: $WindowsPath"
}

if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    throw "WSL is required for APK builds on Windows. Install WSL first: wsl --install"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$repoWslPath = Convert-ToWslPath -WindowsPath $repoRoot

Write-Host "Running signed release APK build inside WSL Ubuntu..."
Write-Host "Before running, export in WSL: APK_KEYSTORE_PASSWORD and APK_KEY_PASSWORD"
wsl bash -lc "cd '$repoWslPath' && chmod +x scripts/build_apk_release_wsl.sh && ./scripts/build_apk_release_wsl.sh"
