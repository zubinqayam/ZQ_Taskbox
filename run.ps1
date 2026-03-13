<#
  run.ps1 — ZQ_Taskbox one-click launcher for Windows PowerShell
  Copyright © 2026 ZQ AI LOGIC™  |  Apache License 2.0

  Usage:
    Right-click run.ps1 → Run with PowerShell
    — OR —
    cd ZQ_Taskbox && .\run.ps1
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ZQ_Taskbox — INNM Taskbox V2" -ForegroundColor Cyan
Write-Host "  Copyright (c) 2026 ZQ AI LOGIC" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Locate Python ───────────────────────────────────────────────
if (Test-Path ".\venv\Scripts\python.exe") {
    $PY = ".\venv\Scripts\python.exe"
    Write-Host "[OK] Using venv Python: $PY" -ForegroundColor Green
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PY = "python"
    Write-Host "[OK] Using system Python" -ForegroundColor Yellow
} else {
    Write-Host "[ERROR] Python not found. Install Python 3.10+ and re-run." -ForegroundColor Red
    pause
    exit 1
}

# ── 2. Create venv if missing ──────────────────────────────────────
if (-Not (Test-Path ".\venv")) {
    Write-Host "[SETUP] Creating virtual environment..." -ForegroundColor Yellow
    & $PY -m venv venv
    $PY = ".\venv\Scripts\python.exe"
    Write-Host "[OK] venv created" -ForegroundColor Green
}

# ── 3. Install / upgrade dependencies ──────────────────────────────
Write-Host "[SETUP] Installing dependencies (first run may take a minute)..." -ForegroundColor Yellow
& $PY -m pip install --quiet --upgrade pip
& $PY -m pip install --quiet kivy[base] pandas openpyxl requests

# ── 4. Launch the app ──────────────────────────────────────────────
Write-Host ""
Write-Host "[LAUNCH] Starting INNM Taskbox..." -ForegroundColor Cyan
Write-Host ""
& $PY main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] App exited with code $LASTEXITCODE" -ForegroundColor Red
    pause
}
