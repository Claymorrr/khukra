# Start khukra API + Next.js frontend (run from project root)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; .venv\Scripts\khukra-api.exe"
Start-Sleep -Seconds 2
Set-Location "$root\frontend"
if (-not (Test-Path node_modules)) { npm install }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
Write-Host "API: http://localhost:8000/docs"
Write-Host "UI:  http://localhost:3000"
Write-Host "Admin: admin@khukra.local / khukra-admin"
