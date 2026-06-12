# create-railway-databases.ps1 - Hướng dẫn tạo 12 databases trong Railway PostgreSQL

Write-Host "=== Tạo databases trong Railway PostgreSQL ===" -ForegroundColor Cyan
Write-Host ""

$databases = @(
    "customer_db",
    "product_db",
    "cart_db",
    "staff_db",
    "manager_db",
    "catalog_db",
    "order_db",
    "ship_db",
    "pay_db",
    "comment_rate_db",
    "recommender_db",
    "gateway_db"
)

Write-Host "Bước 1: Kết nối đến Railway PostgreSQL" -ForegroundColor Yellow
Write-Host "  Chạy lệnh:" -ForegroundColor Gray
Write-Host "    railway connect postgres" -ForegroundColor Cyan
Write-Host ""

Write-Host "Bước 2: Trong psql shell, chạy các lệnh sau:" -ForegroundColor Yellow
Write-Host ""
foreach ($db in $databases) {
    Write-Host "  CREATE DATABASE $db;" -ForegroundColor Cyan
}
Write-Host ""

Write-Host "Bước 3: Thoát psql" -ForegroundColor Yellow
Write-Host "  Gõ: \q" -ForegroundColor Gray
Write-Host ""

Write-Host "Hoặc copy toàn bộ SQL này và paste vào psql:" -ForegroundColor Yellow
Write-Host ""
$sqlScript = ($databases | ForEach-Object { "CREATE DATABASE $_;" }) -join "`n"
Write-Host $sqlScript -ForegroundColor White
Write-Host ""

Write-Host "=== Sau khi tạo xong databases ===" -ForegroundColor Green
Write-Host "Chạy script tiếp theo để set environment variables:" -ForegroundColor Gray
Write-Host "  .\scripts\railway-deploy.ps1" -ForegroundColor Cyan
