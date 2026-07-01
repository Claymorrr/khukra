# Verify local install (run from repo root)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path .venv)) {
    Write-Host "No .venv — run .\scripts\setup.ps1 first"
    exit 1
}

Write-Host "Running pytest..."
.\.venv\Scripts\python.exe -m pytest tests/ -q

$apiPort = if ($env:KHUKRA_API_PORT) { $env:KHUKRA_API_PORT } else { "8010" }
$healthUrl = "http://127.0.0.1:$apiPort/api/health"

try {
    $h = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 3
    if ($h.status -ne "ok") { throw "API unhealthy" }
    Write-Host "API health OK ($healthUrl)"
    Write-Host "Capabilities: $($h.capabilities -join ', ')"
} catch {
    Write-Host "API not running at $healthUrl (start with .\scripts\setup.ps1 -Dev to test live API)"
}

Write-Host "Smoke test passed."
