# Start khukra API + Next.js frontend (run from project root)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$apiPort = if ($env:KHUKRA_API_PORT) { $env:KHUKRA_API_PORT } else { "8000" }
$env:KHUKRA_API_PORT = $apiPort
$env:KHUKRA_API_URL = "http://127.0.0.1:$apiPort"
$env:NEXT_PUBLIC_API_URL = $env:KHUKRA_API_URL
@"
# Auto-synced by scripts/start-dev.ps1 — must match KHUKRA_API_PORT
KHUKRA_API_URL=$($env:KHUKRA_API_URL)
NEXT_PUBLIC_API_URL=$($env:NEXT_PUBLIC_API_URL)
"@ | Set-Content -Encoding utf8 "$root\frontend\.env.local"

Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'uvicorn khukra\.api\.main'
} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'khukra\\frontend' -and $_.CommandLine -match 'next'
} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
Remove-Item -Recurse -Force "$root\frontend\.next" -ErrorAction SilentlyContinue

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; `$env:KHUKRA_API_PORT='$apiPort'; .venv\Scripts\python.exe -m uvicorn khukra.api.main:app --host 0.0.0.0 --port $apiPort --reload"
Start-Sleep -Seconds 2
Set-Location "$root\frontend"
if (-not (Test-Path node_modules)) { npm install }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; `$env:KHUKRA_API_URL='http://127.0.0.1:$apiPort'; npm run dev"
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
Write-Host "API: http://localhost:$apiPort/docs"
Write-Host "UI:  http://localhost:3000"
Write-Host "Admin: admin@khukra.local / khukra-admin"
