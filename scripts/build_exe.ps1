$ErrorActionPreference = "Stop"

Write-Host "[1/3] Cleaning old build artifacts..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

Write-Host "[2/3] Installing packaging dependencies..."
python -m pip install --upgrade pip
python -m pip install pyinstaller

Write-Host "[3/3] Building INNM_Taskbox.exe..."
python -m PyInstaller --noconfirm INNM_Taskbox.spec

Write-Host "Build complete: dist/INNM_Taskbox.exe"
