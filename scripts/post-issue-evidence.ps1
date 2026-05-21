# Post verification evidence to open Khukra issues (repo-ready batch).
$Evidence = @"
## Verification (repo-ready)

- Backend: ``pytest tests -q`` — 26 passed
- Frontend: ``npm run build`` — success
- Artifacts: CI (``.github/workflows/ci.yml``), ``Dockerfile``, ``.env.example``, ``scripts/smoke-test.ps1``
- API: ``/api/v1/*`` products/workflows/governance; audit logs; external model registry
- Data: migration v7 (audit, snapshots, external_models); ``KHUKRA_DATA_ROOT``

Restart API on port 8000 (kill stale uvicorn) before smoke: ``.\scripts\start-dev.ps1``
"@

$CloseReady = @(2,3,4,6,7,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,25,26,27,29,30)
$StatusOnly = @(1,5,24,28)  # hosting creds or full acceptance re-audit pending

foreach ($n in $CloseReady) {
    gh issue comment $n --body $Evidence 2>$null
    if ($LASTEXITCODE -eq 0) { gh issue close $n --comment "Closed: acceptance met in repo (see prior comment)." 2>$null }
}

foreach ($n in $StatusOnly) {
    gh issue comment $n --body "$Evidence`n`n**Status:** Repo-ready items delivered; full production acceptance still pending (hosting/credentials or re-audit per plan)." 2>$null
}

Write-Host "Posted evidence to issues."
