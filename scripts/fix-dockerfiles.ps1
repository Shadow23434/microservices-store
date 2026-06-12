# fix-dockerfiles.ps1 - Fix Dockerfiles cho Railway Root Directory build context
# Chạy từ thư mục gốc của project

$ErrorActionPreference = "Stop"
$ROOT = $PSScriptRoot | Split-Path -Parent

$Services = @{
    "api-gateway"            = "api_gateway"
    "cart-service"           = "cart_service"
    "catalog-service"        = "catalog_service"
    "comment-rate-service"   = "comment_rate_service"
    "customer-service"       = "customer_service"
    "manager-service"        = "manager_service"
    "order-service"          = "order_service"
    "pay-service"            = "pay_service"
    "product-service"        = "product_service"
    "recommender-ai-service" = "recommender_ai_service"
    "ship-service"           = "ship_service"
    "staff-service"          = "staff_service"
}

Write-Host "=== Fixing Dockerfiles for Railway Root Directory build ===" -ForegroundColor Cyan

foreach ($svc in $Services.Keys) {
    $svcDir = Join-Path $ROOT $svc
    $pkg = $Services[$svc]
    $dockerfile = Join-Path $svcDir "Dockerfile"

    # 1. Copy wait_for_db.py into service directory
    $waitDb = Join-Path $svcDir "wait_for_db.py"
    if (-not (Test-Path $waitDb)) {
        Copy-Item (Join-Path $ROOT "docker\wait_for_db.py") $waitDb
        Write-Host "  Copied wait_for_db.py -> $svc/" -ForegroundColor Gray
    }

    # 2. Rewrite Dockerfile with relative paths
    $content = @"
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wait_for_db.py .
COPY ${pkg}/ .
CMD ["sh", "-c", "python wait_for_db.py && python manage.py migrate --noinput && gunicorn ${pkg}.wsgi:application --bind 0.0.0.0:8888 --workers 2 --timeout 120"]
"@

    Set-Content -Path $dockerfile -Value $content -NoNewline
    Write-Host "  [OK] $svc/Dockerfile fixed" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Done! All Dockerfiles now use relative paths ===" -ForegroundColor Green
Write-Host ""
Write-Host "Railway settings for each service:" -ForegroundColor Cyan
Write-Host "  Root Directory: <service-name>  (e.g. product-service)" -ForegroundColor Yellow
Write-Host "  Build:          Dockerfile" -ForegroundColor Yellow
Write-Host "  Dockerfile:     Dockerfile" -ForegroundColor Yellow
