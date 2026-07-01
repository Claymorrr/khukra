# First-time setup for Khukra Logistics (run from repo root via .\scripts\setup.ps1)
param(
    [switch]$SeedData,
    [int]$Years = 5
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Require-Command($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $name"
    }
}

Write-Host "Khukra Logistics setup"
Write-Host "======================"

Require-Command python
Require-Command npm

$pyVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$pyMajor, $pyMinor = $pyVersion.Split(".") | ForEach-Object { [int]$_ }
if ($pyMajor -lt 3 -or ($pyMajor -eq 3 -and $pyMinor -lt 10)) {
    throw "Python 3.10+ required (found $pyVersion)"
}
Write-Host "Python $pyVersion"

if (-not (Test-Path .venv)) {
    Write-Host "Creating virtualenv..."
    python -m venv .venv
}

Write-Host "Installing Python package (editable + dev)..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip -q
.\.venv\Scripts\python.exe -m pip install -e ".[dev]" -q

Write-Host "Installing frontend dependencies..."
Set-Location frontend
if (-not (Test-Path node_modules)) { npm install }
Set-Location $root

if (-not (Test-Path data)) {
    New-Item -ItemType Directory -Path data | Out-Null
}

if ($SeedData) {
    Write-Host "Seeding disruption signal cache (${Years}y history; may take 1-2 min)..."
    .\.venv\Scripts\khukra-logistics.exe refresh --years $Years
    Write-Host "Polling RSS news feeds..."
    .\.venv\Scripts\khukra-logistics.exe refresh-news
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "  Run:  .\scripts\start-dev.ps1"
Write-Host "  Test: .\scripts\smoke-test.ps1"
if (-not $SeedData) {
    Write-Host "  Optional seed data: .\scripts\setup.ps1 -SeedData"
}
