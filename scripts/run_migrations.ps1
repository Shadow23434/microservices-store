# run_migrations.ps1
# Script to run Django migrations for all services via Docker Compose

$ErrorActionPreference = "Stop"

$services = @(
    "customer-service",
    "product-service",
    "cart-service",
    "staff-service",
    "manager-service",
    "catalog-service",
    "order-service",
    "ship-service",
    "pay-service",
    "comment-rate-service",
    "recommender-ai-service",
    "api-gateway"
)

Write-Host "=== Running migrations for all services ===" -ForegroundColor Cyan

foreach ($svc in $services) {
    Write-Host "--- Migrating $svc ---" -ForegroundColor Yellow
    docker compose exec $svc python manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Migration failed for $svc"
        exit 1
    }
}

Write-Host "=== All migrations completed successfully ===" -ForegroundColor Green
