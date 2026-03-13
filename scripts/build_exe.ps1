$ErrorActionPreference = "Stop"

Write-Host "[1/4] Cleaning old build artifacts..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

Write-Host "[2/4] Installing packaging dependencies..."
python -m pip install --upgrade pip
python -m pip install pyinstaller

Write-Host "[3/3] Building INNM_Taskbox.exe..."
python -m PyInstaller --noconfirm --onefile --windowed --name INNM_Taskbox --add-data "ui.kv;." main.py
Write-Host "[3/4] Installing project dependencies from requirements.txt..."
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
} else {
    Write-Warning "requirements.txt not found; skipping installation of project dependencies."
}

Write-Host "[4/4] Building INNM_Taskbox.exe..."
python -m PyInstaller --noconfirm --onefile --name INNM_Taskbox INNM_Taskbox.py

Write-Host "Build complete: dist/INNM_Taskbox.exe"
