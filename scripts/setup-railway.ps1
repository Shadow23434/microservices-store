# Railway Deployment Setup Script
# Chạy script này để tự động setup mọi thứ cần thiết cho Railway deployment

param(
    [string]$PostgresUrl = "",
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

$ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ROOT = $PSScriptRoot | Split-Path -Parent

# Danh sách services và database tương ứng
$Services = @{
    "api-gateway" = @{
        DbName = "gateway_db"
        PythonPkg = "api_gateway"
        Dependencies = @("customer-service", "product-service", "cart-service", "staff-service", "manager-service", "catalog-service", "order-service", "ship-service", "pay-service", "comment-rate-service", "recommender-ai-service")
    }
    "customer-service" = @{
        DbName = "customer_db"
        PythonPkg = "customer_service"
        Dependencies = @("cart-service")
    }
    "product-service" = @{
        DbName = "product_db"
        PythonPkg = "product_service"
        Dependencies = @()
    }
    "cart-service" = @{
        DbName = "cart_db"
        PythonPkg = "cart_service"
        Dependencies = @("product-service")
    }
    "staff-service" = @{
        DbName = "staff_db"
        PythonPkg = "staff_service"
        Dependencies = @()
    }
    "manager-service" = @{
        DbName = "manager_db"
        PythonPkg = "manager_service"
        Dependencies = @()
    }
    "catalog-service" = @{
        DbName = "catalog_db"
        PythonPkg = "catalog_service"
        Dependencies = @()
    }
    "order-service" = @{
        DbName = "order_db"
        PythonPkg = "order_service"
        Dependencies = @("pay-service", "ship-service", "product-service")
    }
    "ship-service" = @{
        DbName = "ship_db"
        PythonPkg = "ship_service"
        Dependencies = @()
    }
    "pay-service" = @{
        DbName = "pay_db"
        PythonPkg = "pay_service"
        Dependencies = @()
    }
    "comment-rate-service" = @{
        DbName = "comment_rate_db"
        PythonPkg = "comment_rate_service"
        Dependencies = @()
    }
    "recommender-ai-service" = @{
        DbName = "recommender_db"
        PythonPkg = "recommender_ai_service"
        Dependencies = @("product-service", "comment-rate-service", "order-service", "cart-service")
    }
}

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  [!] $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

# ═══════════════════════════════════════════════════════════════
# STEP 1: Fix Dockerfiles for Railway (paths from root repo)
# ═══════════════════════════════════════════════════════════════

Write-Step "Step 1: Fixing Dockerfiles for Railway build context"

foreach ($svc in $Services.Keys) {
    $svcDir = Join-Path $ROOT $svc
    $dockerfilePath = Join-Path $svcDir "Dockerfile"
    $pkg = $Services[$svc].PythonPkg

    if (Test-Path $dockerfilePath) {
        $content = Get-Content $dockerfilePath -Raw

        # Fix COPY paths - thay "svc-name/requirements.txt" thành "requirements.txt"
        # vì Railway build từ root repo nhưng dockerfile path là svc/Dockerfile
        # Actually Railway với Nixpacks/Dockerfile builder, build context = root repo
        # nên "COPY api-gateway/requirements.txt ." là đúng
        # Nhưng cần đảm bảo wait_for_db.py path đúng
        $content = $content -replace "COPY docker/wait_for_db\.py \.", "COPY docker/wait_for_db.py ."

        Set-Content -Path $dockerfilePath -Value $content -NoNewline
        Write-Ok "$svc/Dockerfile - paths verified"
    } else {
        Write-Warn "$svc/Dockerfile not found"
    }
}

# ═══════════════════════════════════════════════════════════════
# STEP 2: Create railway.toml for each service
# ═══════════════════════════════════════════════════════════════

Write-Step "Step 2: Creating railway.toml for each service"

foreach ($svc in $Services.Keys) {
    $svcDir = Join-Path $ROOT $svc
    $tomlPath = Join-Path $svcDir "railway.toml"

    $tomlContent = @"
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"
watchPatterns = ["**/*.py", "**/*.html", "requirements.txt"]

[deploy]
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
"@

    if (-not $DryRun) {
        Set-Content -Path $tomlPath -Value $tomlContent -NoNewline
    }
    Write-Ok "$svc/railway.toml created"
}

# ═══════════════════════════════════════════════════════════════
# STEP 3: Copy wait_for_db.py to each service (backup)
# ═══════════════════════════════════════════════════════════════

Write-Step "Step 3: Verifying wait_for_db.py availability"

$waitForDbPath = Join-Path $ROOT "docker\wait_for_db.py"
if (Test-Path $waitForDbPath) {
    Write-Ok "docker/wait_for_db.py exists - Dockerfiles can COPY it from root context"
} else {
    Write-Warn "docker/wait_for_db.py NOT FOUND! Services will fail to start."
}

# ═══════════════════════════════════════════════════════════════
# STEP 4: Add gunicorn to requirements.txt
# ═══════════════════════════════════════════════════════════════

Write-Step "Step 4: Adding gunicorn to requirements.txt (Railway needs production server)"

foreach ($svc in $Services.Keys) {
    $reqPath = Join-Path $ROOT "$svc\requirements.txt"

    if (Test-Path $reqPath) {
        $content = Get-Content $reqPath -Raw
        if ($content -notmatch "gunicorn") {
            $content = $content.TrimEnd() + "`ngunicorn>=21.2.0`n"
            if (-not $DryRun) {
                Set-Content -Path $reqPath -Value $content -NoNewline
            }
            Write-Ok "$svc/requirements.txt - added gunicorn"
        } else {
            Write-Ok "$svc/requirements.txt - gunicorn already present"
        }
    }
}

# ═══════════════════════════════════════════════════════════════
# STEP 5: Update Dockerfiles to use gunicorn
# ═══════════════════════════════════════════════════════════════

Write-Step "Step 5: Updating Dockerfiles to use gunicorn for production"

foreach ($svc in $Services.Keys) {
    $dockerfilePath = Join-Path $ROOT "$svc\Dockerfile"
    $pkg = $Services[$svc].PythonPkg
    $wsgiApp = "$pkg.${pkg}.wsgi:application"

    if (Test-Path $dockerfilePath) {
        $content = Get-Content $dockerfilePath -Raw

        # Thay runserver bằng gunicorn
        $oldCmd = 'python manage.py runserver 0.0.0.0:8888'
        $newCmd = "gunicorn $wsgiApp --bind 0.0.0.0:8888 --workers 2 --timeout 120"

        $content = $content -replace [regex]::Escape($oldCmd), $newCmd

        if (-not $DryRun) {
            Set-Content -Path $dockerfilePath -Value $content -NoNewline
        }
        Write-Ok "$svc/Dockerfile - using gunicorn"
    }
}

# ═══════════════════════════════════════════════════════════════
# STEP 6: Generate Railway env var setup commands
# ═══════════════════════════════════════════════════════════════

Write-Step "Step 6: Railway Environment Variables Setup"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "  RAILWAY DEPLOYMENT INSTRUCTIONS" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "1. First, create Railway project and add PostgreSQL:" -ForegroundColor White
Write-Host "   railway init" -ForegroundColor Yellow
Write-Host "   railway add -d postgres" -ForegroundColor Yellow
Write-Host ""

Write-Host "2. Get DATABASE_URL from Railway:" -ForegroundColor White
Write-Host "   railway variables list" -ForegroundColor Yellow
Write-Host "   (copy the DATABASE_URL value)" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Create 12 databases in PostgreSQL:" -ForegroundColor White
Write-Host "   railway connect postgres" -ForegroundColor Yellow
Write-Host "   Then run these SQL commands:" -ForegroundColor Gray
Write-Host ""

foreach ($svc in $Services.Keys) {
    $dbName = $Services[$svc].DbName
    Write-Host "   CREATE DATABASE $dbName;" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "4. For each service, link and set variables:" -ForegroundColor White
Write-Host ""

# Generate individual service setup commands
foreach ($svc in $Services.Keys | Sort-Object) {
    $info = $Services[$svc]
    $dbName = $info.DbName
    $deps = $info.Dependencies

    Write-Host "--- $svc ---" -ForegroundColor Cyan
    Write-Host ""

    # Base env vars
    $dbUrl = "`${{Postgres.DATABASE_URL}}"
    Write-Host "  railway service $svc" -ForegroundColor Yellow
    Write-Host "  railway variables set DATABASE_URL=`"$dbUrl`" --service $svc" -ForegroundColor Yellow

    # Service dependency URLs - using Railway internal networking
    foreach ($dep in $deps) {
        $envVar = ($dep -replace '-', '_').ToUpper() + "_URL"
        # Railway internal URL format: http://service-name.railway.internal:8888
        $internalUrl = "http://${dep}.railway.internal:8888"
        Write-Host "  railway variables set ${envVar}=`"$internalUrl`" --service $svc" -ForegroundColor Yellow
    }

    # Special: recommender-ai-service needs LLM config
    if ($svc -eq "recommender-ai-service") {
        Write-Host "  railway variables set LLM_PROVIDER=`"openrouter`" --service $svc" -ForegroundColor Yellow
        Write-Host "  railway variables set LLM_MODEL=`"meta-llama/llama-3.1-8b-instruct:free`" --service $svc" -ForegroundColor Yellow
        Write-Host "  railway variables set OPENROUTER_API_KEY=`"your-key-here`" --service $svc" -ForegroundColor Yellow
    }

    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════
# STEP 7: Generate automated setup script
# ═══════════════════════════════════════════════════════════════

Write-Step "Step 7: Generating automated Railway setup script"

$autoScript = @'
# railway-deploy.ps1 - Tu dong deploy tat ca services len Railway
# Su dung: .\railway-deploy.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Railway Automated Deployment ===" -ForegroundColor Cyan

# Check railway CLI
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Railway CLI not installed!" -ForegroundColor Red
    Write-Host "Install with: npm install -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

# Prompt for DATABASE_URL
$DATABASE_URL = Read-Host "Enter Railway Postgres DATABASE_URL (from railway variables list)"

if ([string]::IsNullOrWhiteSpace($DATABASE_URL)) {
    Write-Host "ERROR: DATABASE_URL is required!" -ForegroundColor Red
    exit 1
}

# Service configs: Name -> @{ DbSuffix, Deps }
$Services = [ordered]@{
    "product-service"       = @{ Db = "product_db";      Deps = @() }
    "catalog-service"       = @{ Db = "catalog_db";      Deps = @() }
    "staff-service"         = @{ Db = "staff_db";        Deps = @() }
    "manager-service"       = @{ Db = "manager_db";      Deps = @() }
    "ship-service"          = @{ Db = "ship_db";         Deps = @() }
    "pay-service"           = @{ Db = "pay_db";          Deps = @() }
    "cart-service"          = @{ Db = "cart_db";         Deps = @("product-service") }
    "customer-service"      = @{ Db = "customer_db";     Deps = @("cart-service") }
    "comment-rate-service"  = @{ Db = "comment_rate_db"; Deps = @() }
    "order-service"         = @{ Db = "order_db";        Deps = @("pay-service", "ship-service", "product-service") }
    "recommender-ai-service"= @{ Db = "recommender_db";  Deps = @("product-service", "comment-rate-service", "order-service", "cart-service") }
    "api-gateway"           = @{ Db = "gateway_db";      Deps = @("customer-service", "product-service", "cart-service", "staff-service", "manager-service", "catalog-service", "order-service", "ship-service", "pay-service", "comment-rate-service", "recommender-ai-service") }
}

# Parse DATABASE_URL to replace db name
function Get-DbUrl {
    param([string]$BaseUrl, [string]$DbName)
    # postgresql://user:pass@host:port/xxx -> replace xxx with DbName
    if ($BaseUrl -match '^(postgresql://[^/]+/)(.+)$') {
        return $Matches[1] + $DbName
    }
    return $BaseUrl
}

foreach ($svc in $Services.Keys) {
    Write-Host ""
    Write-Host ">>> Setting up $svc..." -ForegroundColor Cyan

    $dbUrl = Get-DbUrl -BaseUrl $DATABASE_URL -DbName $Services[$svc].Db

    # Link to service
    Write-Host "  Linking to service..." -ForegroundColor Gray
    railway link $svc 2>$null

    # Set DATABASE_URL
    Write-Host "  Setting DATABASE_URL for $($Services[$svc].Db)..." -ForegroundColor Gray
    railway variables set "DATABASE_URL=$dbUrl" --service $svc

    # Set service dependency URLs
    foreach ($dep in $Services[$svc].Deps) {
        $envVar = ($dep -replace '-', '_').ToUpper() + "_URL"
        $internalUrl = "http://${dep}.railway.internal:8888"
        Write-Host "  Setting ${envVar}=$internalUrl" -ForegroundColor Gray
        railway variables set "${envVar}=${internalUrl}" --service $svc
    }

    # Special config for recommender-ai-service
    if ($svc -eq "recommender-ai-service") {
        Write-Host "  Setting LLM config..." -ForegroundColor Gray
        railway variables set "LLM_PROVIDER=openrouter" --service $svc
        railway variables set "LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free" --service $svc
    }

    # Django common vars
    railway variables set "DJANGO_ALLOWED_HOSTS=*" --service $svc
    railway variables set "DJANGO_DEBUG=False" --service $svc

    Write-Host "  [OK] $svc configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== All services configured! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Deploy: railway up --service <service-name>" -ForegroundColor Yellow
Write-Host "  2. Or push to GitHub and Railway will auto-deploy" -ForegroundColor Yellow
'@

$autoScriptPath = Join-Path $ROOT "scripts\railway-deploy.ps1"
if (-not $DryRun) {
    Set-Content -Path $autoScriptPath -Value $autoScript -NoNewline
}
Write-Ok "Generated scripts/railway-deploy.ps1"

# ═══════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "  - Fixed Dockerfiles for Railway build context" -ForegroundColor White
Write-Host "  - Created railway.toml for each service" -ForegroundColor White
Write-Host "  - Added gunicorn for production deployment" -ForegroundColor White
Write-Host "  - Generated railway-deploy.ps1 for automated env setup" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Create Railway project: railway init" -ForegroundColor Yellow
Write-Host "  2. Add PostgreSQL:       railway add -d postgres" -ForegroundColor Yellow
Write-Host "  3. Create 12 databases in Postgres" -ForegroundColor Yellow
Write-Host "  4. Run:                  .\scripts\railway-deploy.ps1" -ForegroundColor Yellow
Write-Host "  5. Deploy:               railway up --service api-gateway" -ForegroundColor Yellow
Write-Host ""