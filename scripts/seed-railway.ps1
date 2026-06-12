# seed-railway.ps1 - Chạy seed script cho Railway
# Cách dùng: .\seed-railway.ps1 -ApiUrl "https://your-app.up.railway.app"

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiUrl,

    [string]$DatabaseUrl = ""
)

$ErrorActionPreference = "Stop"

Write-Host "=== Railway Seed Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python or add it to PATH" -ForegroundColor Yellow
    exit 1
}

# Check required packages
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$packages = @('psycopg2-binary', 'requests')
foreach ($pkg in $packages) {
    try {
        python -c "import $pkg.Replace('-binary','')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  Installing $pkg..." -ForegroundColor Gray
            pip install $pkg -q
        }
    } catch {
        Write-Host "  Installing $pkg..." -ForegroundColor Gray
        pip install $pkg -q
    }
}

# Set DATABASE_URL if not provided
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    Write-Host ""
    Write-Host "DATABASE_URL not provided." -ForegroundColor Yellow
    Write-Host "You can get it from Railway Dashboard:" -ForegroundColor Gray
    Write-Host "  1. Go to your Postgres service" -ForegroundColor Gray
    Write-Host "  2. Click 'Variables' tab" -ForegroundColor Gray
    Write-Host "  3. Copy DATABASE_URL value" -ForegroundColor Gray
    Write-Host ""

    $DatabaseUrl = Read-Host "Enter DATABASE_URL"

    if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
        Write-Host "ERROR: DATABASE_URL is required!" -ForegroundColor Red
        exit 1
    }
}

# Set environment variable
$env:DATABASE_URL = $DatabaseUrl

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  API URL: $ApiUrl" -ForegroundColor Gray
Write-Host "  Database: Connected" -ForegroundColor Gray
Write-Host ""

# Run seed script
Write-Host "Starting seed process..." -ForegroundColor Cyan
Write-Host ""

$seedScript = Join-Path $PSScriptRoot "seed_railway.py"

if (-not (Test-Path $seedScript)) {
    Write-Host "ERROR: seed_railway.py not found!" -ForegroundColor Red
    Write-Host "Expected location: $seedScript" -ForegroundColor Gray
    exit 1
}

python $seedScript --api-url $ApiUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Seed completed successfully! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now visit: $ApiUrl" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "=== Seed failed! ===" -ForegroundColor Red
    exit 1
}
