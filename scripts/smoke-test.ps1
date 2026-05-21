# Post-deploy / local smoke checks for Khukra
param(
    [string]$ApiBase = $(if ($env:KHUKRA_API_URL) { $env:KHUKRA_API_URL } else { "http://127.0.0.1:8000" }),
    [string]$AdminEmail = "admin@khukra.local",
    [string]$AdminPassword = "khukra-admin"
)

$ErrorActionPreference = "Stop"
$passed = 0
$failed = 0

function Test-Step($name, $script) {
    try {
        & $script
        Write-Host "[PASS] $name" -ForegroundColor Green
        $script:passed++
    } catch {
        Write-Host "[FAIL] $name - $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
    }
}

Test-Step "Health" {
    $r = Invoke-RestMethod "$ApiBase/api/health"
    if ($r.status -ne "ok" -and $r.status -ne "degraded") { throw "bad status" }
}

Test-Step "Login" {
    $body = @{ email = $AdminEmail; password = $AdminPassword } | ConvertTo-Json
    $global:token = (Invoke-RestMethod -Method POST -Uri "$ApiBase/api/auth/login" -Body $body -ContentType "application/json").access_token
    if (-not $global:token) { throw "no token" }
}

$headers = @{ Authorization = "Bearer $token" }

Test-Step "Catalog" {
    Invoke-RestMethod -Uri "$ApiBase/api/catalog" -Headers $headers | Out-Null
}

Test-Step "V1 products" {
    Invoke-RestMethod -Uri "$ApiBase/api/v1/products" -Headers $headers | Out-Null
}

Test-Step "Platform manifest" {
    Invoke-RestMethod -Uri "$ApiBase/api/platform/manifest" -Headers $headers | Out-Null
}

Test-Step "Versioning summary" {
    Invoke-RestMethod -Uri "$ApiBase/api/versioning/summary" -Headers $headers | Out-Null
}

Write-Host ""
Write-Host "Smoke: $passed passed, $failed failed"
if ($failed -gt 0) { exit 1 }
