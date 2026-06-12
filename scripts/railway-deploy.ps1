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

    # Build all variables for this service
    $vars = @("DATABASE_URL=$dbUrl")
    $vars += "DJANGO_ALLOWED_HOSTS=*"
    $vars += "DJANGO_DEBUG=False"

    # Add service dependency URLs
    foreach ($dep in $Services[$svc].Deps) {
        $envVar = ($dep -replace '-', '_').ToUpper() + "_URL"
        $internalUrl = "http://${dep}.railway.internal:8888"
        $vars += "${envVar}=$internalUrl"
    }

    # Special config for recommender-ai-service
    if ($svc -eq "recommender-ai-service") {
        $vars += "LLM_PROVIDER=openrouter"
        $vars += "LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free"
    }

    # Link to service (interactive - user selects service from list)
    Write-Host "  Please select '$svc' from the list:" -ForegroundColor Yellow
    railway link

    # Set all variables at once
    Write-Host "  Setting $($vars.Count) variables..." -ForegroundColor Gray
    $varsString = $vars -join " "
    Invoke-Expression "railway variables set $varsString"

    Write-Host "  [OK] $svc configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== All services configured! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Deploy: railway up --service <service-name>" -ForegroundColor Yellow
Write-Host "  2. Or push to GitHub and Railway will auto-deploy" -ForegroundColor Yellow