<#
.SYNOPSIS
  Syncs board.manifest.json to GitHub Issues + "Khukra Operations" Project board.

.PREREQUISITES
  gh auth refresh -s project,read:project

.USAGE
  powershell -ExecutionPolicy Bypass -File scripts/sync-operations-board.ps1
  powershell -ExecutionPolicy Bypass -File scripts/sync-operations-board.ps1 -OpenBoard
#>

param(
    [string]$ManifestPath = "",
    [string]$Owner = "Claymorrr",
    [switch]$OpenBoard
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $ManifestPath) { $ManifestPath = Join-Path $root "board.manifest.json" }

function FromJson($s) { $s | ConvertFrom-Json }

function Ensure-Label($Repo, $Name, $Color = "ededed") {
    $names = gh label list --repo $Repo --json name -q ".[].name" 2>$null
    if ($names -contains $Name) { return }
    gh label create $Name --repo $Repo --color $Color --force 1>$null 2>$null
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$projectTitle = $manifest.project_title
$statusFieldName = $manifest.status_field
$statusOptions = @($manifest.status_options)

Write-Host "==> Verifying gh project scope..."
gh project list --owner $Owner 1>$null 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Run: gh auth refresh -s project,read:project"
    exit 1
}

# Create or reuse project
$projects = FromJson (gh project list --owner $Owner --format json)
$project = $projects.projects | Where-Object { $_.title -eq $projectTitle } | Select-Object -First 1
if ($null -eq $project) {
    Write-Host "==> Creating project '$projectTitle'..."
    $project = FromJson (gh project create --owner $Owner --title $projectTitle --format json)
} else {
    Write-Host "==> Reusing project '$projectTitle' (#$($project.number))."
}
$projNumber = $project.number
$projId = $project.id

# Status field
$fields = FromJson (gh project field-list $projNumber --owner $Owner --format json)
$field = $fields.fields | Where-Object { $_.name -eq $statusFieldName } | Select-Object -First 1
if ($null -eq $field) {
    Write-Host "==> Creating '$statusFieldName' field..."
    $optArg = ($statusOptions -join ",")
    gh project field-create $projNumber --owner $Owner --name $statusFieldName `
        --data-type SINGLE_SELECT --single-select-options $optArg 1>$null
    $fields = FromJson (gh project field-list $projNumber --owner $Owner --format json)
    $field = $fields.fields | Where-Object { $_.name -eq $statusFieldName } | Select-Object -First 1
}
$fieldId = $field.id
$statusMap = @{}
foreach ($opt in $field.options) { $statusMap[$opt.name] = $opt.id }

# Link default repo
$defaultRepo = $manifest.default_repo
if ($defaultRepo) {
    gh project link $projNumber --owner $Owner --repo $defaultRepo 1>$null 2>$null
}

foreach ($item in $manifest.items) {
    $repo = if ($item.repo) { $item.repo } else { $defaultRepo }
    foreach ($label in @($item.labels)) {
        Ensure-Label -Repo $repo -Name $label
    }
    $labels = @($item.labels) -join ","
    $marker = "[$( $item.id )]"
    $existing = FromJson (gh issue list --repo $repo --state all --search $item.id --json number,title,url --limit 5)
    $issue = $existing | Where-Object { $_.title -like "*$($item.id)*" } | Select-Object -First 1

    if ($null -eq $issue) {
        Write-Host "==> Creating $($item.id): $($item.title)"
        $body = @(
            $item.body
            ""
            "---"
            "Board ID: ``$($item.id)``"
            "Status: $($item.status)"
            "Synced from board.manifest.json"
        ) -join "`n"
        $createArgs = @(
            "issue", "create",
            "--repo", $repo,
            "--title", "$marker $($item.title)",
            "--body", $body
        )
        foreach ($label in @($item.labels)) { $createArgs += @("--label", $label) }
        $issueUrl = gh @createArgs 2>$null
        if ($LASTEXITCODE -ne 0) {
            $issueUrl = gh issue create --repo $repo --title "$marker $($item.title)" --body $body
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to create $($item.id) on $repo."
            continue
        }
        $issue = FromJson (gh issue view $issueUrl --json number,url)
    } else {
        Write-Host "==> Updating $($item.id) (#$($issue.number))"
        gh issue edit $issue.number --repo $repo --title "$marker $($item.title)" 1>$null
    }

    $itemJson = FromJson (gh project item-add $projNumber --owner $Owner --url $issue.url --format json)
    $optId = $statusMap[$item.status]
    if ($optId) {
        gh project item-edit --id $itemJson.id --project-id $projId --field-id $fieldId `
            --single-select-option-id $optId 1>$null
    }
    Write-Host "   -> $($item.status)"
}

Write-Host ""
Write-Host "DONE. Open board: gh project view $projNumber --owner $Owner --web"
if ($OpenBoard) {
    gh project view $projNumber --owner $Owner --web
}
