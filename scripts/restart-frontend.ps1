# Restart Next.js dev with a clean .next cache (fixes vendor-chunks MODULE_NOT_FOUND)
$root = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $root "frontend"

Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'khukra\\frontend' -and ($_.CommandLine -match 'next' -or $_.Name -eq 'node.exe')
} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Remove-Item -Recurse -Force (Join-Path $frontend ".next") -ErrorAction SilentlyContinue
Set-Location $frontend
Write-Host "Starting Next dev (clean cache)..."
npm run dev
