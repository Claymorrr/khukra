# Seed sample simulation runs so the dashboard has data to show
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$demos = @(
    @{ domain = "physical"; subdomain = "structural_mechanics"; model = "damped_oscillator" },
    @{ domain = "finance"; subdomain = "market_research"; model = "market_scenario_research" },
    @{ domain = "finance"; subdomain = "strategy_backtesting"; model = "strategy_backtest_validation" },
    @{ domain = "finance"; subdomain = "strategy_delivery"; model = "paper_trading_delivery_gate" },
    @{ domain = "supply_chain"; subdomain = "disruption_intelligence"; model = "disruption_risk_forecast" }
    @{ domain = "supply_chain"; subdomain = "quality_drift"; model = "defect_rate_forecast" }
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
