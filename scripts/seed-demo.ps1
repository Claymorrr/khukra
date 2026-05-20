# Seed sample simulation runs so the dashboard has data to show
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$demos = @(
    @{ domain = "physical"; subdomain = "structural_mechanics"; model = "damped_oscillator" },
    @{ domain = "finance"; subdomain = "derivatives_risk"; model = "black_scholes_option" },
    @{ domain = "supply_chain"; subdomain = "inventory_management"; model = "inventory_simulation" }
)

foreach ($d in $demos) {
    $body = @{ domain = $d.domain; subdomain = $d.subdomain; model = $d.model; parameters = @{} } | ConvertTo-Json
    try {
        $r = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/runs -Method POST -Body $body -ContentType "application/json"
        Write-Host "OK $($d.model) -> $($r.run_id)"
    } catch {
        Write-Host "Skip $($d.model): $_"
    }
}

Write-Host "Done. Open http://localhost:3000 and sign in."
