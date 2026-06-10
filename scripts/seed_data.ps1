# seed_data.ps1
# Script to seed initial data for services via Docker Compose

$ErrorActionPreference = "Stop"

Write-Host "=== Seeding data ===" -ForegroundColor Cyan

# Note: You'll need to create fixtures or management commands for seeding
# Example using fixtures (if you have them):

# Write-Host "--- Seeding catalog data ---" -ForegroundColor Yellow
# docker compose exec catalog-service python manage.py loaddata initial_categories.json

# Write-Host "--- Seeding book data ---" -ForegroundColor Yellow
# docker compose exec book-service python manage.py loaddata initial_books.json

# Example using custom management commands (if you create them):
# docker compose exec book-service python manage.py seed_books
# docker compose exec customer-service python manage.py seed_customers

Write-Host "=== Seed data script ready ===" -ForegroundColor Green
Write-Host "NOTE: Add your specific seed commands to this script" -ForegroundColor Yellow
