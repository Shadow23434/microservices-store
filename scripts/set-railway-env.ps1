# set-railway-env.ps1 - Set environment variables từ file .env.railway

$ErrorActionPreference = "Stop"

$envFile = Join-Path $PSScriptRoot "..\.env.railway"

if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: File .env.railway not found!" -ForegroundColor Red
    exit 1
}

Write-Host "=== Setting Railway Environment Variables ===" -ForegroundColor Cyan
Write-Host ""

$vars = Get-Content $envFile | Where-Object { $_ -match '^\s*[^#]' -and $_.Trim() }

$count = 0
foreach ($line in $vars) {
    if ($line -match '^\s*([^=]+)=(.*)$') {
        $key = $Matches[1].Trim()
        $value = $Matches[2].Trim()

        Write-Host "Setting $key..." -ForegroundColor Gray
        railway variable set "$key=$value" 2>$null

        if ($LASTEXITCODE -eq 0) {
            $count++
            Write-Host "  [OK] $key" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] $key" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== Set $count variables successfully ===" -ForegroundColor Green
