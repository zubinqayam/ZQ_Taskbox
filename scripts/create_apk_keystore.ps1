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
    throw "WSL is required for APK signing setup. Install WSL first: wsl --install"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$repoWslPath = Convert-ToWslPath -WindowsPath $repoRoot

Write-Host "Generating Android keystore inside WSL..."
Write-Host "Tip: you can pre-set env vars APK_KEYSTORE_PASSWORD and APK_KEY_PASSWORD in WSL."
wsl bash -lc "cd '$repoWslPath' && chmod +x scripts/create_apk_keystore_wsl.sh && ./scripts/create_apk_keystore_wsl.sh"
